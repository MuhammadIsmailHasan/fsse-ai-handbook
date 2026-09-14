"""S3 uploads and RDS credentials. See README.md."""

import json
import uuid
from urllib.parse import quote

CONTENT_TYPES = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}


def create_private_bucket(s3, name: str, region: str) -> None:
    kwargs = {"Bucket": name}
    if region != "us-east-1":
        kwargs["CreateBucketConfiguration"] = {"LocationConstraint": region}
    s3.create_bucket(**kwargs)
    s3.put_public_access_block(
        Bucket=name,
        PublicAccessBlockConfiguration={"BlockPublicAcls": True, "IgnorePublicAcls": True, "BlockPublicPolicy": True, "RestrictPublicBuckets": True},
    )
    s3.put_bucket_encryption(
        Bucket=name,
        ServerSideEncryptionConfiguration={"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]},
    )
    s3.put_bucket_versioning(Bucket=name, VersioningConfiguration={"Status": "Enabled"})
    s3.put_bucket_lifecycle_configuration(
        Bucket=name,
        LifecycleConfiguration={
            "Rules": [
                {
                    "ID": "cleanup",
                    "Filter": {"Prefix": ""},
                    "Status": "Enabled",
                    "NoncurrentVersionExpiration": {"NoncurrentDays": 30},
                    "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7},
                }
            ]
        },
    )
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "DenyInsecureTransport",
                "Effect": "Deny",
                "Principal": "*",
                "Action": "s3:*",
                "Resource": [f"arn:aws:s3:::{name}", f"arn:aws:s3:::{name}/*"],
                "Condition": {"Bool": {"aws:SecureTransport": "false"}},
            }
        ],
    }
    s3.put_bucket_policy(Bucket=name, Policy=json.dumps(policy))


def _extension(filename: str) -> str:
    _, dot, ext = filename.rpartition(".")
    ext = ext.lower()
    if not dot or ext not in CONTENT_TYPES:
        raise ValueError("only jpg, jpeg, png and webp images are allowed")
    return ext


def product_image_key(product_id: int, filename: str, *, uuid_factory=uuid.uuid4) -> str:
    if not isinstance(product_id, int) or isinstance(product_id, bool) or product_id <= 0:
        raise ValueError("product_id must be a positive integer")
    # Never trust the user's filename in the key: no path traversal, no collisions, no PII.
    return f"products/{product_id}/{uuid_factory().hex}.{_extension(filename)}"


def presigned_upload(s3, bucket: str, product_id: int, filename: str, content_type: str, *, max_bytes: int = 5_000_000, expires: int = 300) -> dict:
    if CONTENT_TYPES[_extension(filename)] != content_type:
        raise ValueError("content type doesn't match the file extension")
    key = product_image_key(product_id, filename)
    post = s3.generate_presigned_post(
        Bucket=bucket,
        Key=key,
        Fields={"Content-Type": content_type},
        Conditions=[{"Content-Type": content_type}, ["content-length-range", 1, max_bytes]],
        ExpiresIn=expires,
    )
    return {"url": post["url"], "fields": post["fields"], "key": key}


def database_url_from_secret(secrets, secret_id: str, *, host: str, port: int = 5432, dbname: str, sslrootcert: str = "/etc/ssl/certs/rds-global-bundle.pem") -> str:
    data = json.loads(secrets.get_secret_value(SecretId=secret_id)["SecretString"])
    try:
        user, password = data["username"], data["password"]
    except KeyError as missing:
        raise ValueError(f"secret is missing {missing}") from None
    return f"postgresql://{quote(user, safe='')}:{quote(password, safe='')}@{host}:{port}/{dbname}?sslmode=verify-full&sslrootcert={sslrootcert}"
