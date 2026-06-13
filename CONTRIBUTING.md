# Contributing to Lumen

Lumen follows evidence-first development.

## Development Standard

Before submitting a change, answer:

1. What claim does this code make?
2. What evidence supports the claim?
3. Can the behavior be replayed?
4. What fails closed if evidence is missing?

## Required Checks

```bash
pip install -e . pytest
pytest tests -q
python examples/demo_full_loop.py
```

## Claim Discipline

Do not describe a feature as production-ready, hardware-enforced, independently verified, or certified unless the repository contains evidence for that claim.

## Pull Request Expectations

Every PR should include:

- summary of behavior changed;
- tests added or updated;
- evidence boundary;
- known limitations.

## Authority Boundary

Code may produce evidence. Code does not create authority by itself.
