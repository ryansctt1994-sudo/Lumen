"""FreeLattice-to-Chronicle adapter.

This adapter preserves useful local-first FreeLattice concepts while routing
memory writes through Lumen's evidence layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from lumen.chronicle import Chronicle
from lumen.receipt import Receipt


@dataclass(frozen=True)
class FreeLatticeEntry:
    kind: str
    content: str
    source_id: str
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class FreeLatticeAdapter:
    """Writes FreeLattice-style entries as Chronicle events with receipts."""

    def __init__(self, chronicle: Chronicle, *, policy_version: str = "v0.1"):
        self.chronicle = chronicle
        self.policy_version = policy_version

    def plant_entry(self, entry: FreeLatticeEntry, *, actor_id: str = "freelattice_adapter") -> Dict[str, Any]:
        event = self.chronicle.append(
            "FREELATTICE_ENTRY_IMPORTED",
            {
                "kind": entry.kind,
                "content": entry.content,
                "source_id": entry.source_id,
                "session_id": entry.session_id,
            },
            metadata={
                "origin": "FreeLattice",
                "adapter": "FreeLatticeAdapter",
                **entry.metadata,
            },
        )

        receipt = Receipt.create(
            actor_id=actor_id,
            event_hash=event["hash"],
            previous_event_hash=event["prev_hash"],
            policy_version=self.policy_version,
            proposal_payload={
                "kind": entry.kind,
                "source_id": entry.source_id,
                "session_id": entry.session_id,
            },
            admissibility_result="IMPORTED_AS_EVIDENCE_RECORD",
            replay_result="PENDING_REPLAY",
            verifier_id="lumen.adapters.freelattice",
        )

        return {"event": event, "receipt": receipt.to_dict()}
