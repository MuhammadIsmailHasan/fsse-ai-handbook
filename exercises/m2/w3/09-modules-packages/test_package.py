"""Checks the careerpilot_core package. Don't edit this file."""

import ast
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
PACKAGE = HERE / "careerpilot_core"
MODULES = ["__init__", "models", "analysis", "formatting", "__main__"]


def test_package_files_exist():
    missing = [name for name in MODULES if not (PACKAGE / f"{name}.py").exists()]
    assert not missing, f"Create careerpilot_core/{missing[0]}.py"


def test_public_api_and_behavior():
    import careerpilot_core
    import monolith

    assert careerpilot_core.__version__ == "0.1.0"
    jobs_text = ["Backend Dev:python,sql", "AI Engineer:Python, LLM", "QA:"]
    jobs = [careerpilot_core.JobListing.parse(text) for text in jobs_text]
    reference = [monolith.JobListing.parse(text) for text in jobs_text]
    assert careerpilot_core.top_skills(jobs, 3) == monolith.top_skills(reference, 3)
    assert careerpilot_core.format_report(jobs, 2) == monolith.format_report(reference, 2)


def package_imports(module: str) -> set[str]:
    tree = ast.parse((PACKAGE / f"{module}.py").read_text())
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level > 0:  # relative: from .models import …
                found.add(node.module.split(".")[0] if node.module else "")
            elif node.module and node.module.startswith("careerpilot_core"):
                parts = node.module.split(".")
                found.add(parts[1] if len(parts) > 1 else "__init__")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("careerpilot_core."):
                    found.add(alias.name.split(".")[1])
    return found - {""}


@pytest.mark.parametrize(
    ("module", "allowed"),
    [("models", set()), ("analysis", {"models"}), ("formatting", {"models", "analysis"})],
)
def test_import_direction(module, allowed):
    test_package_files_exist()
    imports = package_imports(module)
    assert imports <= allowed, f"{module}.py may only import {allowed or 'nothing'} from the package, found {imports}"


def run_module(*args):
    return subprocess.run([sys.executable, "-m", "careerpilot_core", *args], capture_output=True, text=True, cwd=HERE)


def test_cli_version():
    result = run_module("--version")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "0.1.0"


def test_cli_report():
    result = run_module("report", "Backend Dev:python,sql", "AI Engineer:python,llm", "--top", "2")
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ["Top skills across 2 job(s):", "1. python (2)", "2. llm (1)"]
