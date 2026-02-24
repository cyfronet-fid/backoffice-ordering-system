def test_admin_sees_all_users(admin_client, user):
    response = admin_client.get("/users/")
    assert response.status_code == 200
    assert user.email in {u["email"] for u in response.json()}


def test_get_user_by_id(admin_client, user):
    response = admin_client.get(f"/users/{user.id}")
    assert response.status_code == 200
    assert response.json()["email"] == user.email
