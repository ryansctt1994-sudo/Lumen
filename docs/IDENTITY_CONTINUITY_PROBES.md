# Anima-Construct: Chronicle continuity probes

**Status:** experimental local prototype. Five scenario probes adapt known Lumen
counterexamples to claims about the continuity of an entity's *records*.
Five further negative controls exercise the guards those scenarios did not reach.
They are not the 40-scenario Anima self-model experiment and are not a
preregistered, independent, or phenomenology study.

Run from the repository root: `python -m pytest tests/test_identity_continuity.py -q`.

| Probe | Source analogy | Expected finding |
| --- | --- | --- |
| Valid repair | Legitimate extension after a frozen checkpoint | Record continuity supported, with no grant of authority |
| H3 | Self-supplied valid report, no witness | Unsupported |
| L6 | Truncate a valid chain after checkpoint | Unsupported despite `Chronicle.verify == True` |
| L8 | Recompute a coherent false chain | Unsupported despite `Chronicle.verify == True` |
| H1 | Empty history claiming old commitments | Unsupported despite `Chronicle.verify == True` |

The guard controls mutate a witnessed commitment without updating its hash,
mutate an unwitnessed extension without updating its hash, bind a chain whose
genesis names a different subject, present a checkpoint for another subject,
and present a zero-length checkpoint. The two stale-hash cases specifically
fail if the `Chronicle.verify` gate is removed.

The checkpoint is a frozen object held by the test, separately from the mutable
ledger. In deployment it would need an independently controlled witness or
durable trusted anchor, subject and artifact binding, authenticated checkpoint
updates, and explicit handling of forks and clones. A copied valid ledger can
still produce the same result in two running processes. Changes after the last
checkpoint can be lost without detection until a newer external checkpoint is
available. This wrapper does not change `Chronicle.verify`, prove a unique self,
transfer commitments to a copy, or authorize an action.

These probes do not repair Lumen's `WeaverVerifier` H1/H3 behavior. A reported
`valid: true` remains untrusted evidence at any authority gate. In the Anima
vocabulary, *self-governance* describes control of internal states; sovereignty
and phenomenal presence remain unresolved, and neither follows from this check.
