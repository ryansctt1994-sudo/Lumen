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
- SQLite replay cache;
- minimal Weaver-style authority verifier;
- provider mesh interface;
- skill manifest schema;
- FreeLattice-to-Chronicle adapter;
- Quillan evidence graph schema;
- E3 candidate receipt package generator/verifier;
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
Status: E3_CANDIDATE_SCAFFOLD
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
src/lumen/chronicle.py              Append-only hash-chained audit ledger
src/lumen/hardware_veto.py          Simulated fail-closed latch
src/lumen/receipt.py                Receipt binding helpers
src/lumen/replay.py                 Replay verification helpers
src/lumen/replay_cache/             SQLite replay cache
src/lumen/authority/                Weaver-style authority verifier
src/lumen/providers/                Provider mesh interfaces
src/lumen/skills/                   Skill manifest schema
src/lumen/adapters/freelattice.py   FreeLattice import adapter
examples/demo_full_loop.py          End-to-end demo
scripts/generate_e3_receipt.py      E3 candidate package generator
scripts/verify_e3_package.py        E3 candidate package verifier
tests/                              Unit tests
docs/VALIDATION.md                  Local validation record
docs/ARCHITECTURE.md                Architecture and evidence model
docs/EVIDENCE_POLICY.md             Claim discipline and evidence levels
docs/INTEGRATION_GUIDE.md           Integration ownership model
docs/FREELATTICE_INTEGRATION.md     FreeLattice extraction notes
observatory/quillan/schema.json     Evidence graph schema
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

Expected test result after the E3 scaffold expansion:

```text
9 passed
```

The demo writes `audit_log.jsonl`, verifies the hash chain, simulates a fail-closed veto event, replays the ledger, and emits a receipt object.

## E3 Candidate Package

Generate local candidate artifacts:

```bash
python scripts/generate_e3_receipt.py
python scripts/verify_e3_package.py
```

This creates:

```text
receipts/demo_audit_log.jsonl
receipts/demo_receipt.json
receipts/demo_receipt.sha256
receipts/demo_replay_cache.sqlite
```

Important: this is an **E3 candidate** path. E3 is earned only when the generated artifacts are committed, hashed, and reviewed. Independent replay is still required for E4.

## Local Validation

The earlier MVP was locally validated with:

```bash
PYTHONPATH=src pytest tests -q
PYTHONPATH=src python examples/demo_full_loop.py
```

Observed result before the E3 expansion:

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
2. Receipt binding and replay verification — current
3. SQLite replay cache — current
4. Weaver-style authority verifier — current minimal version
5. FreeLattice shell bridge — scaffolded via adapter
6. Quillan evidence dashboard — schema added
7. Atropos evaluation environments
8. Hermes skill-evolution gate
9. Independent replay package

## License

Apache-2.0. See [`LICENSE`](LICENSE).
