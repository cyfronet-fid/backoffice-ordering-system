from typing import Callable

from backend.models.tables import OrderStatus


def _on_hold_email(ctx: dict) -> tuple[str, str]:
    return (
        f"Your order for {ctx['offer_name']} is on hold",
        "Dear User,\n\n"
        f"Your order {ctx['offer_name']} from {ctx['provider_names']} is currently on hold. "
        "This means processing has been temporarily paused.\n\n"
        "We'll let you know once it resumes.\n\n"
        "If you need more details about the on hold status,"
        f"contact the provider here: {ctx['marketplace_order_link']}\n\n"
        f"Best regards,\nOperations Team\n{ctx['platform_name']}",
    )


def _completed_email(ctx: dict) -> tuple[str, str]:
    return (
        f"Your order for {ctx['offer_name']} was successfully processed",
        "Dear User,\n\n"
        f"Your order {ctx['offer_name']} from {ctx['provider_names']} has been successfully processed.\n\n"
        f"You can view the order details and access information here: {ctx['order_link']}\n\n"
        f"If you need help with next steps, you can ask the provider here: {ctx['marketplace_order_link']}\n\n"
        f"Best regards,\nOperations Team\n{ctx['platform_name']}",
    )


def _rejected_email(ctx: dict) -> tuple[str, str]:
    return (
        f"Your order for {ctx['offer_name']} has been rejected",
        "Dear User,\n\n"
        f"We regret to inform you that your order {ctx['offer_name']}"
        f"from {ctx['provider_names']} has been rejected.\n\n"
        "If you need more details about the reason for rejection,"
        f"you can contact the provider here: {ctx['marketplace_order_link']}\n\n"
        f"Best regards,\nOperations Team\n{ctx['platform_name']}",
    )


STATUS_NOTIFICATION_MAP: dict[OrderStatus, tuple[Callable, list[str]]] = {
    OrderStatus.ON_HOLD: (_on_hold_email, ["mp_user", "provider_manager", "coordinator"]),
    OrderStatus.COMPLETED: (_completed_email, ["mp_user"]),
    OrderStatus.REJECTED: (_rejected_email, ["mp_user"]),
}
