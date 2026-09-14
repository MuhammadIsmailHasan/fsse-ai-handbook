"""Checks for config_loader.py (SSM and Secrets Manager mocked with moto). Don't edit this file."""

import json

import boto3
import pytest
from moto import mock_aws

from config_loader import CachedConfig, load_parameters, resolve_references

REGION = "ap-southeast-1"


@pytest.fixture(autouse=True)
def credentials(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")


@mock_aws
def test_load_parameters_recursive_decrypted_paginated():
    ssm = boto3.client("ssm", region_name=REGION)
    ssm.put_parameter(Name="/revoshop/production/JWT_SECRET_KEY", Value="s3cr3t", Type="SecureString")
    ssm.put_parameter(Name="/revoshop/production/midtrans/server_key", Value="Mid-server-abc", Type="SecureString")
    ssm.put_parameter(Name="/revoshop/production/APP_ENV", Value="production", Type="String")
    for i in range(25):
        ssm.put_parameter(Name=f"/revoshop/production/flags/feature_{i:02d}", Value="on", Type="String")
    ssm.put_parameter(Name="/revoshop/staging/JWT_SECRET_KEY", Value="staging", Type="SecureString")
    config = load_parameters(ssm, "/revoshop/production/")
    assert config["JWT_SECRET_KEY"] == "s3cr3t"
    assert config["MIDTRANS_SERVER_KEY"] == "Mid-server-abc"
    assert config["APP_ENV"] == "production"
    assert len([k for k in config if k.startswith("FLAGS_FEATURE_")]) == 25
    assert len(config) == 28
    for bad in ["/revoshop/production", "revoshop/production/"]:
        with pytest.raises(ValueError):
            load_parameters(ssm, bad)


@mock_aws
def test_load_parameters_rejects_bad_and_colliding_names():
    ssm = boto3.client("ssm", region_name=REGION)
    ssm.put_parameter(Name="/app/a/1-bad", Value="x", Type="String")
    with pytest.raises(ValueError):
        load_parameters(ssm, "/app/a/")
    ssm.put_parameter(Name="/app/b/db/url", Value="x", Type="String")
    ssm.put_parameter(Name="/app/b/DB_URL", Value="y", Type="String")
    with pytest.raises(ValueError):
        load_parameters(ssm, "/app/b/")


@mock_aws
def test_resolve_references_fetches_each_secret_once():
    sm = boto3.client("secretsmanager", region_name=REGION)
    arn = sm.create_secret(Name="rds!db-revoshop", SecretString=json.dumps({"username": "revoshop_admin", "password": "p@ss"}))["ARN"]
    calls = []
    real = sm.get_secret_value

    def spy(**kwargs):
        calls.append(kwargs["SecretId"])
        return real(**kwargs)

    sm.get_secret_value = spy
    config = {"DB_USER": f"secretsmanager:{arn}#username", "DB_PASSWORD": f"secretsmanager:{arn}#password", "APP_ENV": "production"}
    assert resolve_references(config, sm) == {"DB_USER": "revoshop_admin", "DB_PASSWORD": "p@ss", "APP_ENV": "production"}
    assert calls == [arn]
    with pytest.raises(KeyError):
        resolve_references({"X": f"secretsmanager:{arn}#host"}, sm)


def test_cached_config_ttl_stale_and_invalidate():
    now = [0.0]
    results = [{"v": 1}, {"v": 2}, RuntimeError("SSM throttled"), RuntimeError("still down"), {"v": 3}]
    loads = []

    def load():
        loads.append(now[0])
        result = results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    config = CachedConfig(load, ttl=60, max_stale=300, clock=lambda: now[0])
    assert config.get() == {"v": 1}
    now[0] = 59
    assert config.get() == {"v": 1}
    now[0] = 60
    assert config.get() == {"v": 2}
    now[0] = 200
    assert config.get() == {"v": 2}, "stale value served during a short outage"
    now[0] = 400
    with pytest.raises(RuntimeError):
        config.get()
    config.invalidate()
    assert config.get() == {"v": 3}
    assert loads == [0, 60, 200, 400, 400]


def test_cached_config_without_cache_raises():
    def failing():
        raise RuntimeError("no credentials")

    with pytest.raises(RuntimeError):
        CachedConfig(failing, ttl=60, max_stale=300, clock=lambda: 0).get()
