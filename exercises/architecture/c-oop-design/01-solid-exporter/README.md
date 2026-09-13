# Architecture · C · SOLID Application Exporter

> 🚫🤖 **No-AI** · ⏱️ ~60 min

`legacy_export.py` shows the "before": one `export()` function with `if format == ...` branches that also writes files. Every new format or destination means editing it. Build the SOLID version in **`solid_export.py`**:

| Piece | Contract |
|---|---|
| `Exporter` (Protocol) | `extension: str` and `render(applications) -> str` |
| `CsvExporter` | `extension = "csv"`; header `company,role,status,applied_on`, one row per application, written with the `csv` module (so commas get quoted), `\n` line endings |
| `JsonExporter` | `extension = "json"`; `json.dumps(list_of_dicts, indent=2)` with keys in the order above and dates as `"YYYY-MM-DD"` |
| `MarkdownExporter` | `extension = "md"`; `| Company | Role | Status | Applied on |`, then `|---|---|---|---|`, then one row per application; ends with `\n` |
| `Destination` (Protocol) | `write(filename: str, content: str) -> None` |
| `FolderDestination(folder)` | writes `folder/filename` (UTF-8) |
| `MemoryDestination()` | stores `files: dict[str, str]` — useful in tests |
| `export_applications(applications, exporter, destination, basename="applications") -> str` | renders, writes `f"{basename}.{exporter.extension}"`, returns the filename |

Applications are dicts: `{"company", "role", "status", "applied_on": date | None}` (`None` renders as an empty string / `null` in JSON).

Rules checked by the tests:
- `export_applications` works with **any** object that has `extension` and `render` (open/closed — a test adds a new exporter without touching your code)
- `export_applications` doesn't mention any concrete exporter or destination class (dependency inversion)
- empty lists work for every exporter (Liskov: every implementation honors the same contract)

```bash
cd exercises
uv run pytest architecture/c-oop-design/01-solid-exporter
```
