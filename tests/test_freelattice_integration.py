from lumen import Chronicle
from lumen.adapters import FreeLatticeAdapter, FreeLatticeEntry
from lumen.skills import SkillEvaluation, SkillIO, SkillManifest


def test_freelattice_entry_import_creates_chronicle_event_and_receipt(tmp_path):
    chronicle = Chronicle(tmp_path / "audit.jsonl")
    adapter = FreeLatticeAdapter(chronicle)
    result = adapter.plant_entry(
        FreeLatticeEntry(kind="question", content="What evidence supports this?", source_id="q1", session_id="s1")
    )
    assert result["event"]["event_type"] == "FREELATTICE_ENTRY_IMPORTED"
    assert result["receipt"]["event_hash"] == result["event"]["hash"]
    assert Chronicle.verify(tmp_path / "audit.jsonl") is True


def test_skill_manifest_hash_and_validation():
    manifest = SkillManifest(
        name="receipt-generation",
        version="0.1.0",
        description="Generate a receipt for a Chronicle event.",
        inputs=[SkillIO(name="event", schema={"type": "object"})],
        outputs=[SkillIO(name="receipt", schema={"type": "object"})],
        evaluations=[SkillEvaluation(command="pytest tests -q", success_criteria="tests pass")],
        evidence_level="E1",
    )
    manifest.validate_for_candidate()
    assert len(manifest.manifest_hash()) == 64
