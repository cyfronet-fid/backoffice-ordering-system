import pytest

from backend.auth import current_user
from backend.config import get_settings
from backend.main import app


@pytest.fixture
def seeded_order(order_factory, provider_factory, user_factory):
    return order_factory(providers=[provider_factory()], users=[user_factory()])


def _role_client(client, user):
    app.dependency_overrides[current_user] = lambda: user
    try:
        yield client
    finally:
        app.dependency_overrides.pop(current_user, None)


def _role_client_with_user(client, user):
    app.dependency_overrides[current_user] = lambda: user
    try:
        yield client, user
    finally:
        app.dependency_overrides.pop(current_user, None)


@pytest.fixture
def admin_client(client, admin_user_factory):
    yield from _role_client(client, admin_user_factory())


@pytest.fixture
def coordinator_client(client, coordinator_user_factory):
    yield from _role_client(client, coordinator_user_factory())


@pytest.fixture
def provider_manager_client(client, provider_manager_user_factory):
    yield from _role_client(client, provider_manager_user_factory())


@pytest.fixture
def provider_manager_client_with_user(client, provider_manager_user_factory):
    user = provider_manager_user_factory()
    yield from _role_client_with_user(client, user)


@pytest.fixture
def mp_user_client_with_user(client, user):
    yield from _role_client_with_user(client, user)


@pytest.fixture
def mp_user_client(client, user):
    yield from _role_client(client, user)


@pytest.fixture
def api_client(client):
    client.headers["x-key"] = get_settings().api_key
    yield client
    client.headers.pop("x-key", None)
