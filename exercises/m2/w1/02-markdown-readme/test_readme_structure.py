"""Checks the structure of README.md in this folder. Don't edit this file."""

import re
from pathlib import Path

import pytest

README = Path(__file__).with_name("README.md")
REQUIRED_SECTIONS = ["features", "tech stack", "architecture", "getting started", "usage", "testing"]


@pytest.fixture(scope="module")
def text():
    assert README.exists(), "Create README.md in this folder"
    return README.read_text(encoding="utf-8")


def outside_code(text):
    return re.sub(r"```.*?```", "", text, flags=re.S)


def test_single_title_on_first_line(text):
    titles = re.findall(r"^# .+", outside_code(text), flags=re.M)
    assert len(titles) == 1, "Use exactly one level-1 heading"
    assert text.lstrip().startswith("# "), "The title should be the first line"
    assert text.splitlines()[0].strip() != "# TODO", "Give the project a real title"


def test_description_after_title(text):
    lines = text.strip().splitlines()[1:]
    paragraph = next((line for line in lines if line.strip() and not line.startswith(("#", "!", "[", "<"))), "")
    assert len(paragraph.split()) >= 10, "Add a one-sentence description (10+ words) right after the title"


def test_required_sections(text):
    headings = [re.sub(r"[^a-z ]", "", h.lower()).strip() for h in re.findall(r"^## (.+)", outside_code(text), flags=re.M)]
    missing = [section for section in REQUIRED_SECTIONS if not any(section in heading for heading in headings)]
    assert not missing, f"Missing ## sections: {missing}"


def test_bash_block_with_run_command(text):
    blocks = re.findall(r"```bash\n(.*?)```", text, flags=re.S)
    assert any("python cli.py" in block for block in blocks), "Add a ```bash block that shows `python cli.py ...`"


def test_has_table_and_mermaid(text):
    assert re.search(r"^\|.+\|\n\|[\s:|-]+\|", outside_code(text), flags=re.M), "Add at least one Markdown table"
    assert "```mermaid" in text, "Add a mermaid diagram"


def test_links_are_relative_or_https(text):
    for url in re.findall(r"\]\(([^)]+)\)", text):
        assert not url.startswith("http://"), f"Use https: {url}"
        assert "localhost" not in url and "127.0.0.1" not in url, f"No local URLs in a README: {url}"


def test_no_secrets(text):
    assert not re.search(r"(password|secret|api[_-]?key|token)\s*[:=]\s*\S+", text, flags=re.I), "Remove secrets"
