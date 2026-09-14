"""Image tags and OCI labels. See README.md."""

import re
from datetime import UTC, datetime

SEMVER = re.compile(r"^v(\d+)\.(\d+)\.(\d+)(-[0-9A-Za-z.-]+)?$")


def _sanitize(branch: str) -> str:
    cleaned = re.sub(r"[^a-z0-9._-]", "-", branch.lower()).strip("-.")
    return cleaned[:128]


def image_tags(image: str, *, ref: str, sha: str, default_branch: str = "main") -> list[str]:
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("sha must be a full 40-character commit hash")
    tags = {f"sha-{sha[:7]}"}  # every image is traceable to a commit

    if ref.startswith("refs/heads/"):
        branch = ref.removeprefix("refs/heads/")
        tags.add(_sanitize(branch))
        if branch == default_branch:
            tags.add("edge")
    elif ref.startswith("refs/tags/"):
        match = SEMVER.match(ref.removeprefix("refs/tags/"))
        if match:
            major, minor, patch, prerelease = match.groups()
            if prerelease:
                tags.add(f"{major}.{minor}.{patch}{prerelease}")
            else:
                tags |= {f"{major}.{minor}.{patch}", f"{major}.{minor}", major, "latest"}
    elif match := re.fullmatch(r"refs/pull/(\d+)/(?:merge|head)", ref):
        tags.add(f"pr-{match.group(1)}")

    return sorted(f"{image}:{tag}" for tag in tags)


def oci_labels(*, title: str, source: str, version: str, revision: str, created: datetime) -> dict[str, str]:
    return {
        "org.opencontainers.image.title": title,
        "org.opencontainers.image.source": source,
        "org.opencontainers.image.version": version,
        "org.opencontainers.image.revision": revision,
        "org.opencontainers.image.created": created.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
