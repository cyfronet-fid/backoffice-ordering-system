from backend.models.tables import User, UserType
from backend.utils import get_whitelabel_role


def test_get_whitelabel_role_returns_coordinator_for_coordinator_user():
    user = User(name="coord", email="coord@example.com", user_type=[UserType.COORDINATOR])
    role = get_whitelabel_role(user)
    assert role == UserType.COORDINATOR


def test_get_whitelabel_role_returns_coordinator_for_admin_user():
    user = User(name="admin", email="admin@example.com", user_type=[UserType.ADMIN])
    role = get_whitelabel_role(user)
    assert role == UserType.COORDINATOR


def test_get_whitelabel_role_returns_provider_manager_for_provider_manager_user():
    user = User(name="pm", email="pm@example.com", user_type=[UserType.PROVIDER_MANAGER])
    role = get_whitelabel_role(user)
    assert role == UserType.PROVIDER_MANAGER


def test_get_whitelabel_role_returns_provider_manager_for_mp_user():
    user = User(name="user", email="user@example.com", user_type=[UserType.MP_USER])
    role = get_whitelabel_role(user)
    assert role == UserType.PROVIDER_MANAGER


def test_get_whitelabel_role_prefers_coordinator_when_multiple_roles():
    user = User(
        name="multi",
        email="multi@example.com",
        user_type=[UserType.PROVIDER_MANAGER, UserType.COORDINATOR],
    )
    role = get_whitelabel_role(user)
    assert role == UserType.COORDINATOR
