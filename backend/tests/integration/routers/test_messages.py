def test_admin_can_post_private_message(admin_client, seeded_order):
    response = admin_client.post(
        "/messages/",
        json={"content": "Hello", "scope": "private", "order_id": seeded_order.id},
    )
    assert response.status_code == 200
    assert response.json()["content"] == "Hello"
    assert response.json()["scope"] == "private"


def test_create_message_returns_404_for_missing_order(admin_client):
    response = admin_client.post(
        "/messages/",
        json={"content": "Hello", "scope": "private", "order_id": 99999},
    )
    assert response.status_code == 404


def test_forbidden_when_user_has_no_access_to_order(
    mp_user_client, provider_manager_user_factory, order_factory, db_session
):
    order = order_factory()
    pm = provider_manager_user_factory()
    order.users.append(pm)
    db_session.commit()

    response = mp_user_client.post(
        "/messages/",
        json={"content": "Hello", "scope": "private", "order_id": order.id},
    )

    assert response.status_code == 403
    assert "You cannot create messages for order" in response.json()["detail"]


def test_public_message_triggers_whitelabel_call(admin_client, seeded_order, monkeypatch):
    called = {}

    def fake_post_message(message_id: int, send_as: str) -> None:
        called["message_id"] = message_id
        called["send_as"] = send_as

    monkeypatch.setattr("backend.services.call_whitelabel.post_message", fake_post_message)

    response = admin_client.post(
        "/messages/",
        json={"content": "Hello public", "scope": "public", "order_id": seeded_order.id},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["scope"] == "public"

    assert called["message_id"] == body["id"]
    assert isinstance(called["send_as"], str) and called["send_as"]


def test_get_order_messages_returns_404_for_missing_order(admin_client):
    response = admin_client.get("/orders/999999/messages")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_get_order_messages_returns_403_when_user_has_no_access(
    mp_user_client, provider_manager_user_factory, order_factory, message_factory, db_session
):
    order = order_factory()
    pm = provider_manager_user_factory()
    order.users.append(pm)
    message_factory(order=order, author=pm)
    db_session.commit()

    response = mp_user_client.get(f"/orders/{order.id}/messages")
    assert response.status_code == 403
    assert "do not have access" in response.json()["detail"]


def test_get_order_messages_returns_200_for_user_with_access(
    order_factory, message_factory, db_session, provider_manager_client_with_user
):
    client, pm = provider_manager_client_with_user
    order = order_factory()
    order.users.append(pm)
    msg = message_factory(order=order, author=pm)
    db_session.commit()
    response = client.get(f"/orders/{order.id}/messages")
    assert response.status_code == 200
    assert any(m["id"] == msg.id for m in response.json())
