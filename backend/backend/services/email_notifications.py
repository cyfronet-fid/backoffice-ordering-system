import logging
import smtplib
from email.message import EmailMessage

from backend.config import get_settings
from backend.db import get_session
from backend.models.tables import Message, NotifiableType, Notification, Order, OrderStatus, User
from backend.services.email_helper import STATUS_NOTIFICATION_MAP
from backend.utils import _role_label

logger = logging.getLogger(__name__)


def _send_email(subject: str, body: str, recipients: list[str]) -> bool:
    if not recipients:
        logger.info("No recipients provided for email with subject '%s'; skipping send.", subject)
        return False

    settings = get_settings()

    if not settings.smtp_host:
        logger.warning(
            "SMTP host not configured - skipping email send for subject '%s' to %s",
            subject,
            recipients,
        )
        return False

    sender = settings.smtp_user
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            if settings.smtp_starttls:
                smtp.starttls()

            smtp.login(settings.smtp_user, settings.smtp_password)  # type: ignore

            smtp.send_message(message)
            logger.info("Sent email '%s' to %s", subject, recipients)
            return True
    except smtplib.SMTPException:
        logger.exception("Failed to send email '%s' to %s", subject, recipients)
        return False


def _send_and_record(
    *,
    subject: str,
    body: str,
    recipient: User,
    notifiable_id: int,
    notifiable_type: NotifiableType,
) -> Notification:
    sent = _send_email(subject=subject, body=body, recipients=[recipient.email])
    return Notification(
        recipient_id=recipient.id,
        content=body,
        notifiable_id=notifiable_id,
        notifiable_type=notifiable_type,
        email_delivered=sent,
    )


# pylint: disable=too-many-locals
def send_order_message_notification(message_id: int, recipients: list[User]) -> None:
    with get_session() as session:
        db_message = session.get(Message, message_id)
        if db_message is None or db_message.order is None:
            logger.warning("Message %s or related order not found; skipping notification.", message_id)
            return

        order: Order = db_message.order

        settings = get_settings()
        platform_name = settings.platform_name
        order_link = f"{settings.frontend_url}/orders/{order.id}"
        resource_name = order.resource_name
        message_content = db_message.content
        author_name = db_message.author.name  # type: ignore[union-attr]

        notifications: list[Notification] = []
        for recipient in recipients:
            recipient_role = _role_label(recipient)
            subject = f"New message from {author_name} - order {order.id}, {resource_name}"
            body = (
                f"Dear {recipient_role},\n\n"
                f"You've received a new message from {author_name} regarding offer {resource_name}.\n\n"
                f"Order ID: {order.id}\n"
                f"Message content:\n"
                f"{message_content}\n\n"
                f"To view and reply, go to your account: {order_link}\n\n"
                f"Best regards,\n"
                "Operations Team\n"
                f"{platform_name}"
            )
            sent = _send_email(subject=subject, body=body, recipients=[recipient.email])

            notifications.append(
                Notification(
                    recipient_id=recipient.id,
                    content=body,
                    notifiable_id=message_id,
                    notifiable_type=NotifiableType.MESSAGE,
                    email_delivered=sent,
                )
            )

        session.add_all(notifications)
        session.commit()


def send_order_status_change_notification(
    order_id: int,
    status_to: OrderStatus,
    users: dict[str, list[User]],
    order_log_id: int,
) -> None:
    with get_session() as session:
        order = session.get(Order, order_id)
        if order is None:
            logger.warning("Order %s not found; skipping status change notification.", order_id)
            return

        settings = get_settings()
        provider_names = ", ".join(provider.name for provider in order.providers) or "the provider"
        author_names = ", ".join(user.name for user in order.users)

        entry = STATUS_NOTIFICATION_MAP.get(status_to)
        if entry is None:
            return

        email_builder, recipient_groups = entry
        ctx = {
            "offer_name": order.resource_name,
            "provider_names": provider_names,
            "marketplace_order_link": f"{settings.whitelabel_endpoint}/projects/{order.external_ref}/services",
            "order_id": order.id,
            "order_link": f"{settings.frontend_url}/orders/{order.id}",
            "author_names": author_names,
            "platform_name": settings.platform_name,
            "role": "",  # filled per-recipient
        }

        notifications = []
        for group in recipient_groups:
            for recipient in users.get(group, []):
                ctx["role"] = _role_label(recipient)
                subject, body = email_builder(ctx)
                notifications.append(
                    _send_and_record(
                        subject=subject,
                        body=body,
                        recipient=recipient,
                        notifiable_id=order_log_id,
                        notifiable_type=NotifiableType.ORDER_LOG,
                    )
                )

            session.add_all(notifications)
            session.commit()
