"""Image tags and OCI labels. See README.md."""

from datetime import datetime


def image_tags(image: str, *, ref: str, sha: str, default_branch: str = "main") -> list[str]:
    raise NotImplementedError


def oci_labels(*, title: str, source: str, version: str, revision: str, created: datetime) -> dict[str, str]:
    raise NotImplementedError
