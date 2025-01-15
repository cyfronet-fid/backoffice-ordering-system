import enum
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import ARRAY, JSON, Column, String
from sqlmodel import Enum, Field, Relationship, SQLModel


class UserOrderLink(SQLModel, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    order_id: int | None = Field(default=None, foreign_key="order.id", primary_key=True)


class UserProviderLink(SQLModel, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    provider_id: int | None = Field(default=None, foreign_key="provider.id", primary_key=True)


class OrderProviderLink(SQLModel, table=True):
    order_id: int | None = Field(default=None, foreign_key="order.id", primary_key=True)
    provider_id: int | None = Field(default=None, foreign_key="provider.id", primary_key=True)


class OrderStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    ON_HOLD = "on_hold"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = datetime.now(tz=timezone.utc)
    updated_at: datetime = datetime.now(tz=timezone.utc)
    external_ref: str = Field(unique=True, nullable=False)
    project_ref: str = Field(nullable=False)
    status: OrderStatus = Field(default=OrderStatus.SUBMITTED, nullable=False)
    config: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    platforms: list[str] = Field(sa_column=Column(ARRAY(String()), nullable=False))
    resource_ref: str = Field(nullable=False)
    resource_type: str = Field(nullable=False)
    resource_name: str = Field(nullable=False)

    messages: list["Message"] = Relationship(back_populates="order", cascade_delete=True)
    users: list["User"] = Relationship(back_populates="orders", link_model=UserOrderLink)
    providers: list["Provider"] = Relationship(back_populates="orders", link_model=OrderProviderLink)


class UserType(str, enum.Enum):
    MP_USER = "mp_user"
    PROVIDER_MANAGER = "provider_manager"
    COORDINATOR = "coordinator"
    ADMIN = "admin"


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = datetime.now(tz=timezone.utc)
    updated_at: datetime = datetime.now(tz=timezone.utc)
    email: str = Field(nullable=False, unique=True, regex=r"^\S+@\S+\.\S+$")
    user_type: list[UserType] = Field(sa_column=Column(ARRAY(Enum(UserType)), nullable=False), min_length=1)

    messages: list["Message"] = Relationship(back_populates="author", cascade_delete=True)
    orders: list[Order] = Relationship(back_populates="users", link_model=UserOrderLink)
    employers: list["Provider"] = Relationship(back_populates="managers", link_model=UserProviderLink)


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = datetime.now(tz=timezone.utc)
    content: str = Field(min_length=1, nullable=False)

    author_id: int | None = Field(default=None, foreign_key="user.id", ondelete="CASCADE")
    author: User | None = Relationship(back_populates="messages")

    order_id: int | None = Field(default=None, foreign_key="order.id", ondelete="CASCADE")
    order: Order | None = Relationship(back_populates="messages")


class Provider(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = datetime.now(tz=timezone.utc)
    name: str = Field(nullable=False, min_length=1)
    website: str = Field(nullable=False, min_length=1)

    managers: list[User] = Relationship(back_populates="employers", link_model=UserProviderLink)
    orders: list[Order] = Relationship(back_populates="providers", link_model=OrderProviderLink)
