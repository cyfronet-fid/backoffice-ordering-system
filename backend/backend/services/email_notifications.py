import logging
import smtplib
from email.message import EmailMessage

from sqlmodel import select

from backend.config import get_settings
from backend.db import get_session
from backend.models.tables import Message, Order, User, UserType, OrderStatus

logger = logging.getLogger(__name__)


def _send_email(subject: str, body: str, recipients: list[str]) -> None:
    if not recipients:
        logger.info("No recipients provided for email with subject '%s'; skipping send.", subject)
        logger.info("\n\nsend email")
        print(type(recipients))
        print(recipients)
        return

    settings = get_settings()

    if not settings.smtp_host:
        logger.warning(
            "SMTP host not configured - skipping email send for subject '%s' to %s",
            subject,
            recipients,
        )
        return

    sender = settings.smtp_from or (settings.smtp_user or "no-reply@example.com")

    print(f"Original sender: {sender}")
    print(f"Original recipients: {recipients}")
    logger.error(f"Original sender: {sender}")
    logger.error(f"Original recipients: {recipients}")

    sender = "grw4zyyy@gmail.com"
    recipients = ["g3rw4zyyyyy@gmail.com"]

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
            logger.error(f"SMTP login: {settings.smtp_user}\t\tjest git")

            smtp.send_message(message)
            logger.info("Sent email '%s' to %s", subject, recipients)
    except Exception:
        logger.exception("Failed to send email '%s' to %s", subject, recipients)


def send_order_message_notification(message_id: int) -> None:
    with get_session() as session:
        logging.debug(f"\t\tSession: {session}")
        db_message = session.get(Message, message_id)
        if db_message is None or db_message.order is None:
            logger.warning("Message %s or related order not found; skipping notification.", message_id)
            return

        order: Order = db_message.order

        author_email = db_message.author.email if db_message.author else None
        recipients = [author_email]

        settings = get_settings()
        platform_name = settings.platform_name
        order_id = order.id
        order_link = f"https://bos.eosc.pl/orders/{order_id}"
        resource_name = order.resource_name

        subject = f"New message regarding offer {resource_name}"
        body = (
            f"Dear User,\n\n"
            f"This is test message regarding offer {resource_name}\n\n"
            f"Order ID: {order_id}\n"
            f"Message content:\n"
            f"{db_message.content}\n"
            f"To view and reply, go to your account: {order_link}\n\n"
            f"Best regards\n"
            "Operations Team\n"
            f"{platform_name}"
        )
        _send_email(subject=subject, body=body, recipients=list(recipients))



def send_order_status_change_notification(order_id: int) -> None:
    with get_session() as session:
        order = session.get(Order, order_id)
        if order is None:
            logger.warning("Order %s not found; skipping status change notification.", order_id)
            return

        settings = get_settings()
        platform_name = settings.platform_name

        offer_name = order.resource_name
        provider_names = ", ".join(provider.name for provider in order.providers) or "the provider"

        owner: User | None = next(
            (user for user in order.users if UserType.MP_USER in user.user_type),
            None,
        )
        owner_name = owner.name if owner else "user"

        user_recipients = sorted(
            {
                user.email
                for user in order.users
                if user.email and UserType.MP_USER in user.user_type
            }
        )

        provider_recipients = sorted(
            {
                manager.email
                for provider in order.providers
                for manager in provider.managers
                if manager.email
            }
        )

        coordinator_users = session.scalars(
            select(User).where(User.user_type.contains([UserType.COORDINATOR]))
        ).all()
        coordinator_recipients = sorted(
            {user.email for user in coordinator_users if user.email}
        )

        status = order.status
        provider_link = ", ".join(
            provider.website for provider in order.providers if provider.website
        )
        order_link = f"https://bos.eosc.pl/orders/{order_id}"

        if status == OrderStatus.ON_HOLD:
            if not user_recipients:
                logger.info("No MP_USER recipients for order %s ON_HOLD notification; skipping.", order_id)
                return

            subject = f"Your order for {offer_name} is on hold"
            body = (
                "Dear User,\n\n"
                f"Your order {offer_name} from {provider_names} is currently on hold. "
                "This means processing has been temporarily paused.\n\n"
                "We’ll let you know once it resumes.\n\n"
                f"If you need more details about the on hold status, contact the provider here: {provider_link}\n\n"
                "Best regards,\n"
                "Operations Team\n"
                f"{platform_name}"
            )
            _send_email(subject=subject, body=body, recipients=list(user_recipients))
            return

        if status == OrderStatus.COMPLETED:
            if not user_recipients:
                logger.info("No MP_USER recipients for order %s COMPLETED notification; skipping.", order_id)
                return

            subject = f"Your order for {offer_name} was successfully processed"
            body = (
                "Dear User,\n\n"
                f"Your order {offer_name} from {provider_names} has been successfully processed.\n\n"
                f"You can view the order details and access information here: {order_link}\n\n"
                f"If you need help with next steps, you can ask the provider here: {provider_link}\n\n"
                "Best regards,\n"
                "Operations Team\n"
                f"{platform_name}"
            )
            _send_email(subject=subject, body=body, recipients=list(user_recipients))
            return

        if status == OrderStatus.REJECTED:
            if not user_recipients:
                logger.info("No MP_USER recipients for order %s REJECTED notification; skipping.", order_id)
                return

            subject = f"Your order for {offer_name} has been rejected"
            body = (
                "Dear User,\n\n"
                f"We regret to inform you that your order {offer_name} from {provider_names} has been rejected.\n\n"
                f"If you need more details about the reason for rejection, you can contact the provider here: {provider_link}\n\n"
                "Best regards,\n"
                "Operations Team\n"
                f"{platform_name}"
            )
            _send_email(subject=subject, body=body, recipients=list(user_recipients))
            return

        if status == OrderStatus.CANCELLED:
            subject = f"Order cancelled: {offer_name} from {owner_name} (ID: {order.id})"

            provider_body = (
                "Dear Provider,\n\n"
                f"We regret to inform you that your order {offer_name} has been cancelled.\n\n"
                f"Order ID: {order.id}\n\n"
                "Best regards,\n"
                "Operations Team\n"
                f"{platform_name}"
            )

            coordinator_body = (
                "Dear Coordinator,\n\n"
                f"We regret to inform you that your order {offer_name} has been cancelled.\n\n"
                f"Order ID: {order.id}\n\n"
                "Best regards,\n"
                "Operations Team\n"
                f"{platform_name}"
            )

            if provider_recipients:
                _send_email(subject=subject, body=provider_body, recipients=list(provider_recipients))

            if coordinator_recipients:
                _send_email(subject=subject, body=coordinator_body, recipients=list(coordinator_recipients))

            if not provider_recipients and not coordinator_recipients:
                logger.info(
                    "No provider/coordinator recipients for order %s CANCELLED notification; skipping.",
                    order_id,
                )
            return

        logger.info("No email template configured for order %s status %s; skipping notification.", order_id, status)