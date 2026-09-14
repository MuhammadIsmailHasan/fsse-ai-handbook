"""cloud-init user data for a RevoShop EC2 host. See README.md."""

import json
import re

import yaml

MAX_BYTES = 16 * 1024
KEY_PREFIXES = ("ssh-ed25519 ", "ecdsa-sha2-nistp256 ", "ssh-rsa ")
SECRET_WORDS = ("SECRET", "PASSWORD", "TOKEN", "KEY")


def _looks_secret(name: str) -> bool:
    upper = name.upper()
    return any(word in upper for word in SECRET_WORDS) and not upper.endswith("_PUBLIC_KEY")


def render_user_data(*, deploy_user, ssh_keys=(), swap_gb=0, app_dir="/opt/revoshop", timezone="Asia/Jakarta", app_env=None) -> str:
    if not re.fullmatch(r"[a-z_][a-z0-9_-]{0,31}", deploy_user) or deploy_user == "root":
        raise ValueError("invalid deploy user")
    for key in ssh_keys:
        if not key.startswith(KEY_PREFIXES):
            raise ValueError("unsupported SSH public key")
    if not 0 <= swap_gb <= 8:
        raise ValueError("swap_gb must be between 0 and 8")
    for name in app_env or {}:
        if _looks_secret(name):
            raise ValueError(f"{name} looks like a secret; load it from SSM Parameter Store instead")

    user: dict = {"name": deploy_user, "groups": "docker", "shell": "/bin/bash", "lock_passwd": True}
    if ssh_keys:
        user["ssh_authorized_keys"] = list(ssh_keys)

    files = [
        {
            "path": "/etc/ssh/sshd_config.d/99-hardening.conf",
            "permissions": "0644",
            "content": "PasswordAuthentication no\nPermitRootLogin no\nKbdInteractiveAuthentication no\n",
        },
        {
            "path": "/etc/docker/daemon.json",
            "permissions": "0644",
            # Without rotation, container logs grow until the disk is full.
            "content": json.dumps({"log-driver": "json-file", "log-opts": {"max-size": "10m", "max-file": "3"}}, indent=2) + "\n",
        },
    ]
    if app_env:
        files.append(
            {
                "path": f"{app_dir}/app.env",
                "permissions": "0640",
                "owner": f"{deploy_user}:{deploy_user}",
                "defer": True,  # write after users are created
                "content": "".join(f"{k}={v}\n" for k, v in sorted(app_env.items())),
            }
        )

    runcmd = [
        ["systemctl", "enable", "--now", "docker"],
        ["install", "-d", "-o", deploy_user, "-g", deploy_user, "-m", "0750", app_dir],
    ]
    if swap_gb:
        runcmd += [["fallocate", "-l", f"{swap_gb}G", "/swapfile"], ["chmod", "600", "/swapfile"], ["mkswap", "/swapfile"], ["swapon", "/swapfile"]]
    runcmd.append(["systemctl", "restart", "ssh"])

    config = {
        "timezone": timezone,
        "package_update": True,
        "package_upgrade": True,
        "packages": ["docker.io", "docker-compose-v2", "unattended-upgrades"],
        "users": ["default", user],
        "write_files": files,
        "runcmd": runcmd,
    }
    rendered = "#cloud-config\n" + yaml.safe_dump(config, sort_keys=False)
    if len(rendered.encode()) > MAX_BYTES:
        raise ValueError("user data exceeds 16 KB")
    return rendered
