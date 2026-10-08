"""Assistant configuration domain."""

from src.assistant.domain.profile import (
    AssistantProfile,
    CommunicationPreferences,
    IdentityRules,
    LanguagePreferences,
    RecordingPolicy,
    TransferRules,
    WorkingHours,
)

__all__ = [
    "AssistantProfile",
    "CommunicationPreferences",
    "IdentityRules",
    "LanguagePreferences",
    "RecordingPolicy",
    "TransferRules",
    "WorkingHours",
]
