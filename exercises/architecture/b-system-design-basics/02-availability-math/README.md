# Architecture · B · Availability Calculator

> 🚫🤖 **No-AI** · ⏱️ ~30 min

Availability values are fractions: `0.999` means 99.9%.

| Function | Example | Result |
|---|---|---|
| `downtime_minutes_per_year(availability)` | `0.999` | `525.6` (use 365 days) |
| `series(availabilities)` | `[0.999, 0.999]` | `0.998001` (`1.0` for none) |
| `parallel(availabilities)` | `[0.99, 0.99]` | `0.9999` (`0.0` for none) |
| `copies_needed(single, target)` | `0.99, 0.9999` | `2` — smallest n with `1 − (1 − single)ⁿ ≥ target` |

`copies_needed` raises `ValueError` if `single` is not between 0 and 1 (exclusive).

```bash
cd exercises
uv run pytest architecture/b-system-design-basics/02-availability-math
```
