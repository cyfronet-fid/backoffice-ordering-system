import logging
import smtplib
from email.message import EmailMessage

from backend.config import get_settings
from backend.db import get_session
from backend.models.tables import Message, Order, User, UserType, OrderStatus, Notification, NotifiableType, OrderLog

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

    sender = settings.smtp_from or (settings.smtp_user or "no-reply@example.com")

    print(f"Original sender: {sender}")
    print(f"Original recipients: {recipients}")
    logger.error(f"Original sender: {sender}")
    logger.error(f"Original recipients: {recipients}")

    # sender = "gr"
    # recipients = ["g3"]

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
            return True
    except Exception:
        logger.exception("Failed to send email '%s' to %s", subject, recipients)
        return False


def _send_one_email(subject: str, body: str, recipient: str) -> bool:
    if not recipient:
        logger.info("No recipients provided for email with subject '%s'; skipping send.", subject)
        return False

    settings = get_settings()

    if not settings.smtp_host:
        logger.warning(
            "SMTP host not configured - skipping email send for subject '%s' to %s",
            subject,
            recipient,
        )
        return False

    sender = settings.smtp_from or (settings.smtp_user or "no-reply@example.com")

    print(f"Original sender: {sender}")
    print(f"Original recipients: {recipient}")
    logger.error(f"Original sender: {sender}")
    logger.error(f"Original recipients: {recipient}")

    # sender = "gr"
    # recipients = ["g3"]

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            if settings.smtp_starttls:
                smtp.starttls()

            smtp.login(settings.smtp_user, settings.smtp_password)
            logger.error(f"SMTP login: {settings.smtp_user}\t\tjest git")

            smtp.send_message(message)
            logger.info("Sent email '%s' to %s", subject, recipient)
            return True
    except Exception:
        logger.exception("Failed to send email '%s' to %s", subject, recipient)
        return False


def send_order_message_notification(message_id: int, recipients: list[User]) -> None:
    with get_session() as session:
        logging.debug(f"\t\tSession: {session}")
        db_message = session.get(Message, message_id)
        if db_message is None or db_message.order is None:
            logger.warning("Message %s or related order not found; skipping notification.", message_id)
            return

        order: Order = db_message.order

        # author_email = db_message.author.email if db_message.author else None
        # recipient_ids = [db_message.author_id] if db_message.author_id else []
        # recipient_emails = [author_email] if author_email else []

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
                f"To view and reply, go to your account: {order_link} (prawdopodobnie do zmiany)\n\n"
                f"Best regards,\n"
                "Operations Team\n"
                f"{platform_name}"
            )
            sent = _send_one_email(subject=subject, body=body, recipient=recipient.email)

            notifications.append(
                Notification(
                    recipient_id=recipient.id,
                    content=body,
                    notifiable_id=message_id,
                    notifiable_type=NotifiableType.MESSAGE,
                    email_delivered=sent,
                )
            )

        # # for user_id in recipient_ids:

        session.add_all(notifications)
        session.commit()
        # for notification in notifications:
        #     session.refresh(notification)


        # recipient_emails = [user.email for user in recipients]
        # logging.error(f"\t\t\t\tRecipients: {recipient_emails}")
        # sent = _send_email(subject=subject, body=body, recipients=recipient_emails)
        # if sent:
        #     for notification in notifications:
        #         notification.email_delivered = True
        #     session.add_all(notifications)
        #     session.commit()



def send_order_status_change_notification(order_id: int, status_from: OrderStatus, status_to: OrderStatus, users: dict[str, list[User]], status_change_author: User) -> None:
    # _send_email(subject="test", body="test", recipients=["szymon.figura@cyfronet.pl"])
    with get_session() as session:
        order = session.get(Order, order_id)
        if order is None:
            logger.warning("Order %s not found; skipping status change notification.", order_id)
            return

        order_users = order.users
        print(f"\t\t\tOrder users: {[user.email for user in order.users]}\n\n\n\n\n")

        settings = get_settings()
        platform_name = settings.platform_name

        offer_name = order.resource_name
        provider_names = ", ".join(provider.name for provider in order.providers) or "the provider"
        provider_link = "".join(p.website for p in order.providers)
        order_id = order.id
        order_name = order.resource_name # offer name

        # user_emails = [user.email for user in order_users]

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
            recipient_emails = [recipient.email for recipient in recipients]

            order_log = OrderLog(order_id=order_id, status_from=status_from, status_to=status_to, author_id=status_change_author.id)
            session.add(order_log)
            session.commit()

            notifications: list[Notification] = []
            for recipient in recipients:
                sent = _send_one_email(subject, body, recipient.email)

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
            recipient_emails = [recipient.email for recipient in recipients]

            order_log = OrderLog(order_id=order_id, status_from=status_from, status_to=status_to, author_id=status_change_author.id)
            session.add(order_log)
            session.commit()

            notifications: list[Notification] = []
            for recipient in recipients:
                sent = _send_one_email(subject, body, recipient.email)

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
            recipient_emails = [recipient.email for recipient in recipients]

            order_log = OrderLog(order_id=order_id, status_from=status_from, status_to=status_to,
                                 author_id=status_change_author.id)
            session.add(order_log)
            session.commit()

            notifications: list[Notification] = []
            for recipient in recipients:
                sent = _send_one_email(subject, body, recipient.email)

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
            pass



        # owner: User | None = next(
        #     (user for user in order.users if UserType.MP_USER in user.user_type),
        #     None,
        # )
        # owner_name = owner.name if owner else "user"
        #
        # user_recipients = sorted(
        #     {
        #         user.email
        #         for user in order.users
        #         if user.email and UserType.MP_USER in user.user_type
        #     }
        # )
        #
        # provider_recipients = sorted(
        #     {
        #         manager.email
        #         for provider in order.providers
        #         for manager in provider.managers
        #         if manager.email
        #     }
        # )
        #
        # coordinator_users = session.scalars(
        #     select(User).where(User.user_type.contains([UserType.COORDINATOR]))
        # ).all()
        # coordinator_recipients = sorted(
        #     {user.email for user in coordinator_users if user.email}
        # )
        #
        # status = order.status
        # provider_link = ", ".join(
        #     provider.website for provider in order.providers if provider.website
        # )
        # order_link = f"https://bos.eosc.pl/orders/{order_id}"
        #
        # subject = ""
        # body = ""

        # _send_email(subject="test2", body="test", recipients=["szymon.figura@cyfronet.pl"])








        # recipient_emails = [order.author.email]
        # logging.error(f"\t\t\t\tRecipients: {recipient_emails}")
        # logging.error(f"sending email to {recipient_emails}")
        # if subject and body:
        #     sent = _send_email(subject=subject, body=body, recipients=recipient_emails)
        # sent = _send_email(subject=subject, body=body, recipients=recipient_emails)
        #
        # logger.info("No email template configured for order %s status %s; skipping notification.", order_id, status)

