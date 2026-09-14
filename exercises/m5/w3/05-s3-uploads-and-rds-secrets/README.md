# M5 · W3 · 05 — Private S3 uploads and RDS credentials (boto3 + moto)

> 🚫🤖 **No-AI** · ⏱️ ~2 h · AWS is mocked with **moto**, no account needed

RevoShop stores product images as URL strings. In production, sellers should upload images **directly to a private S3 bucket** with a short-lived **presigned POST** (your API never streams the file), and the API should get its database credentials from **Secrets Manager**. Write `storage.py`.

## 1. `create_private_bucket(s3, name, region) -> None`
- create the bucket (`CreateBucketConfiguration={"LocationConstraint": region}` unless `region == "us-east-1"`)
- **block all public access** (all four settings `True`)
- default encryption `AES256` (SSE-S3)
- versioning `Enabled`
- lifecycle rule id `"cleanup"` for all objects (`Filter: {"Prefix": ""}`): expire **noncurrent** versions after **30** days and abort incomplete multipart uploads after **7** days
- bucket policy with a statement `Sid: "DenyInsecureTransport"` denying `s3:*` on the bucket and its objects when `aws:SecureTransport` is `"false"`

## 2. `product_image_key(product_id, filename, *, uuid_factory=uuid.uuid4) -> str`
`products/{product_id}/{uuid hex}.{ext}` — `ext` from the filename, lower-cased, must be `jpg`, `jpeg`, `png` or `webp` (else `ValueError`); `product_id` must be a positive int. The user's filename never becomes part of the key.

## 3. `presigned_upload(s3, bucket, product_id, filename, content_type, *, max_bytes=5_000_000, expires=300) -> dict`
- `content_type` must match the extension (`jpg`/`jpeg` → `image/jpeg`, `png` → `image/png`, `webp` → `image/webp`), else `ValueError`
- `generate_presigned_post` with `Fields={"Content-Type": content_type}` and `Conditions=[{"Content-Type": content_type}, ["content-length-range", 1, max_bytes]]`, `ExpiresIn=expires`
- return `{"url": …, "fields": …, "key": …}`

## 4. `database_url_from_secret(secrets, secret_id, *, host, port=5432, dbname, sslrootcert="/etc/ssl/certs/rds-global-bundle.pem") -> str`
RDS can manage the master password in Secrets Manager; that secret's JSON contains `username` and `password`. Build
`postgresql://<user>:<password>@<host>:<port>/<dbname>?sslmode=verify-full&sslrootcert=<path>` — username and password **URL-encoded** (passwords contain `@`, `/`, `:`…). Missing keys → `ValueError`.

```bash
cd exercises
uv run pytest m5/w3/05-s3-uploads-and-rds-secrets
```
