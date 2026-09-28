# Architecture · H · Diverge, Then Converge

> 🚫🤖 **No-AI** · ⏱️ ~30 min

Model two replicas that take writes independently during a partition, then merge when the network heals.

| Function | Does |
|---|---|
| `apply(state, key, value, ts)` | Write only if `ts` is newer (last-write-wins) |
| `merge_lww(a, b)` | Merge value-stores by newest timestamp |
| `merge_counter(a, b)` | Merge counters by **summing** increments |

The tests show the key lesson: last-write-wins converges both replicas but can **drop** a concurrent edit, while an additive counter merge converges **without losing** any increments — which is why like counts use summing, not LWW.

```bash
cd exercises
uv run pytest architecture/h-distributed-systems/01-eventual-consistency
```
