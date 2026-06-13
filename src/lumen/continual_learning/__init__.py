"""Continual learning primitives for Lumen.

This layer distinguishes useful transferable learning from memory clutter.
"""

from .models import ExperienceRecord, SkillCandidate, TransferReport, MemoryUtilityReport, PromotionDecision, ForgettingReport
from .skill_extractor import SkillExtractor
from .transfer_analyzer import TransferAnalyzer
from .memprobe import MemProbe
from .promotion_engine import PromotionEngine
from .forgetting_detector import ForgettingDetector

__all__ = [
    "ExperienceRecord",
    "SkillCandidate",
    "TransferReport",
    "MemoryUtilityReport",
    "PromotionDecision",
    "ForgettingReport",
    "SkillExtractor",
    "TransferAnalyzer",
    "MemProbe",
    "PromotionEngine",
    "ForgettingDetector",
]
