import pytest

from backend.models.tables import User, Order, Provider, UserType


@pytest.fixture
def base_user():
    return User(id=1, email="user@example.com", user_type=[UserType.MP_USER])


@pytest.fixture
def admin_user(base_user):
    return User(id=1, email="user@example.com", user_type=[UserType.ADMIN])


@pytest.fixture
def coordinator_user(base_user):
    return User(id=1, email="user@example.com", user_type=[UserType.COORDINATOR])


@pytest.fixture
def provider_manager_user(base_user):
    return User(id=1, email="user@example.com", user_type=[UserType.PROVIDER_MANAGER])


def test_admin_has_access_override(admin_user):
    assert admin_user._has_access_override() is True


def test_coordinator_has_access_override(coordinator_user):
    assert coordinator_user._has_access_override() is True


def test_regular_user_has_no_access_override(base_user):
    assert base_user._has_access_override() is False


def test_has_access_to_order_admin(admin_user):
    fake_order = Order(id=10)
    assert admin_user.has_access_to_order(fake_order)


def test_has_access_to_order_manager(provider_manager_user):
    fake_order = Order(id=1)
    provider_manager_user.orders = [fake_order]
    assert provider_manager_user.has_access_to_order(fake_order)


def test_has_access_to_order_denied(provider_manager_user):
    fake_order = Order(id=2)
    provider_manager_user.orders = []  # Not in orders
    assert not provider_manager_user.has_access_to_order(fake_order)


def test_has_access_to_provider_manager(provider_manager_user):
    provider = Provider(id=1)
    provider_manager_user.employers = [provider]
    assert provider_manager_user.has_access_to_provider(provider)


def test_has_access_to_provider_denied(provider_manager_user):
    provider = Provider(id=1)
    provider_manager_user.employers = []
    assert not provider_manager_user.has_access_to_provider(provider)


def test_has_access_to_other_user_same_id(base_user):
    other = User(id=1, email="user@example.com")
    assert base_user.has_access_to_other_user(other)


def test_has_access_to_other_user_different_id(base_user):
    other = User(id=2, email="other@example.com")
    assert not base_user.has_access_to_other_user(other)


def test_eq_true():
    user1 = User(email="same@example.com")
    user2 = User(email="same@example.com")
    assert user1 == user2


def test_eq_false():
    user1 = User(email="a@example.com")
    user2 = User(email="b@example.com")
    assert user1 != user2


def test_hash():
    user = User(email="hashme@example.com")
    assert hash(user) == hash("hashme@example.com")
