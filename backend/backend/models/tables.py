import enum
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, Column, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, ENUM
from sqlmodel import Field, Relationship, SQLModel


### Link (join) tables
class UserOrderLink(SQLModel, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True, ondelete="CASCADE")
    order_id: int | None = Field(default=None, foreign_key="order.id", primary_key=True, ondelete="CASCADE")


class UserProviderLink(SQLModel, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True, ondelete="CASCADE")
    provider_id: int | None = Field(default=None, foreign_key="provider.id", primary_key=True, ondelete="CASCADE")


class OrderProviderLink(SQLModel, table=True):
    order_id: int | None = Field(default=None, foreign_key="order.id", primary_key=True, ondelete="CASCADE")
    provider_id: int | None = Field(default=None, foreign_key="provider.id", primary_key=True, ondelete="CASCADE")


### Order
class OrderStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    ON_HOLD = "on_hold"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class OrderBase(SQLModel):
    external_ref: str = Field(nullable=False)
    project_ref: str = Field(nullable=False)
    status: OrderStatus = Field(default=OrderStatus.SUBMITTED, nullable=False)
    config: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    platforms: list[str] = Field(sa_column=Column(ARRAY(String()), nullable=False))
    resource_ref: str = Field(nullable=False)
    resource_type: str = Field(nullable=False)
    resource_name: str = Field(nullable=False)


class OrderPublic(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime


class OrderCreateAPI(OrderBase):
    provider_pids: list[str] = Field(min_length=1)
    owner_email: str = Field(regex=r"^\S+@\S+\.\S+$")


class OrderPublicWithDetails(OrderPublic):
    providers: list["ProviderPublic"] = []
    users: list["UserPublic"] = []


class Order(OrderBase, table=True):
    __table_args__ = (UniqueConstraint("project_ref", "external_ref", name="uq_order_project_external_ref"),)

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    synced: bool = Field(default=True, nullable=False)

    messages: list["Message"] = Relationship(back_populates="order", cascade_delete=True)
    users: list["User"] = Relationship(back_populates="orders", link_model=UserOrderLink)
    providers: list["Provider"] = Relationship(back_populates="orders", link_model=OrderProviderLink)
    logs: list["OrderLog"] = Relationship(back_populates="order", cascade_delete=True)


### User
class UserType(str, enum.Enum):
    MP_USER = "mp_user"
    PROVIDER_MANAGER = "provider_manager"
    COORDINATOR = "coordinator"
    ADMIN = "admin"


class UserBase(SQLModel):
    name: str = Field(nullable=False, min_length=1)
    email: str = Field(nullable=False, unique=True, regex=r"^\S+@\S+\.\S+$")
    user_type: list[UserType] = Field(sa_column=Column(ARRAY(ENUM(UserType)), nullable=False), min_length=1)

    def is_admin(self) -> bool:
        return UserType.ADMIN in self.user_type

    def is_coordinator(self) -> bool:
        return UserType.COORDINATOR in self.user_type

    def is_provider_manager(self) -> bool:
        return UserType.PROVIDER_MANAGER in self.user_type


class UserPublic(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


class UserCreate(UserBase):
    pass


class UserPublicWithEmployers(UserPublic):
    employers: list["ProviderPublic"] = []


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

    messages: list["Message"] = Relationship(back_populates="author", cascade_delete=True)
    orders: list[Order] = Relationship(back_populates="users", link_model=UserOrderLink)
    employers: list["Provider"] = Relationship(back_populates="managers", link_model=UserProviderLink)
    order_logs: list["OrderLog"] = Relationship(back_populates="author", cascade_delete=True)

    def _has_access_override(self) -> bool:
        return self.is_admin() or self.is_coordinator()

    def has_access_to_order(self, order: Order) -> bool:
        return self._has_access_override() or (self.is_provider_manager() and order in self.orders)

    def has_access_to_provider(self, provider: "Provider") -> bool:
        # NOTE: if provider is user's employer that automatically means that user is provider's manager
        return self._has_access_override() or (self.is_provider_manager() and provider in self.employers)

    def has_access_to_other_user(self, target_user: "User") -> bool:
        return self._has_access_override() or self.id == target_user.id

    def __hash__(self) -> int:
        return hash(self.email)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, User) and self.email == other.email


class OrderLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

    order_id: int | None = Field(default=None, foreign_key="order.id", nullable=False, ondelete="CASCADE")
    order: Order | None = Relationship(back_populates="logs")
    status_from: OrderStatus = Field(nullable=False)
    status_to: OrderStatus = Field(nullable=False)
    author_id: int = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    author: User | None = Relationship(back_populates="order_logs")


### Message
class MessageScope(str, enum.Enum):
    PRIVATE = "private"
    PUBLIC = "public"


class MessageBase(SQLModel):
    content: str = Field(min_length=1, nullable=False)
    scope: MessageScope = Field(sa_column=Column(ENUM(MessageScope), nullable=False), default=MessageScope.PRIVATE)


class MessagePublic(MessageBase):
    id: int
    created_at: datetime

    author: UserPublic
    order: OrderPublic


class MessageCreate(MessageBase):
    order_id: int


class MessageCreateAPI(MessageBase):
    user_email: str
    order_external_ref: str


class Message(MessageBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    synced: bool = Field(default=True, nullable=False)

    author_id: int | None = Field(default=None, foreign_key="user.id", ondelete="CASCADE")
    author: User | None = Relationship(back_populates="messages")

    order_id: int | None = Field(default=None, foreign_key="order.id", ondelete="CASCADE")
    order: Order | None = Relationship(back_populates="messages")


### Provider
class ProviderBase(SQLModel):
    name: str = Field(nullable=False, min_length=1, unique=True)
    website: str = Field(nullable=False, min_length=1)
    pid: str = Field(nullable=False, unique=True, min_length=1)


class ProviderCreateAPI(ProviderBase):
    manager_emails: list[str] = Field(min_length=1)


class ProviderPublic(ProviderBase):
    id: int
    created_at: datetime


class ProviderPublicWithDetails(ProviderPublic):
    managers: list[UserPublic] = []
    orders: list[OrderPublic] = []


class Provider(ProviderBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

    managers: list[User] = Relationship(back_populates="employers", link_model=UserProviderLink)
    orders: list[Order] = Relationship(back_populates="providers", link_model=OrderProviderLink)


class NotifiableType(str, enum.Enum):
    ORDER_LOG = "order_log"
    MESSAGE = "message"


class NotificationBase(SQLModel):
    content: str = Field(nullable=False)
    email_delivered: bool = Field(default=False, nullable=False)


class Notification(NotificationBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

    recipient_id: int | None = Field(default=None, foreign_key="user.id", nullable=False, ondelete="CASCADE")
    notifiable_id: int | None = Field(default=None, nullable=False)
    notifiable_type: NotifiableType = Field(sa_column=Column(ENUM(NotifiableType), nullable=False))
