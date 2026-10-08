"""AI tool definitions (contracts only — no execution)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ToolName(StrEnum):
    GET_CONTACT = "get_contact"
    SEARCH_CONTACTS = "search_contacts"
    SEARCH_KNOWLEDGE = "search_knowledge"
    GET_OWNER_AVAILABILITY = "get_owner_availability"
    CREATE_CALENDAR_EVENT = "create_calendar_event"
    REQUEST_CALLBACK = "request_callback"
    TAKE_MESSAGE = "take_message"
    SEND_NOTIFICATION = "send_notification"
    TRANSFER_CALL = "transfer_call"
    END_CALL = "end_call"


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    name: ToolName
    description: str
    input_schema: dict[str, Any]
    requires_confirmation: bool = False
    sensitive: bool = False


TOOL_CATALOG: dict[ToolName, ToolDefinition] = {
    ToolName.GET_CONTACT: ToolDefinition(
        name=ToolName.GET_CONTACT,
        description="Get a contact by phone or id",
        input_schema={
            "type": "object",
            "properties": {"phone": {"type": "string"}, "contact_id": {"type": "string"}},
        },
    ),
    ToolName.SEARCH_CONTACTS: ToolDefinition(
        name=ToolName.SEARCH_CONTACTS,
        description="Search contacts by name or company",
        input_schema={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    ),
    ToolName.SEARCH_KNOWLEDGE: ToolDefinition(
        name=ToolName.SEARCH_KNOWLEDGE,
        description="Search approved knowledge base",
        input_schema={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    ),
    ToolName.GET_OWNER_AVAILABILITY: ToolDefinition(
        name=ToolName.GET_OWNER_AVAILABILITY,
        description="Check Uday's calendar availability",
        input_schema={
            "type": "object",
            "properties": {
                "start": {"type": "string"},
                "end": {"type": "string"},
            },
            "required": ["start", "end"],
        },
    ),
    ToolName.CREATE_CALENDAR_EVENT: ToolDefinition(
        name=ToolName.CREATE_CALENDAR_EVENT,
        description="Create a calendar event after caller confirmation",
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "start": {"type": "string"},
                "end": {"type": "string"},
                "caller_confirmed": {"type": "boolean"},
            },
            "required": ["title", "start", "end", "caller_confirmed"],
        },
        requires_confirmation=True,
        sensitive=True,
    ),
    ToolName.REQUEST_CALLBACK: ToolDefinition(
        name=ToolName.REQUEST_CALLBACK,
        description="Create a callback request for Uday",
        input_schema={
            "type": "object",
            "properties": {"note": {"type": "string"}, "preferred_time": {"type": "string"}},
            "required": ["note"],
        },
    ),
    ToolName.TAKE_MESSAGE: ToolDefinition(
        name=ToolName.TAKE_MESSAGE,
        description="Take a message for Uday",
        input_schema={
            "type": "object",
            "properties": {"message": {"type": "string"}},
            "required": ["message"],
        },
    ),
    ToolName.SEND_NOTIFICATION: ToolDefinition(
        name=ToolName.SEND_NOTIFICATION,
        description="Notify Uday about an important event",
        input_schema={
            "type": "object",
            "properties": {"subject": {"type": "string"}, "body": {"type": "string"}},
            "required": ["subject", "body"],
        },
        sensitive=True,
    ),
    ToolName.TRANSFER_CALL: ToolDefinition(
        name=ToolName.TRANSFER_CALL,
        description="Transfer the call to Uday per transfer rules",
        input_schema={
            "type": "object",
            "properties": {
                "reason": {"type": "string"},
                "caller_confirmed": {"type": "boolean"},
            },
            "required": ["reason", "caller_confirmed"],
        },
        requires_confirmation=True,
        sensitive=True,
    ),
    ToolName.END_CALL: ToolDefinition(
        name=ToolName.END_CALL,
        description="Politely end the call",
        input_schema={
            "type": "object",
            "properties": {"reason": {"type": "string"}},
        },
    ),
}
