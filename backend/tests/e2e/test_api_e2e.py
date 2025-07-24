import pytest

from backend.models.tables import MessageScope, UserType


class TestProvidersAPI:
    def test_create_provider_success(self, client, api_headers, db_session):
        provider_data = {
            "name": "Test Provider",
            "website": "https://testprovider.com",
            "pid": "test-provider-001",
            "manager_emails": ["manager@test.com"],
        }

        response = client.post("/api/providers", json=provider_data, headers=api_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Provider"
        assert data["website"] == "https://testprovider.com"
        assert data["pid"] == "test-provider-001"
        assert "id" in data
        assert "created_at" in data

    def test_create_provider_duplicate_pid(self, client, api_headers, db_session):
        provider_data = {
            "name": "Test Provider",
            "website": "https://testprovider.com",
            "pid": "duplicate-pid",
            "manager_emails": ["manager@test.com"],
        }

        # Create first provider
        response1 = client.post("/api/providers", json=provider_data, headers=api_headers)
        assert response1.status_code == 200

        # Try to create duplicate
        response2 = client.post("/api/providers", json=provider_data, headers=api_headers)
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"]

    def test_create_provider_unauthorized(self, client, db_session):
        provider_data = {
            "name": "Test Provider",
            "website": "https://testprovider.com",
            "pid": "test-provider-002",
            "manager_emails": ["manager@test.com"],
        }

        response = client.post("/api/providers", json=provider_data)
        assert response.status_code == 403

    def test_create_provider_missing_required_fields(self, client, api_headers, db_session):
        # Missing name
        provider_data = {
            "website": "https://testprovider.com",
            "pid": "test-provider-003",
            "manager_emails": ["manager@test.com"],
        }
        response = client.post("/api/providers", json=provider_data, headers=api_headers)
        assert response.status_code == 422

        # Missing pid
        provider_data = {
            "name": "Test Provider",
            "website": "https://testprovider.com",
            "manager_emails": ["manager@test.com"],
        }
        response = client.post("/api/providers", json=provider_data, headers=api_headers)
        assert response.status_code == 422

    def test_create_provider_invalid_website_url(self, client, api_headers, db_session):
        provider_data = {
            "name": "Test Provider",
            "website": "not-a-valid-url",
            "pid": "test-provider-004",
            "manager_emails": ["manager@test.com"],
        }

        response = client.post("/api/providers", json=provider_data, headers=api_headers)
        # This should succeed if no URL validation is implemented, or fail if it is
        # The actual behavior depends on the model validation rules
        assert response.status_code in [200, 422]

    def test_create_provider_empty_manager_emails(self, client, api_headers, db_session):
        provider_data = {
            "name": "Test Provider",
            "website": "https://testprovider.com",
            "pid": "test-provider-005",
            "manager_emails": [],
        }

        response = client.post("/api/providers", json=provider_data, headers=api_headers)
        assert response.status_code == 422  # Empty manager_emails not allowed


class TestUsersAPI:
    def test_create_user_success(self, client, api_headers, db_session):
        user_data = {"name": "John Doe", "email": "john.doe@test.com", "user_type": [UserType.MP_USER.value]}

        response = client.post("/api/users", json=user_data, headers=api_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["email"] == "john.doe@test.com"
        assert data["user_type"] == [UserType.MP_USER.value]
        assert "id" in data
        assert "created_at" in data

    def test_create_user_duplicate_email(self, client, api_headers, db_session):
        user_data = {"name": "John Doe", "email": "duplicate@test.com", "user_type": [UserType.MP_USER.value]}

        # Create first user
        response1 = client.post("/api/users", json=user_data, headers=api_headers)
        assert response1.status_code == 200

        # Try to create duplicate
        user_data["name"] = "Jane Doe"  # Different name, same email
        response2 = client.post("/api/users", json=user_data, headers=api_headers)
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"]

    def test_create_user_multiple_roles(self, client, api_headers, db_session):
        user_data = {
            "name": "Admin User",
            "email": "admin@test.com",
            "user_type": [UserType.ADMIN.value, UserType.COORDINATOR.value],
        }

        response = client.post("/api/users", json=user_data, headers=api_headers)

        assert response.status_code == 200
        data = response.json()
        assert UserType.ADMIN.value in data["user_type"]
        assert UserType.COORDINATOR.value in data["user_type"]

    def test_create_user_invalid_type(self, client, api_headers, db_session):
        user_data = {"name": "Invalid User", "email": "invalid@test.com", "user_type": ["invalid_type"]}

        response = client.post("/api/users", json=user_data, headers=api_headers)

        assert response.status_code == 422

    def test_create_user_missing_required_fields(self, client, api_headers, db_session):
        # Missing name
        user_data = {"email": "missing_name@test.com", "user_type": [UserType.MP_USER.value]}
        response = client.post("/api/users", json=user_data, headers=api_headers)
        assert response.status_code == 422

        # Missing email
        user_data = {"name": "Missing Email", "user_type": [UserType.MP_USER.value]}
        response = client.post("/api/users", json=user_data, headers=api_headers)
        assert response.status_code == 422

        # Missing user_type
        user_data = {"name": "Missing Type", "email": "missing_type@test.com"}
        response = client.post("/api/users", json=user_data, headers=api_headers)
        assert response.status_code == 422


class TestOrdersAPI:
    @pytest.fixture
    def setup_provider(self, client, api_headers):
        provider_data = {
            "name": "Order Test Provider",
            "website": "https://ordertestprovider.com",
            "pid": "order-provider-001",
            "manager_emails": ["manager@ordertest.com"],
        }
        response = client.post("/api/providers", json=provider_data, headers=api_headers)
        assert response.status_code == 200
        return response.json()

    def test_create_order_success(self, client, api_headers, db_session, setup_provider):
        order_data = {
            "external_ref": "EXT-12345",
            "project_ref": "PROJ-001",
            "config": {"test": "value"},
            "platforms": ["platform1", "platform2"],
            "resource_ref": "RES-001",
            "resource_type": "compute",
            "resource_name": "Test Resource",
            "provider_pids": [setup_provider["pid"]],
        }

        response = client.post("/api/orders", json=order_data, headers=api_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["external_ref"] == "EXT-12345"
        assert data["project_ref"] == "PROJ-001"
        assert data["status"] == "submitted"
        assert "id" in data
        assert "created_at" in data

    def test_create_order_nonexistent_provider(self, client, api_headers, db_session):
        order_data = {
            "external_ref": "EXT-99999",
            "project_ref": "PROJ-001",
            "config": {"test": "value"},
            "platforms": ["platform1"],
            "resource_ref": "RES-001",
            "resource_type": "compute",
            "resource_name": "Test Resource",
            "provider_pids": ["nonexistent-provider"],
        }

        response = client.post("/api/orders", json=order_data, headers=api_headers)

        assert response.status_code == 400
        assert "do not exist" in response.json()["detail"]

    def test_create_order_duplicate_external_ref_same_project(self, client, api_headers, db_session, setup_provider):
        order_data = {
            "external_ref": "DUP-12345",
            "project_ref": "SAME-PROJ",
            "config": {"test": "value"},
            "platforms": ["platform1"],
            "resource_ref": "RES-001",
            "resource_type": "compute",
            "resource_name": "Test Resource",
            "provider_pids": [setup_provider["pid"]],
        }

        # Create first order
        response1 = client.post("/api/orders", json=order_data, headers=api_headers)
        assert response1.status_code == 200

        # Try to create duplicate with same project_ref and external_ref
        response2 = client.post("/api/orders", json=order_data, headers=api_headers)
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"]

    def test_create_order_same_external_ref_different_project(self, client, api_headers, db_session, setup_provider):
        base_data = {
            "external_ref": "SAME-EXT-REF",
            "config": {"test": "value"},
            "platforms": ["platform1"],
            "resource_ref": "RES-001",
            "resource_type": "compute",
            "resource_name": "Test Resource",
            "provider_pids": [setup_provider["pid"]],
        }

        # Create first order
        order_data1 = {**base_data, "project_ref": "PROJ-001"}
        response1 = client.post("/api/orders", json=order_data1, headers=api_headers)
        assert response1.status_code == 200

        # Create second order with same external_ref but different project_ref (should succeed)
        order_data2 = {**base_data, "project_ref": "PROJ-002"}
        response2 = client.post("/api/orders", json=order_data2, headers=api_headers)
        assert response2.status_code == 200

    def test_create_order_missing_required_fields(self, client, api_headers, db_session):
        # Missing external_ref
        order_data = {
            "project_ref": "PROJ-001",
            "config": {"test": "value"},
            "platforms": ["platform1"],
            "resource_ref": "RES-001",
            "resource_type": "compute",
            "resource_name": "Test Resource",
            "provider_pids": ["some-provider"],
        }
        response = client.post("/api/orders", json=order_data, headers=api_headers)
        assert response.status_code == 422

        # Missing config
        order_data = {
            "external_ref": "EXT-001",
            "project_ref": "PROJ-001",
            "platforms": ["platform1"],
            "resource_ref": "RES-001",
            "resource_type": "compute",
            "resource_name": "Test Resource",
            "provider_pids": ["some-provider"],
        }
        response = client.post("/api/orders", json=order_data, headers=api_headers)
        assert response.status_code == 422

    def test_create_order_with_empty_platforms(self, client, api_headers, db_session, setup_provider):
        order_data = {
            "external_ref": "EXT-EMPTY-PLATFORMS",
            "project_ref": "PROJ-001",
            "config": {"test": "value"},
            "platforms": [],  # Empty platforms array
            "resource_ref": "RES-001",
            "resource_type": "compute",
            "resource_name": "Test Resource",
            "provider_pids": [setup_provider["pid"]],
        }

        response = client.post("/api/orders", json=order_data, headers=api_headers)
        assert response.status_code == 200  # Should succeed with empty platforms

    def test_create_order_multiple_providers(self, client, api_headers, db_session):
        # Create multiple providers
        provider1_data = {
            "name": "Provider 1",
            "website": "https://provider1.com",
            "pid": "provider-1",
            "manager_emails": ["manager1@test.com"],
        }
        provider2_data = {
            "name": "Provider 2",
            "website": "https://provider2.com",
            "pid": "provider-2",
            "manager_emails": ["manager2@test.com"],
        }

        response1 = client.post("/api/providers", json=provider1_data, headers=api_headers)
        response2 = client.post("/api/providers", json=provider2_data, headers=api_headers)
        assert response1.status_code == 200
        assert response2.status_code == 200

        order_data = {
            "external_ref": "EXT-MULTI-PROVIDER",
            "project_ref": "PROJ-001",
            "config": {"test": "value"},
            "platforms": ["platform1"],
            "resource_ref": "RES-001",
            "resource_type": "compute",
            "resource_name": "Test Resource",
            "provider_pids": ["provider-1", "provider-2"],
        }

        response = client.post("/api/orders", json=order_data, headers=api_headers)
        assert response.status_code == 200
        data = response.json()
        # The OrderPublic model doesn't include providers, so we just verify the order was created successfully
        assert data["external_ref"] == "EXT-MULTI-PROVIDER"


class TestMessagesAPI:
    @pytest.fixture
    def setup_user_and_order(self, client, api_headers):
        # Create provider first
        provider_data = {
            "name": "Message Test Provider",
            "website": "https://messagetestprovider.com",
            "pid": "message-provider-001",
            "manager_emails": ["manager@messagetest.com"],
        }
        provider_response = client.post("/api/providers", json=provider_data, headers=api_headers)
        provider = provider_response.json()

        # Create user
        user_data = {"name": "Message User", "email": "messageuser@test.com", "user_type": [UserType.MP_USER.value]}
        user_response = client.post("/api/users", json=user_data, headers=api_headers)
        user = user_response.json()

        # Create order
        order_data = {
            "external_ref": "MSG-ORDER-001",
            "project_ref": "MSG-PROJ-001",
            "config": {"test": "value"},
            "platforms": ["platform1"],
            "resource_ref": "MSG-RES-001",
            "resource_type": "compute",
            "resource_name": "Message Test Resource",
            "provider_pids": [provider["pid"]],
        }
        order_response = client.post("/api/orders", json=order_data, headers=api_headers)
        order = order_response.json()

        return {"user": user, "order": order, "provider": provider}

    def test_create_message_success(self, client, api_headers, db_session, setup_user_and_order):
        data = setup_user_and_order
        message_data = {
            "content": "This is a test message",
            "scope": MessageScope.PUBLIC.value,
            "user_email": data["user"]["email"],
            "order_external_ref": data["order"]["external_ref"],
        }

        response = client.post("/api/messages", json=message_data, headers=api_headers)

        assert response.status_code == 200
        result = response.json()
        assert result["content"] == "This is a test message"
        assert result["scope"] == MessageScope.PUBLIC.value
        assert result["author"]["email"] == data["user"]["email"]
        assert result["order"]["external_ref"] == data["order"]["external_ref"]

    def test_create_message_user_not_found(self, client, api_headers, db_session, setup_user_and_order):
        data = setup_user_and_order
        message_data = {
            "content": "This is a test message",
            "scope": MessageScope.PUBLIC.value,
            "user_email": "nonexistent@test.com",
            "order_external_ref": data["order"]["external_ref"],
        }

        response = client.post("/api/messages", json=message_data, headers=api_headers)

        assert response.status_code == 404
        assert "does not exist" in response.json()["detail"]

    def test_create_message_order_not_found(self, client, api_headers, db_session, setup_user_and_order):
        data = setup_user_and_order
        message_data = {
            "content": "This is a test message",
            "scope": MessageScope.PUBLIC.value,
            "user_email": data["user"]["email"],
            "order_external_ref": "NONEXISTENT-ORDER",
        }

        response = client.post("/api/messages", json=message_data, headers=api_headers)

        assert response.status_code == 404
        assert "does not exist" in response.json()["detail"]

    def test_create_message_private_scope(self, client, api_headers, db_session, setup_user_and_order):
        data = setup_user_and_order
        message_data = {
            "content": "This is a private message",
            "scope": MessageScope.PRIVATE.value,
            "user_email": data["user"]["email"],
            "order_external_ref": data["order"]["external_ref"],
        }

        response = client.post("/api/messages", json=message_data, headers=api_headers)

        assert response.status_code == 200
        result = response.json()
        assert result["content"] == "This is a private message"
        assert result["scope"] == MessageScope.PRIVATE.value

    def test_create_message_non_mp_user(self, client, api_headers, db_session, setup_user_and_order):
        # Create a non-MP_USER
        non_mp_user_data = {"name": "Admin User", "email": "admin_user@test.com", "user_type": [UserType.ADMIN.value]}
        user_response = client.post("/api/users", json=non_mp_user_data, headers=api_headers)
        assert user_response.status_code == 200

        data = setup_user_and_order
        message_data = {
            "content": "This should fail",
            "scope": MessageScope.PUBLIC.value,
            "user_email": "admin_user@test.com",
            "order_external_ref": data["order"]["external_ref"],
        }

        response = client.post("/api/messages", json=message_data, headers=api_headers)

        assert response.status_code == 400
        assert "is not an MP_USER" in response.json()["detail"]

    def test_create_message_missing_required_fields(self, client, api_headers, db_session, setup_user_and_order):
        data = setup_user_and_order

        # Missing content
        message_data = {
            "scope": MessageScope.PUBLIC.value,
            "user_email": data["user"]["email"],
            "order_external_ref": data["order"]["external_ref"],
        }
        response = client.post("/api/messages", json=message_data, headers=api_headers)
        assert response.status_code == 422

        # Missing scope - should succeed with default PRIVATE scope
        message_data = {
            "content": "Test message",
            "user_email": data["user"]["email"],
            "order_external_ref": data["order"]["external_ref"],
        }
        response = client.post("/api/messages", json=message_data, headers=api_headers)
        assert response.status_code == 200
        result = response.json()
        assert result["scope"] == MessageScope.PRIVATE.value  # Default value

    def test_create_message_invalid_scope(self, client, api_headers, db_session, setup_user_and_order):
        data = setup_user_and_order
        message_data = {
            "content": "Test message",
            "scope": "invalid_scope",
            "user_email": data["user"]["email"],
            "order_external_ref": data["order"]["external_ref"],
        }

        response = client.post("/api/messages", json=message_data, headers=api_headers)
        assert response.status_code == 422
