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
