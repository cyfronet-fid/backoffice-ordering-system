from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from smtplib import SMTPException
from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pytest

from backend.models.tables import (
    Message,
    MessageScope,
    NotifiableType,
    Notification,
    Order,
    OrderLog,
    OrderStatus,
    Provider,
    User,
    UserType,
)


@dataclass(frozen=True)
class _FakeSettings:
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = "user@gmail.com"
    smtp_password: str | None = "password"
    smtp_starttls: bool = True
    platform_name: str | None = "BOS"
    frontend_url: str = ""
    whitelabel_endpoint: str = ""


class _FakeSession:
    def __init__(self, *, message: Message | None = None, order: Order | None = None) -> None:
        self._message = message
        self._order = order
        self.added: list[Any] = []
        self.added_all: list[Any] = []
        self.commit_count: int = 0

    def get(self, model: Any, obj_id: int, **kwargs: Any) -> Any | None:  # noqa: ANN401, ARG002
        if model is Message:
            return self._message
        if model is Order:
            return self._order
        return None

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    def add_all(self, objs: list[Any]) -> None:
        self.added_all.extend(objs)

    def commit(self) -> None:
        self.commit_count += 1
        for obj in self.added:
            if isinstance(obj, OrderLog) and obj.id is None:
                obj.id = 55  # type: ignore[assignment]


@contextmanager
def _fake_get_session(session: _FakeSession) -> Generator[_FakeSession, None, None]:
    yield session


def _make_order(order_id: int) -> Order:
    order = Order(
        id=order_id,
        external_ref="10",
        project_ref="20",
        status=OrderStatus.SUBMITTED,
        config={},
        platforms=["web"],
        resource_ref="r",
        resource_type="t",
        resource_name="Offer X",
    )
    order.providers = [Provider(id=1, name="Provider A", website="https://provider.example", pid="p1")]  # type: ignore[assignment]
    order.users = [User(id=99, name="Order Owner", email="owner@example.com", user_type=[UserType.MP_USER])]  # type: ignore[assignment]
    return order


def _make_message(message_id: int, order: Order, author: User) -> Message:
    msg = Message(id=message_id, content="Hello", scope=MessageScope.PUBLIC)
    msg.order = order
    msg.author = author
    return msg


def test__send_email_no_recipients_returns_false():
    from backend.services import email_notifications as en

    assert en._send_email(subject="S", body="B", recipients=[]) is False


def test__send_email_missing_smtp_host_returns_false(monkeypatch):
    from backend.services import email_notifications as en

    monkeypatch.setattr(en, "get_settings", lambda: _FakeSettings(smtp_host=None))
    assert en._send_email(subject="S", body="B", recipients=["a@example.com"]) is False


def test__send_email_success_sends_message_with_starttls(monkeypatch):
    from backend.services import email_notifications as en

    monkeypatch.setattr(en, "get_settings", lambda: _FakeSettings(smtp_host="smtp.example", smtp_starttls=True))

    smtp = MagicMock()
    smtp.__enter__.return_value = smtp

    with patch.object(en.smtplib, "SMTP", return_value=smtp) as _smtp_cls:
        ok = en._send_email(subject="Subject", body="Body", recipients=["a@example.com"])

    assert ok is True
    assert smtp.starttls.called is True
    assert smtp.login.called is True
    assert smtp.send_message.called is True


def test__send_email_exception_returns_false(monkeypatch):
    from backend.services import email_notifications as en

    monkeypatch.setattr(en, "get_settings", lambda: _FakeSettings(smtp_host="smtp.example", smtp_starttls=False))

    smtp = MagicMock()
    smtp.__enter__.return_value = smtp
    smtp.send_message.side_effect = SMTPException("boom")

    with patch.object(en.smtplib, "SMTP", return_value=smtp):
        ok = en._send_email(subject="Subject", body="Body", recipients=["a@example.com"])

    assert ok is False


