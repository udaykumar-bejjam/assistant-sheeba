from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from src.assistant.domain.profile import AssistantProfile
from src.infrastructure.container import AppContainer
from src.interfaces.api.deps import get_container

router = APIRouter()


def _container(request: Request) -> AppContainer:
    return get_container(request)


@router.get("/settings")
async def get_settings(container: AppContainer = Depends(_container)) -> dict[str, object]:
    profile = await container.profiles.get("default")
    if profile is None:
        profile = AssistantProfile.default()
        await container.profiles.save(profile)
    return {
        "assistant_name": profile.identity.assistant_name,
        "owner_name": profile.identity.owner_name,
        "greeting": profile.identity.greeting,
        "prompt_version": profile.prompt_version,
        "preferred_language": profile.languages.preferred_language.value,
        "supported_languages": [lang.value for lang in profile.languages.supported_languages],
        "auto_detect": profile.languages.auto_detect,
        "transfer_enabled": profile.transfer_rules.enabled,
        "recording_enabled": profile.recording.recording_enabled,
        "transcription_enabled": profile.recording.transcription_enabled,
        "retention_days": profile.recording.retention_days,
    }
