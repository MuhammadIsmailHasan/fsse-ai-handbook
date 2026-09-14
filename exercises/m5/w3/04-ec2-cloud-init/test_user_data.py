"""Checks for user_data.py. Don't edit this file."""

import json

import pytest
import yaml

from user_data import render_user_data

KEY = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFakeKeyForTests sari@laptop"


def parse(text):
    first, _, rest = text.partition("\n")
    assert first == "#cloud-config"
    return yaml.safe_load(rest)


def files_by_path(config):
    return {f["path"]: f for f in config["write_files"]}


def test_full_config():
    config = parse(render_user_data(deploy_user="deploy", ssh_keys=[KEY], swap_gb=2, app_env={"APP_ENV": "production", "WEB_CONCURRENCY": "2"}))
    assert config["timezone"] == "Asia/Jakarta"
    assert config["package_update"] is True and config["package_upgrade"] is True
    assert config["packages"] == ["docker.io", "docker-compose-v2", "unattended-upgrades"]
    default, user = config["users"]
    assert default == "default"
    assert user["name"] == "deploy" and user["groups"] == "docker" and user["shell"] == "/bin/bash" and user["lock_passwd"] is True
    assert user["ssh_authorized_keys"] == [KEY]
    assert "sudo" not in user

    files = files_by_path(config)
    sshd = files["/etc/ssh/sshd_config.d/99-hardening.conf"]["content"]
    for line in ("PasswordAuthentication no", "PermitRootLogin no", "KbdInteractiveAuthentication no"):
        assert line in sshd.splitlines()
    daemon = json.loads(files["/etc/docker/daemon.json"]["content"])
    assert daemon == {"log-driver": "json-file", "log-opts": {"max-size": "10m", "max-file": "3"}}
    env_file = files["/opt/revoshop/app.env"]
    assert env_file["content"] == "APP_ENV=production\nWEB_CONCURRENCY=2\n"
    assert env_file["permissions"] == "0640" and env_file["owner"] == "deploy:deploy"

    assert config["runcmd"] == [
        ["systemctl", "enable", "--now", "docker"],
        ["install", "-d", "-o", "deploy", "-g", "deploy", "-m", "0750", "/opt/revoshop"],
        ["fallocate", "-l", "2G", "/swapfile"],
        ["chmod", "600", "/swapfile"],
        ["mkswap", "/swapfile"],
        ["swapon", "/swapfile"],
        ["systemctl", "restart", "ssh"],
    ]


def test_minimal_config():
    config = parse(render_user_data(deploy_user="app_1", app_dir="/srv/shop", timezone="UTC"))
    assert config["timezone"] == "UTC"
    assert "ssh_authorized_keys" not in config["users"][1]
    assert set(files_by_path(config)) == {"/etc/ssh/sshd_config.d/99-hardening.conf", "/etc/docker/daemon.json"}
    assert config["runcmd"] == [
        ["systemctl", "enable", "--now", "docker"],
        ["install", "-d", "-o", "app_1", "-g", "app_1", "-m", "0750", "/srv/shop"],
        ["systemctl", "restart", "ssh"],
    ]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"deploy_user": "root"},
        {"deploy_user": "Deploy"},
        {"deploy_user": "9lives"},
        {"deploy_user": "deploy", "ssh_keys": ["AAAAC3Nza... no type"]},
        {"deploy_user": "deploy", "swap_gb": 9},
        {"deploy_user": "deploy", "swap_gb": -1},
        {"deploy_user": "deploy", "app_env": {"JWT_SECRET_KEY": "x"}},
        {"deploy_user": "deploy", "app_env": {"POSTGRES_PASSWORD": "x"}},
        {"deploy_user": "deploy", "app_env": {"MIDTRANS_SERVER_KEY": "x"}},
        {"deploy_user": "deploy", "app_env": {"github_token": "x"}},
        {"deploy_user": "deploy", "ssh_keys": [KEY] * 400},
    ],
)
def test_rejects(kwargs):
    with pytest.raises(ValueError):
        render_user_data(**kwargs)


def test_public_keys_are_not_secrets():
    config = parse(render_user_data(deploy_user="deploy", app_env={"VAPID_PUBLIC_KEY": "BEl62iUY", "APP_URL": "https://api.example.com"}))
    assert "VAPID_PUBLIC_KEY=BEl62iUY" in files_by_path(config)["/opt/revoshop/app.env"]["content"]
