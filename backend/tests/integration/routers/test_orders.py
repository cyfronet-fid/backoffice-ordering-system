def test_admin_sees_all_orders(admin_client, seeded_order):
    response = admin_client.get("/orders/")
    assert response.status_code == 200
    assert any(o["external_ref"] == seeded_order.external_ref for o in response.json())


def test_get_order_by_id(admin_client, seeded_order):
    response = admin_client.get(f"/orders/{seeded_order.id}")
    assert response.status_code == 200
    assert response.json()["external_ref"] == seeded_order.external_ref
