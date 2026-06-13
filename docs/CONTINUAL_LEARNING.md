# Continual Learning Layer

Inspired by the AGENTCL framing: agents do not improve merely because they retain memory. They improve only when past experience produces measurable transfer on later tasks without causing confusion or degradation.

## Principle

```text
Storage is not learning.
Memory is not transfer.
A skill is not promoted until it improves later tasks under replayable evaluation.
```

## Pipeline

```text
Chronicle Event
→ Replay
→ ExperienceRecord
→ SkillCandidate
→ TransferReport
→ MemoryUtilityReport
→ PromotionDecision
→ Skill Registry
```

## Components

```text
src/lumen/continual_learning/models.py
src/lumen/continual_learning/skill_extractor.py
src/lumen/continual_learning/transfer_analyzer.py
src/lumen/continual_learning/memprobe.py
src/lumen/continual_learning/promotion_engine.py
src/lumen/continual_learning/forgetting_detector.py
```

## Promotion Criteria

Default rule:

```text
replay_valid = true
transfer_gain >= 0.10
degradation <= 0.03
memory_utility >= 0.0
```

A promoted skill remains `EVIDENCE_ONLY` until stronger independent replay and authority verification are attached.

## Forgetting / Clutter Detection

Skills can be marked:

```text
ACTIVE
STALE
REVIEW
DEPRECATED
```

Reasons include:

```text
negative transfer
conflict threshold exceeded
unused beyond retention window
```

## Evidence Boundary

The current implementation is deterministic local scaffolding. It does not prove autonomous continual learning. It provides the measurable structure required to test whether memory improves later performance.
