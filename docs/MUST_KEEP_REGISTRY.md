# Must-Keep Registry

This registry is a preservation manifest, not an execution claim.

## Prime Boundary

```text
Listed does not mean implemented.
Implemented does not mean tested.
Tested does not mean verified.
Verified does not mean authorized.
```

## Tier 0 — Constitutional Docs

Preserve as governing doctrine and invariant sources.

Examples:

```text
WEAVER_OS_AUTHORITY_AUDIT_v0_1.md
CONSOLIDATED_ARTIFACT_REGISTRY.md
ARCHITECTURE_21_LAYERS.md
CATHEDRAL_OS_RFC.md
TIER_0_PRIME_INVARIANTS.md
PRIME_INVARIANT.md
SDA_251222_182309.pdf
Epistemic.pdf
```

Authority status: doctrine only unless compiled into executable policy and tested.

## Tier 1 — Runnable Python MVP

Preserve as candidate executable runtime code.

Examples:

```text
weaver_kernel_v3.5.py
cathedral_kernel_refactored.py
reality_gate.py
ilion_gate.py
master_orchestrator.py
aegis_cesk.py
```

Authority status: none until imported, tested, receipted, and replayed.

## Tier 2 — Replay / Receipt Infrastructure

Highest-priority implementation tier because all later verification depends on it.

Examples:

```text
chronicle.py
receipt.py
hashchain.py
replay_validator.py
replay_engine.py
canonical_serializer.py
event_serializer.py
fold_chronicle.jsonl
```

Current Lumen analogs:

```text
src/lumen/chronicle.py
src/lumen/receipt.py
src/lumen/replay.py
src/lumen/replay_cache/sqlite_replay.py
scripts/generate_e3_receipt.py
scripts/verify_e3_package.py
```

Authority status: evidence-only after successful local execution.

## Tier 3 — Hardware Candidates

Preserve for future physical validation. Do not treat as active enforcement until synthesized, tested, and independently verified.

Examples:

```text
lucifer_latch.v
lucifer_latch_hardened.v
heartbeat_watchdog_v2.v
watchdog.ino
gan_power_stage_if.sv
trace_attestation_engine.sv
dcls_comparator.sv
cathedral_uart_top.v
steward_efuse_ignition.py
gate_h0_temporal_filter.sv
gate_h0_sync_chain.sv
h0_atomic_fsm.sv
```

Authority status: zero in current Lumen MVP.

## Tier 4 — Formal Verification Candidates

Preserve for later proof work. Formal verification must follow an executable replay target.

Examples:

```text
INVARIANTS.tla
CathedralAOE.tla
UpperRoom.tla
DV_SMR.tla
NSIR_UNIFIED.tla
CathedralOS.lean
Ledger.lean
StepSafety.lean
refinement_proof.lean
z3_sovereignty_spec.py
veritas_sieve_z3.py
winning_region_table.json
```

Authority status: zero until bound to runnable code and checked.

## Tier 5 — Swarm / Federation Candidates

Preserve for later witness and distributed consensus work.

Examples:

```text
crucible_trial_4_node.py
hotstuff_core.py
libp2p_chronicle_sync.py
witness_registry.py
witness_federation_sim.py
slashing_conditions.yaml
```

Authority status: zero until local replay and E3 artifacts exist.

## Tier 6 — Archive / Speculative

Preserve as research, narrative, mythos, or future design. Must not be represented as runtime authority.

Examples:

```text
LogOS.Primus
mythic documents
symbolic protocols
unexecuted architecture notes
speculative agent identities
```

Authority status: none.

## Current Priority

```text
Tier 2 first.
E3 receipt package first.
Independent replay next.
Hardware and formal proof later.
```
