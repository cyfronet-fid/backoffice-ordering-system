import logging
import smtplib
from email.message import EmailMessage

from backend.config import get_settings
from backend.db import get_session
from backend.models.tables import Message, NotifiableType, Notification, Order, OrderLog, OrderStatus, User

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

            smtp.login(settings.smtp_user, settings.smtp_password)

            smtp.send_message(message)
            logger.info("Sent email '%s' to %s", subject, recipients)
            return True
    except Exception:
        logger.exception("Failed to send email '%s' to %s", subject, recipients)
        return False


def send_order_message_notification(message_id: int, recipients: list[User]) -> None:
    with get_session() as session:
        logging.debug(f"\t\tSession: {session}")
        db_message = session.get(Message, message_id)
        if db_message is None or db_message.order is None:
            logger.warning("Message %s or related order not found; skipping notification.", message_id)
            return

        order: Order = db_message.order

        settings = get_settings()
        platform_name = settings.platform_name
        order_id = order.id
        order_link = f"https://bos.eosc.pl/orders/{order_id}"
        resource_name = order.resource_name
        message_content = db_message.content
        author_name = db_message.author.name

        notifications: list[Notification] = []
        for recipient in recipients:
            if recipient.is_coordinator():
                recipient_role = "Coordinator"
            elif recipient.is_provider_manager():
                recipient_role = "Provider"
            else:
                recipient_role = "User"
            subject = f"New message from {author_name} - order {order_id}, {resource_name}"
            body = (
                f"Dear {recipient_role},\n\n"
                f"You've received a new message from {author_name} regarding offer {resource_name}.\n\n"
                f"Order ID: {order_id}\n"
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
    status_from: OrderStatus,
    status_to: OrderStatus,
    users: dict[str, list[User]],
    status_change_author: User,
) -> None:
    with get_session() as session:
        order = session.get(Order, order_id)
        if order is None:
            logger.warning("Order %s not found; skipping status change notification.", order_id)
            return

        settings = get_settings()
        platform_name = settings.platform_name

        offer_name = order.resource_name
        provider_names = ", ".join(provider.name for provider in order.providers) or "the provider"
        provider_link = "".join(p.website for p in order.providers)
        order_id = order.id
        order_name = order.resource_name  # offer name
        author_name = "".join(user.name for user in order.users)

        order_log = OrderLog(
            order_id=order_id, status_from=status_from, status_to=status_to, author_id=status_change_author.id
        )
        session.add(order_log)
        session.commit()

        if status_to == OrderStatus.ON_HOLD:
            subject = f"Your order for {offer_name} is on hold"
            body = (
                f"Dear User,\n\n"
                f"Your order {order_name} from {provider_names} is currently on hold. This means processing has been temporarily paused.\n\n"
                "We'll let you know once it resumes.\n\n"
                f"If you need more details about the on hold status, contact the provider here: {provider_link}\n\n"
                "Best regards,\n"
                "Operations Team\n"
                f"{platform_name}"
            )
            recipients = users["mp_user"]

            notifications: list[Notification] = []
            for recipient in recipients:
                sent = _send_email(subject=subject, body=body, recipients=[recipient.email])

                notifications.append(
                    Notification(
                        recipient_id=recipient.id,
                        content=body,
                        notifiable_id=order_log.id,
                        notifiable_type=NotifiableType.ORDER_LOG,
                        email_delivered=sent,
                    )
                )
            session.add_all(notifications)
            session.commit()

        if status_to == OrderStatus.COMPLETED:
            subject = f"Your order for {offer_name} was successfully completed"
            body = (
                f"Dear User,\n\n"
                f"Your order {order_name} from {provider_names} has been successfully processed.\n\n"
                f"You can view the order details and access information here: {provider_link}\n\n"
                f"If you need help with the next steps, you can ask the provider here: {provider_link}\n\n"
                "Best regards,\n"
                "Operations Team\n"
                f"{platform_name}"
            )
            recipients = users["mp_user"]

            notifications: list[Notification] = []
            for recipient in recipients:
                sent = _send_email(subject=subject, body=body, recipients=[recipient.email])

                notifications.append(
                    Notification(
                        recipient_id=recipient.id,
                        content=body,
                        notifiable_id=order_log.id,
                        notifiable_type=NotifiableType.ORDER_LOG,
                        email_delivered=sent,
                    )
                )
            session.add_all(notifications)
            session.commit()

        if status_to == OrderStatus.REJECTED:
            subject = f"Your order for {offer_name} has been rejected"
            body = (
                f"Dear User,\n\n"
                f"We regret to inform you that your order {order_name} from {provider_names} has been rejected.\n\n"
                f"If you need more details about the reason for rejection, you can contact the provider here: {provider_link}\n\n"
                "Best regards,\n"
                "Operations Team\n"
                f"{platform_name}"
            )
            recipients = users["mp_user"]

            notifications: list[Notification] = []
            for recipient in recipients:
                sent = _send_email(subject=subject, body=body, recipients=[recipient.email])

                notifications.append(
                    Notification(
                        recipient_id=recipient.id,
                        content=body,
                        notifiable_id=order_log.id,
                        notifiable_type=NotifiableType.ORDER_LOG,
                        email_delivered=sent,
                    )
                )
            session.add_all(notifications)
            session.commit()

        if status_to == OrderStatus.CANCELLED:

            subject = f"Order cancelled: {offer_name} from {author_name} (ID: {order_id})"

            recipients = users["provider_manager"]
            notifications: list[Notification] = []
            for recipient in recipients:
                role = "provider_manager"
                body = (
                    f"Dear {role},\n\n"
                    f"We regret to inform you that your order {order_name} has been cancelled.\n\n"
                    f"Order ID: {order_id}\n\n"
                    "Best regards,\n"
                    "Operations Team\n"
                    f"{platform_name}"
                )

                sent = _send_email(subject=subject, body=body, recipients=[recipient.email])

                notifications.append(
                    Notification(
                        recipient_id=recipient.id,
                        content=body,
                        notifiable_id=order_log.id,
                        notifiable_type=NotifiableType.ORDER_LOG,
                        email_delivered=sent,
                    )
                )

            recipients = users["coordinator"]
            for recipient in recipients:
                role = "coordinator"
                body = (
                    f"Dear {role},\n\n"
                    f"We regret to inform you that your order {order_name} has been cancelled.\n\n"
                    f"Order ID: {order_id}\n\n"
                    "Best regards,\n"
                    "Operations Team\n"
                    f"{platform_name}"
                )

                sent = _send_email(subject=subject, body=body, recipients=[recipient.email])

                notifications.append(
                    Notification(
                        recipient_id=recipient.id,
                        content=body,
                        notifiable_id=order_log.id,
                        notifiable_type=NotifiableType.ORDER_LOG,
                        email_delivered=sent,
                    )
                )

            session.add_all(notifications)
            session.commit()
