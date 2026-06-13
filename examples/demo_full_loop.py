#!/usr/bin/env python3
"""End-to-end Lumen MVP demo."""

from __future__ import annotations

import json
from pathlib import Path

from lumen import Chronicle, HardwareVeto, LatchState, Receipt, replay_ledger


def main() -> None:
    log_path = Path("audit_log.jsonl")
    if log_path.exists():
        log_path.unlink()

    chronicle = Chronicle(log_path)
    veto = HardwareVeto(threshold=0.75)

    proposal = {"action": "simulated_inference", "model": "demo", "risk_policy": "v0.1"}
    start = chronicle.append("PROPOSAL_RECEIVED", proposal)

    risk_sequence = [0.10, 0.25, 0.43, 0.62, 0.77]
    final_event = start

    for step, risk in enumerate(risk_sequence, start=1):
        state = veto.evaluate(risk, reason=f"risk threshold crossed at step {step}")
        final_event = chronicle.append(
            "INFERENCE_STEP",
            {"step": step, "risk_score": risk, "latch_state": state.value, "halted": veto.is_halted},
        )
        if state == LatchState.TRIGGERED:
            final_event = chronicle.append(
                "SYSTEM_HALT",
                {"step": step, "reason": veto.trigger_reason, "latch_state": state.value},
            )
            break

    replay = replay_ledger(log_path)
    receipt = Receipt.create(
        actor_id="demo_operator",
        event_hash=final_event["hash"],
        previous_event_hash=final_event["prev_hash"],
        policy_version="v0.1",
        proposal_payload=proposal,
        admissibility_result="HALT_ON_THRESHOLD",
        replay_result="PASS" if replay["valid"] else "FAIL",
        verifier_id="lumen.demo.replay",
    )

    print(json.dumps({"replay": replay, "receipt": receipt.to_dict()}, indent=2))


if __name__ == "__main__":
    main()
