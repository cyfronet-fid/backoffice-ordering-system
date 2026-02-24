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
