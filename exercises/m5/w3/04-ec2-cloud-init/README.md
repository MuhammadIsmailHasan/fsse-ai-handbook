# M5 · W3 · 04 — Bootstrap an EC2 instance with cloud-init

> 🚫🤖 **No-AI** · ⏱️ ~90 min · no AWS account needed

A server you configure by hand can't be rebuilt. **User data** (processed by cloud-init on first boot) makes an EC2 instance reproducible. Write `user_data.py` that renders cloud-config for an **Ubuntu 24.04** instance that will run RevoShop with Docker Compose.

## `render_user_data(*, deploy_user, ssh_keys=(), swap_gb=0, app_dir="/opt/revoshop", timezone="Asia/Jakarta", app_env=None) -> str`

Returns text that starts with the line `#cloud-config`, followed by YAML with:

| Key | Content |
|---|---|
| `timezone` | the timezone |
| `package_update` / `package_upgrade` | `true` / `true` |
| `packages` | exactly `docker.io`, `docker-compose-v2`, `unattended-upgrades` |
| `users` | `["default", {name: deploy_user, groups: "docker", shell: "/bin/bash", lock_passwd: true, ssh_authorized_keys: [...]}]` — **no** `sudo` for the deploy user; omit `ssh_authorized_keys` when there are no keys |
| `write_files` | `/etc/ssh/sshd_config.d/99-hardening.conf` (`PasswordAuthentication no`, `PermitRootLogin no`, `KbdInteractiveAuthentication no`), `/etc/docker/daemon.json` (JSON: `json-file` log driver with `max-size` `10m` and `max-file` `"3"`), and `{app_dir}/app.env` with `app_env` as `KEY=value` lines (sorted, mode `"0640"`, owner `"{deploy_user}:{deploy_user}"`) — only if `app_env` is given |
| `runcmd` | in order: `["systemctl", "enable", "--now", "docker"]`, `["install", "-d", "-o", deploy_user, "-g", deploy_user, "-m", "0750", app_dir]`, then — only when `swap_gb > 0` — `["fallocate", "-l", "{swap_gb}G", "/swapfile"]`, `["chmod", "600", "/swapfile"]`, `["mkswap", "/swapfile"]`, `["swapon", "/swapfile"]`, and finally `["systemctl", "restart", "ssh"]` |

Validation (`ValueError`):
- `deploy_user` must match `^[a-z_][a-z0-9_-]{0,31}$` and not be `root`
- each SSH key must start with `ssh-ed25519 `, `ecdsa-sha2-nistp256 ` or `ssh-rsa `
- `swap_gb` between 0 and 8
- **no secrets in user data** (anyone with `ec2:DescribeInstanceAttribute` or access to the instance metadata can read it): any `app_env` key containing `SECRET`, `PASSWORD`, `TOKEN`, `KEY` (but not `_PUBLIC_KEY`) is rejected — secrets come from SSM Parameter Store at runtime (Week 4)
- the rendered result must be ≤ **16 KB** (EC2's user data limit)

```bash
cd exercises
uv run pytest m5/w3/04-ec2-cloud-init
```
