"""ORM <-> domain mappers."""

from __future__ import annotations

from datetime import time
from typing import Any

from src.assistant.domain.profile import (
    DEFAULT_SYSTEM_PROMPT_V1,
    AssistantProfile,
    CommunicationPreferences,
    IdentityRules,
    LanguagePreferences,
    RecordingPolicy,
    TransferRules,
    WorkingHours,
)
from src.call_management.domain.call import (
    Call,
    CallClassification,
    CallOutcome,
    CallSummary,
)
from src.contacts.domain.contact import Contact, ContactCategory
from src.infrastructure.persistence.orm import AssistantProfileRow, CallRow, ContactRow
from src.shared.domain.value_objects import (
    CallId,
    CallIntent,
    CallPriority,
    CallStatus,
    ContactId,
    ConversationId,
    EmailAddress,
    Language,
    PhoneNumber,
)


def call_to_row(call: Call) -> CallRow:
    return CallRow(
        id=str(call.id),
        provider_call_id=call.provider_call_id,
        caller_phone=str(call.caller_phone),
        caller_name=call.caller_name,
        contact_id=str(call.contact_id) if call.contact_id else None,
        conversation_id=str(call.conversation_id) if call.conversation_id else None,
        status=call.status.value,
        language=call.language.value,
        intent=call.classification.intent.value,
        priority=call.classification.priority.value,
        spam_score=call.classification.spam_score,
        outcome_json={
            "message_taken": call.outcome.message_taken,
            "message_text": call.outcome.message_text,
            "callback_requested": call.outcome.callback_requested,
            "callback_note": call.outcome.callback_note,
            "appointment_requested": call.outcome.appointment_requested,
            "transferred": call.outcome.transferred,
            "transfer_destination": call.outcome.transfer_destination,
            "follow_up_required": call.outcome.follow_up_required,
            "classification_reasons": call.classification.reasons,
        },
        summary_json=call.summary.to_dict() if call.summary else None,
        transcript=call.transcript,
        answered_at=call.answered_at,
        ended_at=call.ended_at,
        created_at=call.created_at,
        updated_at=call.updated_at,
    )


def row_to_call(row: CallRow) -> Call:
    outcome_data: dict[str, Any] = row.outcome_json or {}
    summary = None
    if row.summary_json:
        summary = CallSummary(
            caller_name=row.summary_json.get("caller_name"),
            phone_number=row.summary_json.get("phone_number") or row.caller_phone,
            intent=CallIntent(row.summary_json.get("intent", row.intent)),
            priority=CallPriority(row.summary_json.get("priority", row.priority)),
            summary=row.summary_json.get("summary") or "",
            requested_action=row.summary_json.get("requested_action"),
            callback_requested=bool(row.summary_json.get("callback_requested")),
            appointment_requested=bool(row.summary_json.get("appointment_requested")),
            transferred=bool(row.summary_json.get("transferred")),
            follow_up_required=bool(row.summary_json.get("follow_up_required")),
        )
    return Call(
        id=CallId(row.id),
        caller_phone=PhoneNumber(row.caller_phone),
        status=CallStatus(row.status),
        provider_call_id=row.provider_call_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        contact_id=ContactId(row.contact_id) if row.contact_id else None,
        caller_name=row.caller_name,
        conversation_id=ConversationId(row.conversation_id) if row.conversation_id else None,
        language=Language(row.language),
        classification=CallClassification(
            intent=CallIntent(row.intent),
            priority=CallPriority(row.priority),
            spam_score=row.spam_score,
            reasons=list(outcome_data.get("classification_reasons") or []),
        ),
        outcome=CallOutcome(
            message_taken=bool(outcome_data.get("message_taken")),
            message_text=outcome_data.get("message_text"),
            callback_requested=bool(outcome_data.get("callback_requested")),
            callback_note=outcome_data.get("callback_note"),
            appointment_requested=bool(outcome_data.get("appointment_requested")),
            transferred=bool(outcome_data.get("transferred")),
            transfer_destination=outcome_data.get("transfer_destination"),
            follow_up_required=bool(outcome_data.get("follow_up_required")),
        ),
        summary=summary,
        transcript=row.transcript,
        answered_at=row.answered_at,
        ended_at=row.ended_at,
    )


def contact_to_row(contact: Contact) -> ContactRow:
    return ContactRow(
        id=str(contact.id),
        name=contact.name,
        phone_numbers_json=[str(p) for p in contact.phone_numbers],
        email=str(contact.email) if contact.email else None,
        company=contact.company,
        relationship=contact.relationship,
        category=contact.category.value,
        priority=contact.priority.value,
        notes=contact.notes,
        is_trusted=contact.is_trusted,
        is_blocked=contact.is_blocked,
        created_at=contact.created_at,
        updated_at=contact.updated_at,
    )


