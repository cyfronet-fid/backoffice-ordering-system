def test_admin_sees_all_providers(admin_client, provider):
    response = admin_client.get("/providers/")
    assert response.status_code == 200
    assert any(p["pid"] == provider.pid for p in response.json())


def test_get_provider_by_id(admin_client, provider):
    response = admin_client.get(f"/providers/{provider.id}")
    assert response.status_code == 200
    assert response.json()["pid"] == provider.pid
