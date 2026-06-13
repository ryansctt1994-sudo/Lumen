# Lumen Integration Guide

This guide defines how FreeLattice, Hermes, Atropos, Claw, Quillan, and Delta-717 integrate without weakening Lumen's evidence spine.

## Ownership Model

```text
OMEGA / CVP        constitution and authority principles
Weaver             authority verification
Lumen Chronicle    evidence, receipts, replay
Delta-717          event-sourced execution model
Claw               harness runtime
Hermes             skill and memory evolution
Atropos            evaluation environments
Quillan            observability dashboard
FreeLattice        local-first human shell
```

## Rule

```text
Interfaces may propose.
Runtimes may execute.
Learning systems may improve.
Only evidence may promote authority.
```

## Provider Mesh

Providers implement `lumen.providers.Provider`.

Required methods:

```text
generate
health_check
```

Optional methods:

```text
stream
embed
tools
```

Providers do not authorize execution. They only produce candidate outputs.

## Skill Manifest

Skills must declare:

```text
name
version
description
inputs
outputs
required providers
evaluations
evidence level
optional signature
```

Promotion pipeline:

```text
candidate skill
→ manifest hash
→ unit tests
→ Atropos evaluation
→ Chronicle receipt
→ human review
→ registry promotion
```

## FreeLattice Adapter

FreeLattice-style entries must not bypass Chronicle.

```text
Core Entry / Question / Letter
→ FreeLatticeAdapter
→ Chronicle event
→ Receipt
→ Replay status
```

## Quillan / Garden Visualization

Visualization is observability, not authority.

Allowed visual nodes:

```text
Claim
Receipt
Replay
Skill
Provider
Agent
Evaluation
```

## Atropos Evaluation

Atropos environments should be replayable from Chronicle records whenever possible.

Suggested environments:

```text
council_env
skill_env
replay_env
governance_env
provider_env
```

## Evidence Boundary

The current integration scaffold is E2-local only. It adds interfaces and tests but does not establish production readiness, hardware enforcement, or independent replay.
