from unittest.mock import MagicMock, patch

import pytest

from backend.exceptions import NotFoundException
from backend.models.tables import Message, Order, OrderStatus, User, UserType
from backend.services import call_whitelabel
from whitelabel_client import ProjectItemUpdate as PIU


def _make_message():
    order = Order(
        external_ref="123",
        project_ref="456",
        config={},
        platforms=["linux"],
        resource_ref="r1",
        resource_type="vm",
        resource_name="name",
    )
    author = User(name="Author", email="author@example.com", user_type=[UserType.MP_USER])
    return Message(content="hello", order=order, author=author)


@patch("backend.services.call_whitelabel.whitelabel_client.ApiClient")
@patch("backend.services.call_whitelabel.whitelabel_client.MessagesApi")
@patch("backend.services.call_whitelabel.get_settings")
def test_post_message_builds_correct_payload(mock_get_settings, mock_messages_api_cls, mock_api_client_cls):
    mock_get_settings.return_value.whitelabel_default_oms_id = 1

    mock_api_client = MagicMock()
    mock_api_client_cls.return_value.__enter__.return_value = mock_api_client

    api_instance = MagicMock()
    mock_messages_api_cls.return_value = api_instance

    message = _make_message()

    post_message_fn = call_whitelabel._post_message.__wrapped__
    post_message_fn(message, UserType.COORDINATOR)

    api_instance.api_v1_oms_oms_id_messages_post.assert_called_once()
    _, kwargs = api_instance.api_v1_oms_oms_id_messages_post.call_args
    assert kwargs["oms_id"] == "1"
    mw = kwargs["message_write"]
    assert mw.project_id == int(message.order.project_ref)
    assert mw.project_item_id == int(message.order.external_ref)
    assert mw.content == message.content
    assert mw.scope == "public"
    assert mw.author.email == message.author.email
    assert mw.author.name == message.author.name
    assert mw.author.role == "mediator"


@patch("backend.services.call_whitelabel.whitelabel_client.ApiClient")
@patch("backend.services.call_whitelabel.whitelabel_client.ProjectItemsApi")
@patch("backend.services.call_whitelabel.get_settings")
def test_change_order_status_builds_correct_payload(mock_get_settings, mock_project_items_api_cls, mock_api_client_cls):
    mock_get_settings.return_value.whitelabel_default_oms_id = 1

    mock_api_client = MagicMock()
    mock_api_client_cls.return_value.__enter__.return_value = mock_api_client

    api_instance = MagicMock()
    mock_project_items_api_cls.return_value = api_instance

    order = Order(
        external_ref="ext-1",
        project_ref="proj-1",
        config={},
        platforms=["linux"],
        resource_ref="r1",
        resource_type="vm",
        resource_name="name",
        status=OrderStatus.SUBMITTED,
    )

    change_status_fn = call_whitelabel._change_order_status.__wrapped__
    change_status_fn(order)

    api_instance.api_v1_oms_oms_id_projects_pid_project_items_pi_id_patch.assert_called_once()
    _, kwargs = api_instance.api_v1_oms_oms_id_projects_pid_project_items_pi_id_patch.call_args
    assert kwargs["oms_id"] == "1"
    assert kwargs["p_id"] == order.project_ref
    assert kwargs["pi_id"] == order.external_ref

    assert isinstance(kwargs["project_item_update"], PIU)


@patch("backend.services.call_whitelabel.get_session")
def test_wl_sync_wrapper_marks_entity_synced_on_success(mock_get_session):
    entity = MagicMock()
    entity.id = 1
    entity_cls = MagicMock()
    entity_cls.__name__ = "Message"

    session = MagicMock()
    session.get.return_value = entity
    mock_get_session.return_value.__enter__.return_value = session

    def sync_fn(e):
        assert e is entity

    call_whitelabel._wl_sync_wrapper(entity_cls, 1, sync_fn)

    assert entity.synced is True
    assert session.commit.call_count >= 2


@patch("backend.services.call_whitelabel.logger")
@patch("backend.services.call_whitelabel.get_session")
def test_wl_sync_wrapper_logs_and_raises_when_final_commit_fails(mock_get_session, mock_logger):
    entity = MagicMock()
    entity.id = 2
    entity_cls = MagicMock()
    entity_cls.__name__ = "Message"

    session = MagicMock()
    session.get.return_value = entity
    session.commit.side_effect = [None, Exception("db error")]
    mock_get_session.return_value.__enter__.return_value = session

    def sync_fn(e):
        assert e is entity

    with pytest.raises(Exception, match="db error"):
        call_whitelabel._wl_sync_wrapper(entity_cls, 2, sync_fn)

    mock_logger.exception.assert_called_once()


@patch("backend.services.call_whitelabel.get_session")
def test_wl_sync_wrapper_raises_not_found_for_missing_entity(mock_get_session):
    entity_cls = MagicMock()
    entity_cls.__name__ = "Order"

    session = MagicMock()
    session.get.return_value = None
    mock_get_session.return_value.__enter__.return_value = session

    with pytest.raises(NotFoundException):
        call_whitelabel._wl_sync_wrapper(entity_cls, 123, lambda e: None)


@patch("backend.services.call_whitelabel._post_message")
@patch("backend.services.call_whitelabel.get_session")
def test_post_message_uses_wl_sync_wrapper(mock_get_session, mock_post_message):
    entity = MagicMock()
    entity.id = 5
    session = MagicMock()
    session.get.return_value = entity
    mock_get_session.return_value.__enter__.return_value = session

    call_whitelabel.post_message(5, UserType.PROVIDER_MANAGER)

    mock_post_message.assert_called_once()


@patch("backend.services.call_whitelabel._change_order_status")
@patch("backend.services.call_whitelabel.get_session")
def test_change_order_status_uses_wl_sync_wrapper(mock_get_session, mock_change_order_status):
    entity = MagicMock()
    entity.id = 7
    session = MagicMock()
    session.get.return_value = entity
    mock_get_session.return_value.__enter__.return_value = session

    call_whitelabel.change_order_status(7)

    mock_change_order_status.assert_called_once()
