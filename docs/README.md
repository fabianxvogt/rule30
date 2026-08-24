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