def test_send_order_message_notification_skips_when_message_missing(monkeypatch):
    from backend.services import email_notifications as en

    session = _FakeSession(message=None)
    monkeypatch.setattr(en, "get_session", lambda: _fake_get_session(session))

    en.send_order_message_notification(message_id=123, recipients=[])

    assert session.added_all == []
    assert session.commit_count == 0


def test_send_order_message_notification_creates_notifications_for_recipients(monkeypatch):
    from backend.services import email_notifications as en

    order = _make_order(1)
    author = User(id=5, name="Alice", email="alice@example.com", user_type=[UserType.MP_USER])
    msg = _make_message(10, order=order, author=author)
    session = _FakeSession(message=msg)

    monkeypatch.setattr(en, "get_session", lambda: _fake_get_session(session))
    monkeypatch.setattr(en, "get_settings", lambda: _FakeSettings(platform_name="BOS"))

    sent_calls: list[dict[str, Any]] = []

    def _fake_send_email(*, subject: str, body: str, recipients: list[str]) -> bool:
        sent_calls.append({"subject": subject, "body": body, "recipients": recipients})
        return recipients[0] != "fail@example.com"

    monkeypatch.setattr(en, "_send_email", _fake_send_email)

    recipients = [
        User(id=1, name="C", email="c@example.com", user_type=[UserType.COORDINATOR]),
        User(id=2, name="P", email="p@example.com", user_type=[UserType.PROVIDER_MANAGER]),
        User(id=3, name="U", email="fail@example.com", user_type=[UserType.MP_USER]),
    ]

    en.send_order_message_notification(message_id=10, recipients=recipients)

    assert "Order ID: 1" in sent_calls[0]["body"]
    assert "Hello" in sent_calls[0]["body"]
    assert "Alice" in sent_calls[0]["body"]
    assert "BOS" in sent_calls[0]["body"]
    assert session.commit_count == 1
    assert len(session.added_all) == 3
    assert all(isinstance(n, Notification) for n in session.added_all)
    assert {n.notifiable_type for n in session.added_all} == {NotifiableType.MESSAGE}
    assert [n.email_delivered for n in session.added_all] == [True, True, False]
    assert "New message from Alice" in sent_calls[0]["subject"]


def test_send_order_status_change_notification_skips_when_order_missing(monkeypatch):
    from backend.services import email_notifications as en

    session = _FakeSession(order=None)
    monkeypatch.setattr(en, "get_session", lambda: _fake_get_session(session))

    en.send_order_status_change_notification(
        order_id=1,
        status_to=OrderStatus.ON_HOLD,
        users={"mp_user": [], "provider_manager": [], "coordinator": []},
        order_log_id=1,
    )

    assert session.added == []
    assert session.added_all == []


@pytest.mark.parametrize(
    "status_to, recipients_key, subject_contains",
    [
        (OrderStatus.ON_HOLD, "mp_user", "is on hold"),
        (OrderStatus.COMPLETED, "mp_user", "was successfully processed"),
        (OrderStatus.REJECTED, "mp_user", "has been rejected"),
    ],
)
def test_send_order_status_change_notification_creates_order_log_and_notifications(
    status_to: OrderStatus, recipients_key: str, subject_contains: str, monkeypatch
):
    from backend.services import email_notifications as en

    order = _make_order(1)
    session = _FakeSession(order=order)
    monkeypatch.setattr(en, "get_session", lambda: _fake_get_session(session))
    monkeypatch.setattr(en, "get_settings", lambda: _FakeSettings(platform_name="BOS"))

    sent_calls = []

    def fake_send_email(**kwargs):
        sent_calls.append(kwargs)
        return True

    monkeypatch.setattr(en, "_send_email", fake_send_email)

    mp_users = [User(id=10, name="U1", email="u1@example.com", user_type=[UserType.MP_USER])]

    en.send_order_status_change_notification(
        order_id=1,
        status_to=status_to,
        users={"mp_user": mp_users, "provider_manager": [], "coordinator": []},
        order_log_id=1,
    )

    assert len(sent_calls) == len(mp_users)
    call = sent_calls[0]
    assert "subject" in call and "body" in call
    assert subject_contains in call["subject"]
