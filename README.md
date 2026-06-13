# Lumen

**Lumen** is the MVP master stack for receipt-bound authority verification, replayable evidence, and governed AI execution.

This repository intentionally starts small. It does not claim production readiness, hardware enforcement, independent audit, or model safety. It provides a runnable scaffold for the core invariant:

> No mechanism may silently convert uncertainty into authority.

## Core Thesis

```text
Cognition may propose.
Only replayable evidence may authorize.
Reality retains veto.
No receipt, no authority.
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

## Current Evidence Boundary

```text
Status: MVP_SCAFFOLD
Authority: NONE
Production Readiness: NOT_DEMONSTRATED
Hardware Enforcement: SIMULATED_ONLY
Independent Replay: NOT_YET_PERFORMED
```

## Quick Start

```bash
python examples/demo_full_loop.py
python -m pytest tests -q
```

The demo writes `audit_log.jsonl`, verifies the hash chain, and demonstrates a simulated fail-closed hardware veto.

## Repository Layout

```text
src/lumen/chronicle.py        Append-only hash-chained audit ledger
src/lumen/hardware_veto.py    Simulated fail-closed latch
src/lumen/receipt.py          Receipt binding helpers
src/lumen/replay.py           Replay verification helpers
examples/demo_full_loop.py    End-to-end demo
tests/                        Unit tests
```

## Integration Roadmap

1. Chronicle + hardware veto MVP
2. Receipt binding and replay verification
3. Weaver-style authority verifier
4. Delta-717 event spine
5. Quillan evidence dashboard
6. Atropos evaluation environments
7. Hermes skill-evolution gate

## License

MIT