def row_to_contact(row: ContactRow) -> Contact:
    return Contact(
        id=ContactId(row.id),
        name=row.name,
        phone_numbers=[PhoneNumber(p) for p in row.phone_numbers_json],
        email=EmailAddress(row.email) if row.email else None,
        company=row.company,
        relationship=row.relationship,
        category=ContactCategory(row.category),
        priority=CallPriority(row.priority),
        notes=row.notes,
        is_trusted=row.is_trusted,
        is_blocked=row.is_blocked,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def profile_to_row(profile: AssistantProfile) -> AssistantProfileRow:
    return AssistantProfileRow(
        id=profile.id,
        config_json={
            "identity": {
                "assistant_name": profile.identity.assistant_name,
                "owner_name": profile.identity.owner_name,
                "greeting": profile.identity.greeting,
                "must_disclose_ai": profile.identity.must_disclose_ai,
                "never_impersonate_owner": profile.identity.never_impersonate_owner,
            },
            "communication": {
                "tone": profile.communication.tone,
                "max_response_seconds": profile.communication.max_response_seconds,
            },
            "working_hours": {
                "timezone": profile.working_hours.timezone,
                "start": profile.working_hours.start.isoformat(),
                "end": profile.working_hours.end.isoformat(),
                "days": profile.working_hours.days,
            },
            "transfer_rules": {
                "enabled": profile.transfer_rules.enabled,
                "require_caller_confirmation": profile.transfer_rules.require_caller_confirmation,
                "allow_for_trusted_contacts": profile.transfer_rules.allow_for_trusted_contacts,
                "allow_for_urgent": profile.transfer_rules.allow_for_urgent,
                "owner_phone": profile.transfer_rules.owner_phone,
                "business_hours_only": profile.transfer_rules.business_hours_only,
            },
            "languages": {
                "preferred_language": profile.languages.preferred_language.value,
                "supported_languages": [
                    lang.value for lang in profile.languages.supported_languages
                ],
                "auto_detect": profile.languages.auto_detect,
            },
            "recording": {
                "recording_enabled": profile.recording.recording_enabled,
                "transcription_enabled": profile.recording.transcription_enabled,
                "retention_days": profile.recording.retention_days,
                "announce_recording": profile.recording.announce_recording,
            },
        },
        system_prompt=profile.system_prompt,
        prompt_version=profile.prompt_version,
        updated_at=profile.updated_at,
    )


def row_to_profile(row: AssistantProfileRow) -> AssistantProfile:
    cfg = row.config_json or {}
    identity = cfg.get("identity") or {}
    communication = cfg.get("communication") or {}
    working = cfg.get("working_hours") or {}
    transfer = cfg.get("transfer_rules") or {}
    languages = cfg.get("languages") or {}
    recording = cfg.get("recording") or {}

    def _parse_time(value: str | None, default: time) -> time:
        if not value:
            return default
        hour, minute, *rest = [int(x) for x in value.split(":")]
        return time(hour, minute, rest[0] if rest else 0)

    return AssistantProfile(
        id=row.id,
        identity=IdentityRules(
            assistant_name=identity.get("assistant_name", "Sheeba"),
            owner_name=identity.get("owner_name", "Uday"),
            greeting=identity.get("greeting", "Hi, I'm Uday's AI assistant."),
            must_disclose_ai=bool(identity.get("must_disclose_ai", True)),
            never_impersonate_owner=bool(identity.get("never_impersonate_owner", True)),
        ),
        communication=CommunicationPreferences(
            tone=communication.get("tone", "polite_concise"),
            max_response_seconds=int(communication.get("max_response_seconds", 20)),
        ),
        working_hours=WorkingHours(
            timezone=working.get("timezone", "Asia/Kolkata"),
            start=_parse_time(working.get("start"), time(9, 0)),
            end=_parse_time(working.get("end"), time(21, 0)),
            days=list(working.get("days") or [0, 1, 2, 3, 4, 5, 6]),
        ),
        transfer_rules=TransferRules(
            enabled=bool(transfer.get("enabled", True)),
            require_caller_confirmation=bool(transfer.get("require_caller_confirmation", True)),
            allow_for_trusted_contacts=bool(transfer.get("allow_for_trusted_contacts", True)),
            allow_for_urgent=bool(transfer.get("allow_for_urgent", True)),
            owner_phone=transfer.get("owner_phone"),
            business_hours_only=bool(transfer.get("business_hours_only", False)),
        ),
        languages=LanguagePreferences(
            preferred_language=Language(languages.get("preferred_language", "EN")),
            supported_languages=[
                Language(x) for x in languages.get("supported_languages", ["EN", "TE", "HI_EN"])
            ],
            auto_detect=bool(languages.get("auto_detect", True)),
        ),
        recording=RecordingPolicy(
            recording_enabled=bool(recording.get("recording_enabled", False)),
            transcription_enabled=bool(recording.get("transcription_enabled", True)),
            retention_days=int(recording.get("retention_days", 30)),
            announce_recording=bool(recording.get("announce_recording", True)),
        ),
        system_prompt=row.system_prompt or DEFAULT_SYSTEM_PROMPT_V1,
        prompt_version=row.prompt_version,
        updated_at=row.updated_at,
    )
