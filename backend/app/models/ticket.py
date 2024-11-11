from enum import Enum
from typing import Optional

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


# Marketplace ref: Jira::Client#map_to_jira_order_type
class OfferType(Enum):
    EXTERNAL = "external"
    ORDERABLE = "orderable"
    OPEN_ACCESS = "open_access"


class TicketBase(SQLModel):

    # Marketplace ref: Jira::Client#create_service_issue
    #  Skipping JIRA specific fields like EPIC or project
    summary: str
    order_reference: str
    platforms: list[str] = Field(sa_column=sa.Column(sa.ARRAY(sa.String)))
    i_need_a_voucher: bool
    voucher_id: Optional[str]
    category: Optional[str]
    service: str
    offer: str
    # attributes: dict[str, str] ???
    # service_order_target: Optional[str] ???
    offer_type: str


class Ticket(TicketBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class TicketCreate(TicketBase):
    pass


class TicketPublic(TicketBase):
    id: int
