"""Receipt binding helpers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Receipt:
    actor_id: str
    event_hash: str
    previous_event_hash: Optional[str]
    policy_version: str
    proposal_payload_hash: str
    admissibility_result: str
    replay_result: str
    verifier_id: str
    timestamp: str
    receipt_hash: str

    @staticmethod
    def hash_payload(payload: Dict[str, Any]) -> str:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @classmethod
    def create(
        cls,
        *,
        actor_id: str,
        event_hash: str,
        previous_event_hash: Optional[str],
        policy_version: str,
        proposal_payload: Dict[str, Any],
        admissibility_result: str,
        replay_result: str,
        verifier_id: str,
    ) -> "Receipt":
        base = {
            "actor_id": actor_id,
            "event_hash": event_hash,
            "previous_event_hash": previous_event_hash,
            "policy_version": policy_version,
            "proposal_payload_hash": cls.hash_payload(proposal_payload),
            "admissibility_result": admissibility_result,
            "replay_result": replay_result,
            "verifier_id": verifier_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return cls(**base, receipt_hash=cls.hash_payload(base))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
