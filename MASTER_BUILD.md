# Lumen Master Evidence Runtime v1

**Portfolio role:** Repository 2 of 3  
**Authority:** EVIDENCE_ONLY  
**Production readiness:** NOT DEMONSTRATED  
**Independent reproduction:** NOT ESTABLISHED

Lumen is the only active repository in the master build that owns executable Chronicle, receipt, replay, persistent replay-cache, and witness-package behavior.

## Canonical core

The retained core is intentionally small:

- append-only, hash-chained Chronicle;
- canonical receipt binding;
- semantic replay verification;
- persistent replay cache with restart and concurrency tests;
- failure-atomic state transition and receipt emission;
- bounded authority-verifier interface;
- witness package generation and verification;
- simulation-only veto interface;
- provider and skill schemas that do not grant execution authority.

## Selected intake

`agency-agents6` may contribute only its bounded action-authorization and safety-envelope primitives. Source identity, license, copied paths, and local modifications must be recorded before integration.

The following repositories are donors or references, not components automatically included in Lumen:

- `AI-Research-SKILLs`, `awesome-agent-skills`, and `skills`;
- `ai-agent-terraform` and `ai-ticket`;
- `FreeLattice`, `Gbrain-Reinforced`, `hermes-agent-self-evolution`;
- `owl`, `ruflo`, `SuperAGI`, and `swarms`;
- `tinyclaw`, `strix`, and `rosclaw`;
- `Cortex` and `NexusGate`;
- Quillan evidence-graph or sparse-routing schemas.

Any accepted donor feature must enter through `integrations/<name>/` with a disabled-by-default manifest. No donor runtime may be invoked merely because its repository exists.

## Required adapter manifest

Every integration must declare:

```json
{
  "name": "adapter-name",
  "upstream_repository": "owner/repository",
  "upstream_commit": "immutable-sha",
  "license": "SPDX identifier",
  "enabled_by_default": false,
  "capabilities": [],
  "prohibited_capabilities": [],
  "authority": "NONE",
  "tests": [],
  "receipts": [],
  "non_claims": []
}
```

## Migration order

1. Stabilize Chronicle canonicalization and external-anchor interface.
2. Stabilize receipt schema, predecessor binding, and failure-atomic emission.
3. Merge persistent replay-cache hardening from reviewed authority-spine work.
4. Create a clean witness bundle with environment, commands, raw logs, hashes, and failure transcript.
5. Integrate one donor adapter at a time, beginning with non-executing schema adapters.
6. Keep operations runtimes, security witnesses, and robotics simulation disabled until explicit promotion gates are satisfied.

## Rejection rules

Lumen must reject or hold when:

- source or dependency pins are absent;
- license identity is unresolved;
- receipt or manifest hashes do not match;
- replay evidence conflicts with the requested action;
- the requested capability exceeds the authority lease;
- execution would require an unapproved external service, transport, skill, credential, or physical action;
- an evidence claim exceeds its demonstrated modality.

## Non-claims

This document does not establish E3 or E4 evidence, production readiness, external audit, physical hardware enforcement, model safety, autonomous authority, or institutional authority. Those require artifact-scoped receipts and independent review.