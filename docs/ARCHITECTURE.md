# Lumen Architecture

Lumen is the small executable core of a larger governance stack. Its current job is to demonstrate a narrow but testable chain:

```text
proposal
→ Chronicle append
→ risk evaluation
→ simulated veto latch
→ replay verification
→ receipt emission
```

## Prime Invariant

```text
No mechanism may silently convert uncertainty into authority.
```

## Current Components

### Chronicle

`src/lumen/chronicle.py`

Append-only SHA-256 hash-chained audit ledger. Each entry includes:

- timestamp;
- event type;
- structured data;
- metadata;
- previous hash;
- current hash.

The Chronicle is tamper-evident, not tamper-proof.

### Hardware Veto

`src/lumen/hardware_veto.py`

A simulated fail-closed latch. Once risk crosses threshold, the latch enters `TRIGGERED` and remains halted until explicit reset.

This is a software simulation of the boundary semantics. It is not physical hardware enforcement.

### Receipt

`src/lumen/receipt.py`

A minimal receipt object binding:

- actor;
- event hash;
- previous event hash;
- policy version;
- proposal payload hash;
- admissibility result;
- replay result;
- verifier;
- receipt hash.

### Replay

`src/lumen/replay.py`

Recomputes ledger validity and returns a compact verification report.

## Evidence Boundary

The current implementation establishes local execution evidence only.

```text
Validated: local import, unit tests, demo execution
Not validated: production, independent replay, physical hardware, external audit
```

## Future Integration

Planned integration targets:

- Weaver-style authority verifier;
- Delta-717 event-sourced execution spine;
- Quillan evidence dashboard;
- Atropos evaluation environments;
- Hermes skill-evolution gate.
