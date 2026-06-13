# Evidence Policy

Lumen uses explicit evidence boundaries to prevent claim inflation.

## Rule

```text
A claim must not be promoted beyond the evidence that supports it.
```

## Evidence Levels

```text
E0 — Concept only
E1 — Claimed output or design text
E2 — Local executable run
E3 — Signed or hashed receipt package
E4 — Independent replay
E5 — Independent production or hardware verification
```

## Current Repository Level

```text
E2 — Local executable run
```

Reason:

- tests pass locally;
- demo runs locally;
- Chronicle verifies local hash chain;
- receipt object is emitted;
- replay report returns valid.

Limits:

- no independent replay;
- no external auditor;
- no physical hardware;
- no WORM storage;
- no cryptographic signature authority.

## Required Language

Allowed:

```text
validated locally
simulated hardware veto
hash-chain verifies
receipt object emitted
replay report valid
```

Not allowed yet:

```text
production ready
hardware enforced
independently verified
WORM sealed
post-quantum certified
safe AI system
```

## Promotion Requirements

To move from E2 to E3:

- save demo output as a receipt artifact;
- include SHA-256 manifest;
- bind commit hash to validation run;
- store replay output.

To move from E3 to E4:

- independent machine reruns tests and demo;
- independent result hash matches expected validation envelope;
- third-party replay report is attached.
