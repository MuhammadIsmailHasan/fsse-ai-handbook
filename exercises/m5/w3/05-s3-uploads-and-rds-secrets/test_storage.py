"""Checks for storage.py with moto (no real AWS). Don't edit this file."""

import base64
import json
import uuid
from urllib.parse import unquote, urlsplit

import boto3
import pytest
from moto import mock_aws

from storage import create_private_bucket, database_url_from_secret, presigned_upload, product_image_key

REGION = "ap-southeast-3"


@pytest.fixture(autouse=True)
def fake_credentials(monkeypatch):
    for key, value in {"AWS_ACCESS_KEY_ID": "testing", "AWS_SECRET_ACCESS_KEY": "testing", "AWS_DEFAULT_REGION": REGION}.items():
        monkeypatch.setenv(key, value)


@mock_aws
def test_private_bucket_configuration():
    s3 = boto3.client("s3", region_name=REGION)
    create_private_bucket(s3, "revoshop-images-test", REGION)
    assert s3.get_bucket_location(Bucket="revoshop-images-test")["LocationConstraint"] == REGION
    block = s3.get_public_access_block(Bucket="revoshop-images-test")["PublicAccessBlockConfiguration"]
    assert block == {"BlockPublicAcls": True, "IgnorePublicAcls": True, "BlockPublicPolicy": True, "RestrictPublicBuckets": True}
    rules = s3.get_bucket_encryption(Bucket="revoshop-images-test")["ServerSideEncryptionConfiguration"]["Rules"]
    assert rules[0]["ApplyServerSideEncryptionByDefault"]["SSEAlgorithm"] == "AES256"
    assert s3.get_bucket_versioning(Bucket="revoshop-images-test")["Status"] == "Enabled"
    lifecycle = s3.get_bucket_lifecycle_configuration(Bucket="revoshop-images-test")["Rules"]
    assert len(lifecycle) == 1 and lifecycle[0]["ID"] == "cleanup" and lifecycle[0]["Status"] == "Enabled"
    assert lifecycle[0]["NoncurrentVersionExpiration"]["NoncurrentDays"] == 30
    assert lifecycle[0]["AbortIncompleteMultipartUpload"]["DaysAfterInitiation"] == 7
    policy = json.loads(s3.get_bucket_policy(Bucket="revoshop-images-test")["Policy"])
    deny = [s for s in policy["Statement"] if s.get("Sid") == "DenyInsecureTransport"]
    assert deny and deny[0]["Effect"] == "Deny" and deny[0]["Condition"] == {"Bool": {"aws:SecureTransport": "false"}}
    assert set(deny[0]["Resource"]) == {"arn:aws:s3:::revoshop-images-test", "arn:aws:s3:::revoshop-images-test/*"}


@mock_aws
def test_us_east_1_has_no_location_constraint():
    s3 = boto3.client("s3", region_name="us-east-1")
    create_private_bucket(s3, "revoshop-images-use1", "us-east-1")
    assert s3.get_bucket_versioning(Bucket="revoshop-images-use1")["Status"] == "Enabled"


def test_product_image_key():
    fixed = uuid.UUID("12345678123456781234567812345678")
    assert product_image_key(7, "My Photo.JPG", uuid_factory=lambda: fixed) == "products/7/12345678123456781234567812345678.jpg"
    assert product_image_key(7, "../../etc/passwd.png", uuid_factory=lambda: fixed) == "products/7/12345678123456781234567812345678.png"
    keys = {product_image_key(7, "a.webp") for _ in range(5)}
    assert len(keys) == 5
    for bad_id, bad_name in [(0, "a.png"), (-1, "a.png"), ("7", "a.png"), (True, "a.png"), (7, "a.gif"), (7, "noextension"), (7, "evil.png.exe")]:
        with pytest.raises(ValueError):
            product_image_key(bad_id, bad_name)


@mock_aws
def test_presigned_upload_policy():
    s3 = boto3.client("s3", region_name=REGION)
    create_private_bucket(s3, "revoshop-images-test", REGION)
    result = presigned_upload(s3, "revoshop-images-test", 42, "shirt.webp", "image/webp", max_bytes=2_000_000, expires=120)
    assert result["key"].startswith("products/42/") and result["key"].endswith(".webp")
    assert result["fields"]["key"] == result["key"]
    assert result["fields"]["Content-Type"] == "image/webp"
    assert "revoshop-images-test" in result["url"]
    policy = json.loads(base64.b64decode(result["fields"]["policy"]))
    conditions = policy["conditions"]
    assert {"Content-Type": "image/webp"} in conditions
    assert ["content-length-range", 1, 2_000_000] in conditions
    assert {"key": result["key"]} in conditions
    with pytest.raises(ValueError):
        presigned_upload(s3, "revoshop-images-test", 42, "shirt.webp", "image/png")
    with pytest.raises(ValueError):
        presigned_upload(s3, "revoshop-images-test", 42, "shirt.svg", "image/svg+xml")


@mock_aws
def test_database_url_from_secret():
    sm = boto3.client("secretsmanager", region_name=REGION)
    sm.create_secret(Name="rds!db-revoshop", SecretString=json.dumps({"username": "revoshop_admin", "password": "p@ss:w/rd?#1"}))
    url = database_url_from_secret(sm, "rds!db-revoshop", host="revoshop.abc123.ap-southeast-3.rds.amazonaws.com", dbname="revoshop")
    parts = urlsplit(url)
    assert parts.scheme == "postgresql"
    assert parts.hostname == "revoshop.abc123.ap-southeast-3.rds.amazonaws.com" and parts.port == 5432
    assert unquote(parts.username) == "revoshop_admin" and unquote(parts.password) == "p@ss:w/rd?#1"
    assert parts.path == "/revoshop"
    assert parts.query == "sslmode=verify-full&sslrootcert=/etc/ssl/certs/rds-global-bundle.pem"
    sm.create_secret(Name="broken", SecretString=json.dumps({"user": "x"}))
    with pytest.raises(ValueError):
        database_url_from_secret(sm, "broken", host="h", dbname="d")
