# Lumen MVP Validation

Validation performed after initial scaffold push.

## Commands Tested

```bash
PYTHONPATH=src pytest tests -q
PYTHONPATH=src python examples/demo_full_loop.py
```

## Observed Result

```text
4 passed
```

The demo produced a replay report with:

```json
{
  "valid": true,
  "entry_count": 7,
  "authority": "EVIDENCE_ONLY"
}
```

## What This Proves

- The package imports successfully.
- The Chronicle hash chain verifies.
- The simulated hardware veto latches at threshold.
- Replay reports valid local evidence.
- Receipt creation works.
- The end-to-end demo runs locally.

## What This Does Not Prove

- Production readiness.
- Physical hardware enforcement.
- Independent replay.
- External audit.
- Model safety.
- Institutional authority.

## Evidence Boundary

```text
LOCAL_VALIDATION_PASS
EVIDENCE_ONLY
SIMULATED_HARDWARE
NO_PRODUCTION_AUTHORITY
```

## Maintenance candidate: 2026-10-07

The local verifier now requires a literal boolean replay pass and a nonempty,
well-formed matching replay tip. It checks receipt content integrity and binds
the supplied claim to the receipted proposal payload. These hashes do not
establish a trusted signer, independent replay, or operational authority.

SQLite retries with identical receipt ID/content are idempotent. Reuse with
changed content or predecessor is refused transactionally. Candidate package
runs use fresh UUIDs and link to the verified previous cache tip, so repeated
runs do not silently reuse stale records. Concurrent independent chain appends
remain outside this candidate's guarantee.

Validation: 23 local pytest cases pass (13 existing plus 10 new cases), including
claim substitution, modified receipts, absent tips, conflicting concurrent ID
writes, nonfinite payloads, and repeated package generation. The demo and package
integrity verifier also pass locally. Portfolio promotion remains withheld.

## P0-002 maintained-source repair: transactional replay tip admission

**Scope:** `src/lumen/replay_cache/sqlite_replay.py` on the existing unmerged
`maintenance/receipt-binding-20261007` candidate branch. This is not an
automatic transplant of P0-001's historical Lumen archive patches.

### Exact hosted RED → GREEN

- **RED:** commit `5b0ed5013b588376dc4df708fabe18863423305b`,
  [GitHub Actions run 37877069476](https://github.com/ryansctt1994-sudo/Lumen/actions/runs/37877069476),
  **6 failed, 24 passed**. A test-only change reproduced failure to reject
  stale or impossible predecessors, two distinct writers appending to the same
  tip, append following stored-data tampering, and an uncontrolled malformed
  JSON exception on verification.
- **GREEN:** implementation commit `83b45296430c479c50e6b776a9cd3e4e816e6261`,
  [GitHub Actions run 37877148835](https://github.com/ryansctt1994-sudo/Lumen/actions/runs/37877148835),
  **30 passed**; demo, E3-candidate generation, and package verifier steps
  also completed successfully in that workflow.

### What the code enforces

For a **new** receipt ID, `insert` obtains SQLite's `BEGIN IMMEDIATE` write
transaction, verifies **all** existing hash links and stored JSON, and accepts
the new entry only when its `prev_hash` equals the verified current tip.
The expected predecessor of an empty chain is `None`. An outdated writer must
re-read the tip and explicitly retry. The transaction rejects races before
they can create two siblings; it does not silently rebase evidence.

For an **existing** receipt ID, a byte-equivalent/semantically identical retry
with the same hash and predecessor remains idempotent after chain validation,
including when newer entries have subsequently been appended. Reuse of that ID
with different contents or predecessor is rejected. Malformed stored JSON
returns `valid=False` with `reason=malformed_entry`, and prevents append.

The O(n) full-chain scan per write is intentional for this small local
evidence cache, **not** an efficient production ledger design.

### Limits that remain open

- An attacker controlling the database can rewrite the whole chain and
  recompute every unkeyed SHA-256 hash, or remove its tail. No external trusted
  checkpoint/WORM anchor has been implemented here.
- No issuer authentication, signed replay attestation, immutable environment,
  trustworthy operational admission, cross-host witness, or independent E4
  reproduction is established.
- SQLite's transaction lock applies only to cooperative writers of this **same
  database** and is not distributed consensus across separate databases/hosts.
- The review branch remains unmerged; hosted success is **repo-native CI
  execution**, not production approval.

**Portfolio boundary:** E2 / W0 / O0 WITHHELD / PRODUCTION PROHIBITED.
