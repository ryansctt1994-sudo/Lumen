# Formal Verification Targets

Formal verification artifacts are Tier 4 preservation candidates.

They must not be treated as active proof of the current runtime until they are bound to executable code, run, and receipted.

## Governing Rule

```text
A formal model proves only the model it states.
It does not prove the implementation until refinement is established.
```

## Candidate Artifacts

### TLA+

```text
INVARIANTS.tla
CathedralAOE.tla
UpperRoom.tla
DV_SMR.tla
NSIR_UNIFIED.tla
```

### Lean 4

```text
CathedralOS.lean
Ledger.lean
StepSafety.lean
refinement_proof.lean
PBFT_Quorum.lean
CESK_star.lean
```

### SMT / Z3 / CVC5

```text
z3_sovereignty_spec.py
veritas_sieve_z3.py
winning_region_table.json
```

## Required Before Evaluation

Formal work begins only after Tier 2 produces a stable replay target:

```text
Chronicle event schema frozen
receipt schema frozen
replay equivalence test passing
E3 candidate package generated
```

## Promotion Requirements

A formal artifact can be promoted only with:

```text
model source
tool version
run command
solver/prover output
failure/success status
runtime binding note
receipt hash
```

## Current Status

```text
TLA+ authority: NONE
Lean authority: NONE
SMT authority: NONE
Runtime binding: NOT ESTABLISHED
```

## Correct Order

```text
1. Prove replay works locally.
2. Freeze executable schema.
3. Bind formal model to schema.
4. Run model checker / prover.
5. Receipt proof output.
6. Attempt refinement claim.
```

Until then, formal artifacts remain preserved but quarantined.
