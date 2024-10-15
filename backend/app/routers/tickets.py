from fastapi import APIRouter
from sqlmodel import select

from app.dependencies import SessionDep
from app.models import Ticket, TicketCreate, TicketPublic

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)


@router.get("/", response_model=list[TicketPublic])
def read_tickets(session: SessionDep):  # type: ignore
    return session.exec(select(Ticket)).all()


@router.post("/", response_model=TicketPublic)
def create_ticket(session: SessionDep, ticket: TicketCreate):  # type: ignore
    db_ticket = Ticket.model_validate(ticket)
    session.add(db_ticket)
    session.commit()
    session.refresh(db_ticket)
    return db_ticket
