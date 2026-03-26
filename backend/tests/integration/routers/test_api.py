from http import HTTPStatus

from sqlmodel import select

from backend.models.tables import MessageScope, Order, Provider, User, UserType


def test_api_returns_forbidden_on_missing_key(client):
    response = client.post("/api/providers", json={})
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_api_returns_unauthorized_on_missing_key(client):
    response = client.post("/api/providers", headers={"x-key": "invalid"}, json={})
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["detail"] == "Invalid or missing API Key"


def test_create_provider_happy_path(api_client, db_session):
    payload = {
        "name": "Provider X",
        "website": "https://provider-x.test",
        "pid": "prov-x",
        "manager_emails": ["mgr@test.com"],
    }

    response = api_client.post("/api/providers", json=payload)
    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert data["name"] == payload["name"]
    assert data["pid"] == payload["pid"]

    statement = select(Provider).where(Provider.pid == "prov-x")
    provider = db_session.exec(statement).one()
    assert provider.name == payload["name"]


def test_create_provider_conflict_on_duplicate_pid(api_client, db_session, provider_factory):
    existing = provider_factory(pid="dup-pid")

    payload = {
        "name": "Another",
        "website": "https://another.test",
        "pid": existing.pid,
        "manager_emails": ["mgr@test.com"],
    }

    response = api_client.post("/api/providers", json=payload)
    assert response.status_code == HTTPStatus.CONFLICT
    assert "already exists" in response.json()["detail"]


def test_create_user_happy_path(api_client, db_session):
    payload = {
        "name": "New User",
        "email": "new.user@test.com",
        "user_type": [UserType.MP_USER.value],
    }

    response = api_client.post("/api/users", json=payload)
    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert data["email"] == payload["email"]
    assert data["user_type"] == payload["user_type"]

    statement = select(User).where(User.email == payload["email"])
    user = db_session.exec(statement).one()

    assert user.user_type == [UserType.MP_USER]


def test_create_user_conflict_on_duplicate_email(api_client, user_factory):
    existing = user_factory()

    payload = {
        "name": "Someone Else",
        "email": existing.email,
        "user_type": [ut.value for ut in existing.user_type],
    }

    response = api_client.post("/api/users", json=payload)
    assert response.status_code == HTTPStatus.CONFLICT
    assert "already exists" in response.json()["detail"]


def test_create_message_happy_path(api_client, db_session, user_factory, order_factory):
    mp_user = user_factory(user_type=[UserType.MP_USER])
    order = order_factory(external_ref="ext-123", project_ref="proj-123")
    db_session.commit()

    payload = {
        "content": "Hello",
        "scope": MessageScope.PUBLIC.value,
        "user_email": mp_user.email,
        "order_external_ref": order.external_ref,
        "project_external_ref": order.project_ref,
    }

    response = api_client.post("/api/messages", json=payload)
    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert data["content"] == payload["content"]
    assert data["scope"] == payload["scope"]
    assert data["author"]["email"] == mp_user.email
    assert data["order"]["external_ref"] == order.external_ref

    db_session.refresh(order)
    assert any(u.id == mp_user.id for u in order.users)


def test_create_message_fails_when_user_missing(api_client, order_factory):
    order = order_factory(external_ref="ext-missing-user")

    payload = {
        "content": "Hello",
        "scope": MessageScope.PRIVATE.value,
        "user_email": "no.such.user@test.com",
        "order_external_ref": order.external_ref,
        "project_external_ref": order.project_ref,
    }

    response = api_client.post("/api/messages", json=payload)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "does not exist" in response.json()["detail"]


def test_create_message_fails_when_user_not_mp_user(api_client, db_session, admin_user_factory, order_factory):
    admin = admin_user_factory()
    order = order_factory(external_ref="ext-admin")
    db_session.commit()

    payload = {
        "content": "Hello",
        "scope": MessageScope.PRIVATE.value,
        "user_email": admin.email,
        "order_external_ref": order.external_ref,
        "project_external_ref": order.project_ref,
    }

    response = api_client.post("/api/messages", json=payload)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "is not an MP_USER" in response.json()["detail"]


def test_create_message_matches_order_by_external_ref_and_project_ref(
    api_client, db_session, user_factory, order_factory
):
    mp_user = user_factory(user_type=[UserType.MP_USER])
    order_factory(external_ref="ext-same", project_ref="proj-A")
    order_b = order_factory(external_ref="ext-same", project_ref="proj-B")
    db_session.commit()

    payload = {
        "content": "Message for project B",
        "scope": MessageScope.PUBLIC.value,
        "user_email": mp_user.email,
        "order_external_ref": "ext-same",
        "project_external_ref": "proj-B",
    }

    response = api_client.post("/api/messages", json=payload)
    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert data["order"]["id"] == order_b.id
    assert data["order"]["project_ref"] == "proj-B"


