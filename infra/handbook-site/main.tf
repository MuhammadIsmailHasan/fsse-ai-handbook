# ─────────────────────────────────────────────────────────────────────────────
# Handbook hosting: a private S3 bucket holding `dist/`, served by CloudFront.
#
# Why this shape (the same reasoning as content/modules/m5/w4/01):
#   - The handbook is a static SPA: content is bundled at build time by Vite's
#     import.meta.glob, so there is nothing to run on a server.
#   - S3 stores the files; CloudFront terminates HTTPS, caches at edge locations
#     and rewrites unknown paths to index.html so react-router's
#     createBrowserRouter URLs (/modules/m7/w4/03-...) work on refresh.
#   - The bucket stays private. Only CloudFront may read it (OAC), so there is
#     no public bucket to misconfigure.
# ─────────────────────────────────────────────────────────────────────────────

locals {
  basic_auth_enabled = var.basic_auth_password != ""
}

# ── Storage ─────────────────────────────────────────────────────────────────

resource "aws_s3_bucket" "site" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_public_access_block" "site" {
  bucket                  = aws_s3_bucket.site.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "site" {
  bucket = aws_s3_bucket.site.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# The deploy script syncs with --delete, so stale hashed bundles are removed on
# each deploy. This rule only cleans up uploads that died halfway.
resource "aws_s3_bucket_lifecycle_configuration" "site" {
  bucket = aws_s3_bucket.site.id

  rule {
    id     = "abort-failed-uploads"
    status = "Enabled"

    filter {}

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# Only this distribution may GetObject, and nothing else may read the bucket.
data "aws_iam_policy_document" "site" {
  statement {
    sid       = "AllowCloudFrontRead"
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.site.arn}/*"]

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.site.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "site" {
  bucket = aws_s3_bucket.site.id
  policy = data.aws_iam_policy_document.site.json
}

# ── Delivery ────────────────────────────────────────────────────────────────

resource "aws_cloudfront_origin_access_control" "site" {
  name                              = "${var.bucket_name}-oac"
  description                       = "CloudFront -> private S3 for the FSSE handbook"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# A tiny JS function that runs at the edge on every request and asks the browser
# for a username and password. Cheap (no Lambda cold start) but the password is
# visible to anyone who can read this AWS account, so it is a gate, not a vault.
resource "aws_cloudfront_function" "basic_auth" {
  count   = local.basic_auth_enabled ? 1 : 0
  name    = "${replace(var.bucket_name, ".", "-")}-basic-auth"
  runtime = "cloudfront-js-2.0"
  comment = "Browser password prompt for the handbook"
  publish = true

  code = <<-JS
    function handler(event) {
      var expected = 'Basic ${base64encode("${var.basic_auth_user}:${var.basic_auth_password}")}'
      var headers = event.request.headers

      if (headers.authorization && headers.authorization.value === expected) {
        return event.request
      }

      return {
        statusCode: 401,
        statusDescription: 'Unauthorized',
        headers: {
          'www-authenticate': { value: 'Basic realm="FSSE handbook", charset="UTF-8"' },
          'cache-control': { value: 'no-store' },
        },
      }
    }
  JS
}

resource "aws_cloudfront_distribution" "site" {
  enabled             = true
  comment             = "FSSE handbook"
  default_root_object = "index.html"
  price_class         = var.price_class
  # IPv6 costs nothing and some mobile networks prefer it.
  is_ipv6_enabled = true

  origin {
    domain_name              = aws_s3_bucket.site.bucket_regional_domain_name
    origin_id                = "s3-${aws_s3_bucket.site.id}"
    origin_access_control_id = aws_cloudfront_origin_access_control.site.id
  }

  default_cache_behavior {
    target_origin_id       = "s3-${aws_s3_bucket.site.id}"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    compress               = true

    # AWS-managed policies, referenced by their fixed IDs:
    #   CachingOptimized      — respects the Cache-Control we set at upload time
    #   SecurityHeadersPolicy — adds HSTS, X-Content-Type-Options, etc.
    cache_policy_id            = "658327ea-f89d-4fab-a63d-7e88639e58f6"
    response_headers_policy_id = "67f7725c-6f97-4210-82d7-5512b31e9d03"

    dynamic "function_association" {
      for_each = local.basic_auth_enabled ? [1] : []

      content {
        event_type   = "viewer-request"
        function_arn = aws_cloudfront_function.basic_auth[0].arn
      }
    }
  }

  # The SPA fallback. S3 answers 403 for a key that does not exist (because the
  # bucket is private), so both codes must become index.html with a 200, or a
  # refresh on /modules/m7/w4/03-retrieval would show an error page.
  custom_error_response {
    error_code            = 403
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 10
  }

  custom_error_response {
    error_code            = 404
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 10
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    # The free *.cloudfront.net certificate. A custom domain needs an ACM
    # certificate in us-east-1 plus `aliases` here — see docs/DEPLOY.md.
    cloudfront_default_certificate = true
  }
}
