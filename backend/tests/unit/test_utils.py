from backend.models.tables import Order, User, UserType
from backend.utils import get_whitelabel_role, group_users_by_role


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


def test_group_users_by_role_groups_all_roles_correctly():
    admin = User(name="admin", email="a@example.com", user_type=[UserType.ADMIN])
    coord = User(name="coord", email="c@example.com", user_type=[UserType.COORDINATOR])
    pm = User(name="pm", email="pm@example.com", user_type=[UserType.PROVIDER_MANAGER])
    mp = User(name="mp", email="mp@example.com", user_type=[UserType.MP_USER])

    order = Order(users=[admin, coord, pm, mp])

    grouped = group_users_by_role(order)

    assert grouped["admin"] == [admin]
    assert grouped["coordinator"] == [coord]
    assert grouped["provider_manager"] == [pm]
    assert grouped["mp_user"] == [mp]


def test_group_users_by_role_empty_order():
    order = Order(users=[])

    grouped = group_users_by_role(order)

    assert grouped == {
        "admin": [],
        "coordinator": [],
        "provider_manager": [],
        "mp_user": [],
    }
