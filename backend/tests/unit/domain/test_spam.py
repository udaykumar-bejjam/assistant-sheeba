from __future__ import annotations

from src.ai_agent.domain.spam import SpamClassification, SpamDetectionService
from src.shared.domain.value_objects import CallIntent, PhoneNumber


def test_legitimate_by_default() -> None:
    service = SpamDetectionService()
    result = service.assess(phone=PhoneNumber("+14155552671"))
    assert result.classification == SpamClassification.LEGITIMATE


def test_known_spam_and_frequency() -> None:
    service = SpamDetectionService()
    result = service.assess(
        phone=PhoneNumber("+14155552671"),
        known_spam=True,
        call_count_24h=5,
        intent=CallIntent.SPAM,
    )
    assert result.score >= 0.8
    assert result.classification == SpamClassification.LIKELY_SPAM
    assert result.reasons
