# AI-owned project documentation

Use this folder for concise, reviewable notes maintained by coding agents: verified setup, architecture, validation commands, and bounded cleanup plans.

The project README and any document marked `human-owned` remain authoritative. Do not overwrite human-owned material or make unsupported claims.

Never store credentials, private data, generated output, logs, datasets, or build artifacts here. Preserve unrelated local work and keep each change focused.

## Verified finite-width check

Run `python3 experiments/bitwise_successor_check.py` from the repository root;
use `--max-horizon 13` to reproduce the latest bounded check.
It exhaustively checks tuple/integer round-trips and both boundary transitions for
finite widths `h=0..13` in the latest record, with bit 0 representing the leftmost,
boundary-adjacent cell. This is an implementation check only; it does not prove
the successor identity at widths above `h=13`, infinite Rule 30 behavior, or
any center-column periodicity claim.

## Repository-local package facade

The bounded transition and predictive-partition helpers are also available from
the documented `rule30` facade:

```python
from rule30 import predictive_partition, response_signature
```

See [`agent-wave-2026-08-25-package-facade.md`](agent-wave-2026-08-25-package-facade.md)
for the compatibility checks and explicit finite-horizon limits. The facade
does not include the exploratory scripts or generated results. The
`PredictivePartition.right_truncation_map` method exposes the adjacent-horizon
projection described in the [cross-horizon report](agent-wave-2026-08-25-cross-horizon-map.md).
`class_members` and `right_truncation_fibers` provide immutable class members
and source-class fibers for the same finite partitions, with class-ID and
adjacent-horizon validation. `nested_transition_map` provides the separately
checked boundary-driven map from `S_h` to `S_{h-1}` after one update and right
truncation; it does not assert same-horizon determinism or an infinite
quotient. The partition builder uses a finite recursive lower-horizon key while
still enumerating every bounded state; it remains an exponential small-check
tool, not an infinite-horizon construction.
