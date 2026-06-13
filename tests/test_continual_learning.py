from lumen.continual_learning import (
    ExperienceRecord,
    ForgettingDetector,
    MemProbe,
    PromotionEngine,
    SkillExtractor,
    TransferAnalyzer,
)


def test_skill_extractor_requires_replay_valid_success_support():
    experiences = [
        ExperienceRecord("t1", "refactor", "success", "r1", True),
        ExperienceRecord("t2", "refactor", "success", "r2", True),
        ExperienceRecord("t3", "research", "failure", "r3", True),
        ExperienceRecord("t4", "refactor", "success", "r4", False),
    ]
    candidates = SkillExtractor().extract(experiences, min_support=2)
    assert len(candidates) == 1
    assert candidates[0].name == "skill_refactor"
    assert candidates[0].metadata["support"] == 2


def test_transfer_memprobe_and_promotion():
    transfer = TransferAnalyzer().analyze(
        skill_name="skill_refactor",
        baseline_score=0.70,
        skill_score=0.85,
        replay_valid=True,
    )
    memory = MemProbe().evaluate(
        memory_id="m1",
        with_memory_score=0.85,
        without_memory_score=0.70,
    )
    decision = PromotionEngine(min_transfer_gain=0.10, max_degradation=0.03).decide(transfer, memory)
    assert transfer.transfer_gain > 0.10
    assert memory.memory_utility > 0.10
    assert decision.promote is True


def test_promotion_fails_closed_on_invalid_replay():
    transfer = TransferAnalyzer().analyze(
        skill_name="skill_bad",
        baseline_score=0.70,
        skill_score=0.95,
        replay_valid=False,
    )
    decision = PromotionEngine().decide(transfer)
    assert decision.promote is False
    assert "replay invalid" in decision.reason


def test_forgetting_detector_flags_negative_transfer_and_stale_skills():
    detector = ForgettingDetector(max_days_unused=180, max_conflicts=3)
    negative = detector.evaluate(skill_name="skill_old", transfer_gain=-0.01)
    stale = detector.evaluate(skill_name="skill_stale", transfer_gain=0.05, days_unused=181)
    assert negative.status == "DEPRECATED"
    assert stale.status == "STALE"
