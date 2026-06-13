# Lumen

**Lumen** is a small, runnable MVP for receipt-bound authority verification, replayable evidence, and governed AI execution.

It is the practical core of the broader Weaver-Cathedral / ZOREL-717 master stack. The repository starts with a narrow, testable implementation instead of a large unverified scaffold.

> No mechanism may silently convert uncertainty into authority.

## Core Thesis

```text
Cognition may propose.
Only replayable evidence may authorize.
Reality retains veto.
No receipt, no authority.
```

## What This Repository Does

Lumen currently provides:

- an append-only SHA-256 hash-chained Chronicle ledger;
- a simulated fail-closed hardware veto latch;
- receipt-binding helpers;
- replay verification helpers;
- an end-to-end demo;
- a pytest test suite;
- GitHub Actions CI.

## What This Repository Does Not Claim

Lumen does **not** currently claim:

- production readiness;
- physical FPGA enforcement;
- independent replay;
- external audit;
- model safety;
- institutional authority;
- post-quantum signing;
- WORM-grade storage.

Current evidence status:

```text
Status: MVP_SCAFFOLD_VALIDATED_LOCALLY
Authority: EVIDENCE_ONLY
Production Readiness: NOT_DEMONSTRATED
Hardware Enforcement: SIMULATED_ONLY
Independent Replay: NOT_YET_PERFORMED
```

## Stack Map

```text
OMEGA / CVP Constitution
↓
Weaver Authority Verification
↓
Delta-717 Event Spine
↓
Chronicle / Receipt / Replay
↓
Hardware Veto Simulation
↓
Lumen Evidence Dashboard
```

## Repository Layout

```text
src/lumen/chronicle.py        Append-only hash-chained audit ledger
src/lumen/hardware_veto.py    Simulated fail-closed latch
src/lumen/receipt.py          Receipt binding helpers
src/lumen/replay.py           Replay verification helpers
examples/demo_full_loop.py    End-to-end demo
tests/                        Unit tests
docs/VALIDATION.md            Local validation record
docs/ARCHITECTURE.md          Architecture and evidence model
docs/EVIDENCE_POLICY.md       Claim discipline and evidence levels
```

## Quick Start

```bash
git clone https://github.com/ryansctt1994-sudo/Lumen.git
cd Lumen
python -m venv .venv
source .venv/bin/activate
pip install -e . pytest
pytest tests -q
python examples/demo_full_loop.py
```

Expected test result:

```text
4 passed
```

The demo writes `audit_log.jsonl`, verifies the hash chain, simulates a fail-closed veto event, replays the ledger, and emits a receipt object.

## Local Validation

The current MVP was locally validated with:

```bash
PYTHONPATH=src pytest tests -q
PYTHONPATH=src python examples/demo_full_loop.py
```

Observed result:

```text
4 passed
replay.valid = true
replay.entry_count = 7
replay.authority = EVIDENCE_ONLY
```

See [`docs/VALIDATION.md`](docs/VALIDATION.md).

## Development Rule

Every new authority-related feature must answer four questions:

```text
What claim is being made?
What evidence supports it?
Can it be replayed?
What fails closed if the evidence is missing?
```

## Integration Roadmap

1. Chronicle + hardware veto MVP — current
2. Receipt binding and replay verification — current minimal version
3. Weaver-style authority verifier
4. Delta-717 event spine
5. Quillan evidence dashboard
6. Atropos evaluation environments
7. Hermes skill-evolution gate
8. Independent replay package

## License

Apache-2.0. See [`LICENSE`](LICENSE).
