from typing import Literal

from backend.models.tables import MessageScope, Order, User, UserType


def get_whitelabel_role(user: User) -> Literal[UserType.PROVIDER_MANAGER, UserType.COORDINATOR]:
    # The "strongest" (coordinator) role takes precedent.
    #  Also from the perspective of whitelabel, admin is also a coordinator
    if user.is_coordinator() or user.is_admin():
        return UserType.COORDINATOR
    return UserType.PROVIDER_MANAGER


def _resolve_message_recipients(order: Order, scope: MessageScope) -> list[User]:
    allowed_roles: set[UserType]

    if scope == MessageScope.PUBLIC:
        allowed_roles = {UserType.COORDINATOR, UserType.PROVIDER_MANAGER, UserType.MP_USER}
    else:
        allowed_roles = {UserType.COORDINATOR, UserType.PROVIDER_MANAGER}

    return [u for u in order.users if any(role in allowed_roles for role in u.user_type)]


def group_users_by_role(order: Order) -> dict[str, list[User]]:
    grouped = {
        "admin": [],
        "coordinator": [],
        "provider_manager": [],
        "mp_user": [],
    }

    for user in order.users:
        if user.is_admin():
            grouped["admin"].append(user)
            continue

        if user.is_coordinator():
            grouped["coordinator"].append(user)
            continue

        if user.is_provider_manager():
            grouped["provider_manager"].append(user)
            continue

        if UserType.MP_USER in user.user_type:
            grouped["mp_user"].append(user)

    return grouped
