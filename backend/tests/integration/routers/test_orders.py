from http import HTTPStatus

from backend.models.tables import OrderStatus


def test_admin_sees_all_orders(admin_client, seeded_order, order_factory, db_session):
    older = order_factory()
    older.created_at = seeded_order.created_at.replace(year=seeded_order.created_at.year - 1)
    db_session.commit()

    response = admin_client.get("/orders/")
    assert response.status_code == HTTPStatus.OK
    body = response.json()

    refs = [o["external_ref"] for o in body]
    assert seeded_order.external_ref in refs
    assert older.external_ref in refs

    created_ats = [o["created_at"] for o in body]
    assert created_ats == sorted(created_ats, reverse=True)


def test_get_order_by_id(admin_client, seeded_order):
    response = admin_client.get(f"/orders/{seeded_order.id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["external_ref"] == seeded_order.external_ref


def test_get_order_by_id_returns_404_for_missing_order(admin_client):
    response = admin_client.get("/orders/999999")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "not found" in response.json()["detail"]


def test_get_order_by_id_returns_403_when_user_has_no_access(
    client, db_session, order_factory, provider_manager_user_factory, mp_user_client
):
    order = order_factory()
    pm = provider_manager_user_factory()
    order.users.append(pm)
    db_session.commit()

    response = mp_user_client.get(f"/orders/{order.id}")

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert "do not have access" in response.json()["detail"]


def test_read_orders_coordinator_sees_all_orders(coordinator_client, seeded_order, order_factory):
    another = order_factory()

    response = coordinator_client.get("/orders/")
    assert response.status_code == HTTPStatus.OK
    refs = [o["external_ref"] for o in response.json()]
    assert seeded_order.external_ref in refs
    assert another.external_ref in refs


def test_read_orders_provider_manager_sees_only_own_orders(
    db_session, order_factory, provider_manager_client_with_user
):
    client, pm = provider_manager_client_with_user
    own_order = order_factory(users=[pm])
    foreign_order = order_factory()
    db_session.commit()

    response = client.get(f"/orders/")

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    ids = [o["id"] for o in body]
    assert own_order.id in ids
    assert foreign_order.id not in ids


def test_read_orders_mp_user_sees_no_orders(mp_user_client):
    response = mp_user_client.get(f"/orders/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


def test_get_order_messages_sorted_by_created_at(admin_client, seeded_order, message_factory, db_session):
    m1 = message_factory(order=seeded_order)
    m2 = message_factory(order=seeded_order)
    if m1.created_at > m2.created_at:
        m1.created_at, m2.created_at = m2.created_at, m1.created_at
    db_session.commit()

    response = admin_client.get(f"/orders/{seeded_order.id}/messages")
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    timestamps = [m["created_at"] for m in body]
    assert timestamps == sorted(timestamps)


def test_change_order_status_happy_path_triggers_whitelabel(admin_client, order_factory, db_session, monkeypatch):
    order = order_factory(status=OrderStatus.SUBMITTED)
    db_session.commit()

    called = {}

    def fake_change_order_status(order_id: int) -> None:
        called["order_id"] = order_id

    monkeypatch.setattr("backend.services.call_whitelabel.change_order_status", fake_change_order_status)

    response = admin_client.post(
        f"/orders/{order.id}/change_status", params={"new_status": OrderStatus.PROCESSING.value}
    )
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body["status"] == OrderStatus.PROCESSING.value

    db_session.refresh(order)
    assert order.status == OrderStatus.PROCESSING
    assert called["order_id"] == order.id


def test_change_order_status_invalid_transition_returns_400(admin_client, order_factory, db_session):
    order = order_factory(status=OrderStatus.COMPLETED)
    db_session.commit()

    response = admin_client.post(
        f"/orders/{order.id}/change_status", params={"new_status": OrderStatus.PROCESSING.value}
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "Invalid status transition" in response.json()["detail"]
