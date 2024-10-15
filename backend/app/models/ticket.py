from typing import Optional

from sqlmodel import Field, SQLModel


class TicketBase(SQLModel):
    title: str
    description: str


class Ticket(TicketBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class TicketCreate(TicketBase):
    pass


class TicketPublic(TicketBase):
    id: int
