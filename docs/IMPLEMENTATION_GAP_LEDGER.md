# Implementation Gap Ledger

This document is the null-reference ledger for Lumen Nexus.

Its purpose is to prevent architectural hallucination by explicitly recording components that are preserved or designed but not yet executable, tested, verified, or authorized.

## Governing Rule

```text
If a subsystem is listed here, it has zero execution authority.
```

## Current Proven Core

The current active proof path is limited to:

```text
src/lumen/chronicle.py
src/lumen/receipt.py
src/lumen/replay.py
src/lumen/replay_cache/sqlite_replay.py
src/lumen/authority/verifier.py
examples/demo_full_loop.py
scripts/generate_e3_receipt.py
scripts/verify_e3_package.py
```

Everything else remains below authority unless explicitly promoted by receipt and replay evidence.

## Gaps

### Hardware Veto / Silicon Enforcement

Status: preserved candidate, not active.

Missing:

```text
FPGA target selected
synthesis run
timing report
physical trace
external verification
hardware receipt
```

Authority: none.

### Formal Verification

Status: preserved candidate, not active.

Missing:

```text
TLA+ model bound to current code
TLC run output
Lean proof compiled against current runtime model
Z3 proof integrated with verifier
proof receipt
```

Authority: none.

### Witness Federation

Status: preserved candidate, not active.

Missing:

```text
multi-node replay protocol
witness identity registry
quorum policy
Byzantine failure tests
attestation receipts
```

Authority: none.

### Delta-717 Event Spine

Status: architecture target.

Missing:

```text
event schema imported
state fold implemented
replay equivalence tests
receipt integration
```

Authority: none.

### Hermes Skill Evolution

Status: scaffolded through skill manifests and continual learning primitives.

Missing:

```text
real skill registry
Atropos evaluation bridge
promotion receipts
human review workflow
```

Authority: none beyond EVIDENCE_ONLY scaffolding.

### Atropos Evaluation

Status: integration target.

Missing:

```text
Atropos environment skeletons
rollout schema
score receipts
transfer evaluation artifacts
```

Authority: none.

### FreeLattice Shell

Status: adapter scaffold only.

Missing:

```text
local shell bridge
IndexedDB export/import path
Chronicle sync adapter
UI evidence panel
```

Authority: none.

### Quillan Observatory

Status: schema only.

Missing:

```text
graph builder
visualization UI
Chronicle query backend
evidence heatmaps
```

Authority: none.

## Promotion Requirement

A gap can be removed only when it has:

```text
runnable code
unit test
replayable output
receipt artifact
explicit evidence level
```

## Current System Posture

```text
E3_CANDIDATE_SCAFFOLD
Evidence-only
No hardware authority
No formal proof authority
No distributed authority
```
