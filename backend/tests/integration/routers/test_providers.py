from http import HTTPStatus


def test_admin_sees_all_providers(admin_client, provider, provider_factory, db_session):
    another = provider_factory()
    db_session.commit()

    response = admin_client.get("/providers/")
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    pids = [p["pid"] for p in body]
    assert provider.pid in pids
    assert another.pid in pids


def test_get_provider_by_id(admin_client, provider):
    response = admin_client.get(f"/providers/{provider.id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["pid"] == provider.pid


def test_get_provider_by_id_returns_404_for_missing_provider(admin_client):
    response = admin_client.get("/providers/999999")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "not found" in response.json()["detail"]


def test_get_provider_by_id_returns_403_when_user_has_no_access(
    client, db_session, provider_factory, provider_manager_user_factory, mp_user_client
):
    provider = provider_factory()
    pm = provider_manager_user_factory()
    provider.managers.append(pm)
    db_session.commit()

    response = mp_user_client.get(f"/providers/{provider.id}")

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert "do not have access" in response.json()["detail"]


def test_read_providers_coordinator_sees_all(coordinator_client, provider, provider_factory):
    another = provider_factory()

    response = coordinator_client.get("/providers/")
    assert response.status_code == HTTPStatus.OK
    pids = [p["pid"] for p in response.json()]
    assert provider.pid in pids
    assert another.pid in pids


def test_read_providers_provider_manager_sees_their_employers(
    db_session, provider_factory, provider_manager_client_with_user
):
    client, pm = provider_manager_client_with_user

    employer = provider_factory()
    other = provider_factory()

    employer.managers.append(pm)
    db_session.commit()

    response = client.get("/providers/")

    assert response.status_code == HTTPStatus.OK
    pids = [p["pid"] for p in response.json()]
    assert employer.pid in pids
    assert other.pid not in pids


def test_read_providers_mp_user_sees_none(db_session, provider_factory, mp_user_client):
    provider_factory()
    db_session.commit()

    response = mp_user_client.get("/providers/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []
