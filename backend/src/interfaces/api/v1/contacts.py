from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from src.contacts.domain.contact import Contact, ContactCategory
from src.infrastructure.container import AppContainer
from src.interfaces.api.deps import get_container
from src.shared.domain.errors import DomainError, ValidationError
from src.shared.domain.value_objects import CallPriority, PhoneNumber

router = APIRouter()


class CreateContactRequest(BaseModel):
    name: str = Field(min_length=1)
    phone: str
    company: str | None = None
    category: ContactCategory = ContactCategory.UNKNOWN
    is_trusted: bool = False
    priority: CallPriority = CallPriority.MEDIUM


def _container(request: Request) -> AppContainer:
    return get_container(request)


@router.get("")
async def list_contacts(container: AppContainer = Depends(_container)) -> dict[str, object]:
    items = await container.contacts.list_all()
    return {
        "items": [
            {
                "id": str(c.id),
                "name": c.name,
                "phones": [str(p) for p in c.phone_numbers],
                "company": c.company,
                "category": c.category.value,
                "is_trusted": c.is_trusted,
                "is_blocked": c.is_blocked,
                "priority": c.priority.value,
            }
            for c in items
        ]
    }


@router.post("")
async def create_contact(
    body: CreateContactRequest,
    container: AppContainer = Depends(_container),
) -> dict[str, object]:
    try:
        contact = Contact.create(
            name=body.name,
            phone=PhoneNumber(body.phone),
            company=body.company,
            category=body.category,
            is_trusted=body.is_trusted,
            priority=body.priority,
        )
        await container.contacts.save(contact)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    except DomainError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc
    return {"id": str(contact.id), "name": contact.name}