def test_create_message_fails_when_project_ref_does_not_match(api_client, db_session, user_factory, order_factory):
    mp_user = user_factory(user_type=[UserType.MP_USER])
    order_factory(external_ref="ext-exists", project_ref="proj-real")
    db_session.commit()

    payload = {
        "content": "Hello",
        "scope": MessageScope.PUBLIC.value,
        "user_email": mp_user.email,
        "order_external_ref": "ext-exists",
        "project_external_ref": "proj-wrong",
    }

    response = api_client.post("/api/messages", json=payload)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "does not exist" in response.json()["detail"]


def test_create_message_fails_when_order_missing(api_client, user_factory):
    mp_user = user_factory(user_type=[UserType.MP_USER])

    payload = {
        "content": "Hello",
        "scope": MessageScope.PRIVATE.value,
        "user_email": mp_user.email,
        "order_external_ref": "no-such-order",
        "project_external_ref": "no-such-project",
    }

    response = api_client.post("/api/messages", json=payload)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "does not exist" in response.json()["detail"]


def test_create_order_happy_path(api_client, db_session, provider_factory, provider_manager_user_factory, user_factory):
    provider1 = provider_factory(pid="prov-1")
    provider2 = provider_factory(pid="prov-2")

    manager = provider_manager_user_factory()
    provider1.managers.append(manager)

    owner = user_factory(user_type=[UserType.MP_USER])
    db_session.commit()

    payload = {
        "external_ref": "ext-ord-1",
        "project_ref": "proj-1",
        "config": {},
        "platforms": ["linux"],
        "resource_ref": "res-1",
        "resource_type": "vm",
        "resource_name": "test-vm",
        "provider_pids": [provider1.pid, provider2.pid],
        "owner_email": owner.email,
    }

    response = api_client.post("/api/orders", json=payload)
    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert data["external_ref"] == payload["external_ref"]

    statement = select(Order).where(Order.external_ref == payload["external_ref"])
    order = db_session.exec(statement).one()
    assert order.external_ref == payload["external_ref"]
    assert order.project_ref == payload["project_ref"]


def test_create_order_fails_when_provider_missing(api_client, provider_factory, user_factory):
    provider = provider_factory(pid="prov-present")
    owner = user_factory(user_type=[UserType.MP_USER])

    payload = {
        "external_ref": "ext-ord-2",
        "project_ref": "proj-2",
        "config": {},
        "platforms": ["linux"],
        "resource_ref": "res-2",
        "resource_type": "vm",
        "resource_name": "test-vm-2",
        "provider_pids": [provider.pid, "missing-prov"],
        "owner_email": owner.email,
    }

    response = api_client.post("/api/orders", json=payload)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "do not exist" in response.json()["detail"]


def test_create_order_fails_when_owner_missing_or_not_mp_user(api_client, provider_factory, admin_user_factory):
    provider = provider_factory(pid="prov-x")

    payload = {
        "external_ref": "ext-ord-3",
        "project_ref": "proj-3",
        "config": {},
        "platforms": ["linux"],
        "resource_ref": "res-3",
        "resource_type": "vm",
        "resource_name": "test-vm-3",
        "provider_pids": [provider.pid],
        "owner_email": "no.such.user@test.com",
    }
    response = api_client.post("/api/orders", json=payload)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "does not exist or is not an MP_USER" in response.json()["detail"]


def test_create_order_fails_when_owner_not_mp_user(api_client, provider_factory, admin_user_factory):
    provider = provider_factory(pid="prov-x")
    admin = admin_user_factory()
    payload = {
        "external_ref": "ext-ord-4",
        "project_ref": "proj-3",
        "config": {},
        "platforms": ["linux"],
        "resource_ref": "res-3",
        "resource_type": "vm",
        "resource_name": "test-vm-3",
        "provider_pids": [provider.pid],
        "owner_email": admin.email,
    }
    response = api_client.post("/api/orders", json=payload)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "does not exist or is not an MP_USER" in response.json()["detail"]


def test_create_order_conflict_on_duplicate_external_ref(
    api_client, db_session, provider_factory, user_factory, order_factory
):
    provider = provider_factory(pid="prov-conflict")
    owner = user_factory(user_type=[UserType.MP_USER])
    existing = order_factory(external_ref="ext-conflict", project_ref="proj-conflict")
    db_session.commit()

    payload = {
        "external_ref": existing.external_ref,
        "project_ref": existing.project_ref,
        "config": {},
        "platforms": ["linux"],
        "resource_ref": "res-4",
        "resource_type": "vm",
        "resource_name": "test-vm-4",
        "provider_pids": [provider.pid],
        "owner_email": owner.email,
    }

    response = api_client.post("/api/orders", json=payload)
    assert response.status_code == HTTPStatus.CONFLICT
    assert "already exists" in response.json()["detail"]
