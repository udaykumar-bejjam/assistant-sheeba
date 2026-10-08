"""Domain and application exception hierarchy."""

from __future__ import annotations


class DomainError(Exception):
    """Base for all domain/application failures."""

    code: str = "domain_error"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code
        self.message = message


class ValidationError(DomainError):
    code = "validation_error"


class NotFoundError(DomainError):
    code = "not_found"


class CallNotFoundError(NotFoundError):
    code = "call_not_found"


class ContactNotFoundError(NotFoundError):
    code = "contact_not_found"


class InvalidStateTransitionError(DomainError):
    code = "invalid_state_transition"


class UnauthorizedToolError(DomainError):
    code = "unauthorized_tool"


class ProviderUnavailableError(DomainError):
    code = "provider_unavailable"


class AIProviderError(ProviderUnavailableError):
    code = "ai_provider_error"


class CalendarProviderError(ProviderUnavailableError):
    code = "calendar_provider_error"


class TelephonyProviderError(ProviderUnavailableError):
    code = "telephony_provider_error"


class TransferFailedError(DomainError):
    code = "transfer_failed"


class WebhookAuthenticationError(DomainError):
    code = "webhook_auth_failed"


class IdentityViolationError(DomainError):
    """Raised when an action would violate assistant identity rules."""

    code = "identity_violation"
