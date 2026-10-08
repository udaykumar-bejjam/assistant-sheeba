"""Spam detection domain service."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from src.shared.domain.value_objects import CallIntent, PhoneNumber


class SpamClassification(StrEnum):
    LEGITIMATE = "LEGITIMATE"
    SUSPICIOUS = "SUSPICIOUS"
    LIKELY_SPAM = "LIKELY_SPAM"


@dataclass(frozen=True, slots=True)
class SpamAssessment:
    score: float
    classification: SpamClassification
    reasons: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SpamDetectionConfig:
    suspicious_threshold: float = 0.55
    likely_spam_threshold: float = 0.8
    # Never auto-block solely on AI; thresholds only classify.
    auto_block: bool = False


class SpamDetectionService:
    def __init__(self, config: SpamDetectionConfig | None = None) -> None:
        self.config = config or SpamDetectionConfig()

    def assess(
        self,
        *,
        phone: PhoneNumber,
        intent: CallIntent = CallIntent.UNKNOWN,
        call_count_24h: int = 0,
        known_spam: bool = False,
        conversation_hints: list[str] | None = None,
    ) -> SpamAssessment:
        score = 0.0
        reasons: list[str] = []

        if known_spam:
            score += 0.7
            reasons.append("number flagged in known spam list")

        if intent == CallIntent.SPAM:
            score += 0.35
            reasons.append("intent classified as spam")

        if call_count_24h >= 5:
            score += 0.25
            reasons.append("high call frequency in 24h")
        elif call_count_24h >= 3:
            score += 0.1
            reasons.append("elevated call frequency")

        hints = conversation_hints or []
        spammy = ("lottery", "Congratulations you won", "investment guaranteed", "kycrefund")
        for hint in hints:
            lower = hint.lower()
            if any(s.lower() in lower for s in spammy):
                score += 0.2
                reasons.append("conversation content matches spam patterns")
                break

        # Unknown short codes / patterns — keep mild.
        if phone.value.startswith("+1900"):
            score += 0.3
            reasons.append("premium-rate pattern")

        score = min(1.0, score)
        if score >= self.config.likely_spam_threshold:
            classification = SpamClassification.LIKELY_SPAM
        elif score >= self.config.suspicious_threshold:
            classification = SpamClassification.SUSPICIOUS
        else:
            classification = SpamClassification.LEGITIMATE
            if not reasons:
                reasons.append("no spam indicators")

        return SpamAssessment(score=score, classification=classification, reasons=reasons)
