"""S3 uploads and RDS credentials. See README.md."""

import uuid


def create_private_bucket(s3, name: str, region: str) -> None:
    raise NotImplementedError


def product_image_key(product_id: int, filename: str, *, uuid_factory=uuid.uuid4) -> str:
    raise NotImplementedError


def presigned_upload(s3, bucket: str, product_id: int, filename: str, content_type: str, *, max_bytes: int = 5_000_000, expires: int = 300) -> dict:
    raise NotImplementedError


def database_url_from_secret(secrets, secret_id: str, *, host: str, port: int = 5432, dbname: str, sslrootcert: str = "/etc/ssl/certs/rds-global-bundle.pem") -> str:
    raise NotImplementedError
