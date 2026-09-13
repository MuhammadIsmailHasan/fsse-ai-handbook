# M2 · W6 · 07 — A Real CI Pipeline with GitHub Actions

> 🤖✅ **AI-allowed** (explain every line) · ⏱️ ~90 min · no database needed

The files live in `workflows/` here so they don't run on the handbook repo. In a real project they go to `.github/workflows/ci.yml` and `.github/dependabot.yml`.

## Part 1 — `junit_summary.py`
`sample-report.xml` is a real `pytest --junitxml` report.
- `parse_report(xml_text) -> Report` — root may be `<testsuites>` or a single `<testsuite>`; sum `tests`, `failures`, `errors`, `skipped`, `time` across suites. `failed_tests` lists every `<testcase>` with a `<failure>` or `<error>` as `FailedTest("<classname>::<name>", <first line of the message attribute>)`, in document order.
- `Report.passed` → total − failures − errors − skipped
- `markdown_summary(report)` → exactly the format in the tests (`## ✅ Tests passed` / `## ❌ Tests failed`, a table, duration with 2 decimals + `s`, and a `### Failures` list only when there are failures). Ends with a newline.
- `annotations(report)` → `::error title=<test id>::<message>` per failed test, using GitHub's escaping: in the **message** `%`→`%25`, `\r`→`%0D`, `\n`→`%0A`; in the **title** also `:`→`%3A` and `,`→`%2C`.
- `main(argv)` → `python junit_summary.py report.xml` prints the summary to **stdout** and annotations to **stderr**, returns 0; wrong arguments → usage message on stderr, return 2.

## Part 2 — `workflows/ci.yml`
| Area | Requirement |
|---|---|
| Triggers | `push` to `main`, `pull_request`, (optional `workflow_dispatch`). Never `pull_request_target` |
| Security | top-level `permissions: contents: read`; every `uses:` pinned to a **full 40-char commit SHA** followed by a `# vX.Y.Z` comment; no app secrets in `env` unless they come from `${{ secrets.* }}` |
| Efficiency | `concurrency` group containing `github.ref`, `cancel-in-progress: true`; each job has `timeout-minutes` ≤ 30 and an `ubuntu-*` runner |
| `lint` job | checkout, setup-uv, `uv sync --locked`, `ruff check`, `ruff format --check`, `mypy` |
| `test` job | service `postgres:17-alpine` with `--health-cmd pg_isready…` options and port `5432:5432`; matrix `python-version: ["3.13", "3.14"]` (strings!) with `fail-fast: false`, passed to setup-uv's `python-version`; `DATABASE_URL` pointing at `localhost:5432`; `uv sync --locked`; `pytest --junitxml=report.xml`; a summary step with `if: always()` running `junit_summary.py report.xml >> "$GITHUB_STEP_SUMMARY"` |
| `build` job | `needs: [lint, test]`; only `if: github.event_name == 'push' && github.ref == 'refs/heads/main'`; setup-buildx + build-push-action with `push: false` and a tag containing `${{ github.sha }}` |

Find the current release SHAs on each action's GitHub Releases page (or `git ls-remote https://github.com/actions/checkout refs/tags/v7.0.1`).

## Part 3 — `workflows/dependabot.yml`
`version: 2` with weekly (or daily/monthly) updates for `github-actions` and `uv`.

```bash
cd exercises
uv run pytest m2/w6/07-github-actions-ci
```
