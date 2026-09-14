"""cloud-init user data for a RevoShop EC2 host. See README.md."""


def render_user_data(*, deploy_user: str, ssh_keys=(), swap_gb: int = 0, app_dir: str = "/opt/revoshop", timezone: str = "Asia/Jakarta", app_env: dict | None = None) -> str:
    raise NotImplementedError
