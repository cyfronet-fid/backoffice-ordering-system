from http import HTTPStatus

from backend.models.tables import UserType


def test_admin_sees_all_users(admin_client, user, user_factory, db_session):
    another = user_factory()
    db_session.commit()

    response = admin_client.get("/users/")
    assert response.status_code == HTTPStatus.OK
    emails = {u["email"] for u in response.json()}
    assert user.email in emails
    assert another.email in emails


def test_get_user_by_id(admin_client, user):
    response = admin_client.get(f"/users/{user.id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["email"] == user.email


def test_get_user_by_id_returns_404_for_missing_user(admin_client):
    response = admin_client.get("/users/999999")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "not found" in response.json()["detail"]


def test_get_user_by_id_returns_403_when_no_access(client, db_session, user_factory, mp_user_client):
    admin = user_factory(user_type=[UserType.ADMIN])
    db_session.commit()
    response = mp_user_client.get(f"/users/{admin.id}")
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert "do not have access" in response.json()["detail"]


def test_read_users_coordinator_sees_all_users(coordinator_client, user, user_factory):
    another = user_factory()

    response = coordinator_client.get("/users/")
    assert response.status_code == HTTPStatus.OK
    emails = {u["email"] for u in response.json()}
    assert user.email in emails
    assert another.email in emails


def test_read_users_non_admin_gets_only_self(db_session, user_factory, mp_user_client_with_user):
    client, mp_user = mp_user_client_with_user
    other = user_factory()
    db_session.commit()
    response = client.get("/users/")
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert len(body) == 1
    assert body[0]["email"] == mp_user.email
    assert body[0]["email"] != other.email


def test_get_current_user_returns_authenticated_user(db_session, mp_user_client_with_user):
    client, mp_user = mp_user_client_with_user
    db_session.commit()

    response = client.get("/users/me")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["email"] == mp_user.email
