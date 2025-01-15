from config import get_settings
from sqlmodel import Session, create_engine, delete

from app.models.tables import Message, Order, User, UserOrderLink, UserProviderLink, OrderProviderLink, Provider

if __name__ == "__main__":
    engine = create_engine(get_settings().db_connection_string)

    with Session(engine) as session:
        session.exec(delete(UserOrderLink))
        session.exec(delete(UserProviderLink))
        session.exec(delete(OrderProviderLink))
        session.exec(delete(Provider))
        session.exec(delete(User))
        session.exec(delete(Order))
        session.exec(delete(Message))
        session.commit()
