from typing import Literal

from backend.models.tables import User, UserType


def get_whitelabel_role(user: User) -> Literal[UserType.PROVIDER_MANAGER, UserType.COORDINATOR]:
    # The "strongest" (coordinator) role takes precedent.
    #  Also from the perspective of whitelabel, admin is also a coordinator
    if user.is_coordinator() or user.is_admin():
        return UserType.COORDINATOR
    return UserType.PROVIDER_MANAGER
