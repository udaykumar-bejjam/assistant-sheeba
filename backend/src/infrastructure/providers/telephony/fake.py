"""Fake telephony provider with explicit capability flags."""

from __future__ import annotations

from src.shared.application.ports import CallDetails, TelephonyCapabilities
from src.shared.domain.errors import TelephonyProviderError


class FakeTelephonyProvider:
    """In-memory telephony for local/dev/CI.

    Capabilities: answer/reject/hangup yes; warm transfer no (documented).
    """

    capabilities = TelephonyCapabilities(
        answer=True,
        reject=True,
        hangup=True,
        cold_transfer=True,
        warm_transfer=False,
        bidirectional_audio_stream=False,
        recording=False,
    )

    def __init__(self) -> None:
        self.answered: set[str] = set()
        self.rejected: set[str] = set()
        self.hung_up: set[str] = set()
        self.transferred: dict[str, str] = {}
        self.details: dict[str, CallDetails] = {}

    async def answer_call(self, provider_call_id: str) -> None:
        self.answered.add(provider_call_id)

    async def reject_call(self, provider_call_id: str) -> None:
        self.rejected.add(provider_call_id)

    async def hangup_call(self, provider_call_id: str) -> None:
        self.hung_up.add(provider_call_id)

    async def transfer_call(self, provider_call_id: str, destination: str) -> None:
        if not self.capabilities.cold_transfer and not self.capabilities.warm_transfer:
            raise TelephonyProviderError("Transfer not supported by this provider")
        self.transferred[provider_call_id] = destination

    async def start_audio_stream(self, provider_call_id: str) -> None:
        if not self.capabilities.bidirectional_audio_stream:
            raise TelephonyProviderError(
                "Bidirectional audio streaming not supported by FakeTelephonyProvider"
            )

    async def stop_audio_stream(self, provider_call_id: str) -> None:
        return None

    async def get_call_details(self, provider_call_id: str) -> CallDetails:
        if provider_call_id in self.details:
            return self.details[provider_call_id]
        return CallDetails(
            provider_call_id=provider_call_id,
            from_number="unknown",
            to_number="unknown",
            status="in-progress" if provider_call_id in self.answered else "ringing",
        )
