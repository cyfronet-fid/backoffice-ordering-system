import logging
from typing import Literal

from tenacity import after_log, retry, retry_if_exception_type, stop_after_delay, wait_random_exponential

import whitelabel_client
from backend.config import get_settings
from backend.const import WHITELABEL_ORDER_STATUS_MAPPING
from backend.db import get_session
from backend.exceptions import NotFoundException
from backend.models.tables import Message, Order, UserType
from whitelabel_client import ApiException, MessageWrite, MessageWriteAuthor, ProjectItemUpdate

logger = logging.getLogger(__name__)

configuration = whitelabel_client.Configuration(
    host=get_settings().whitelabel_endpoint,
    api_key={"authentication_token": get_settings().whitelabel_client_key},
)


MAX_RETRY_DELAY = get_settings().whitelabel_max_retry_delay_s


@retry(
    reraise=True,
    retry=retry_if_exception_type(ApiException),
    wait=wait_random_exponential(multiplier=0.5, max=30),
    stop=stop_after_delay(max_delay=MAX_RETRY_DELAY),
    after=after_log(logger, logging.WARNING),
)
def _post_message(message: Message, send_as: Literal[UserType.PROVIDER_MANAGER, UserType.COORDINATOR]) -> None:
    with whitelabel_client.ApiClient(configuration) as api_client:
        api_instance = whitelabel_client.MessagesApi(api_client)
        api_instance.api_v1_oms_oms_id_messages_post(
            oms_id=str(get_settings().whitelabel_default_oms_id),
            message_write=MessageWrite(
                project_id=int(message.order.project_ref),  # type: ignore
                project_item_id=int(message.order.external_ref),  # type: ignore
                content=message.content,
                scope="public",
                author=MessageWriteAuthor(
                    email=message.author.email,  # type: ignore
                    name=message.author.name,  # type: ignore
                    role="mediator" if send_as == UserType.COORDINATOR else "provider",
                ),
            ),
        )


@retry(
    reraise=True,
    retry=retry_if_exception_type(ApiException),
    wait=wait_random_exponential(multiplier=0.5, max=30),
    stop=stop_after_delay(MAX_RETRY_DELAY),
    after=after_log(logger, logging.WARNING),
)
def _change_order_status(order: Order) -> None:
    with whitelabel_client.ApiClient(configuration) as api_client:
        api_instance = whitelabel_client.ProjectItemsApi(api_client)
        api_instance.api_v1_oms_oms_id_projects_pid_project_items_pi_id_patch(
            oms_id=str(get_settings().whitelabel_default_oms_id),
            p_id=order.project_ref,
            pi_id=order.external_ref,
            project_item_update=ProjectItemUpdate(
                {
                    "status": {
                        "value": WHITELABEL_ORDER_STATUS_MAPPING[order.status],
                        "type": WHITELABEL_ORDER_STATUS_MAPPING[order.status],
                    }
                }
            ),
        )


def _wl_sync_wrapper(entity_cls, entity_id, sync_fn):  # type: ignore
    with get_session() as session:
        entity = session.get(entity_cls, entity_id, with_for_update=True)
        if entity is None:
            raise NotFoundException(f"{entity_cls.__name__} {entity_id} not found")

        entity.synced = False
        session.commit()

        # TODO: Remember about the potential DB session block here if it ever becomes a problem
        sync_fn(entity)

        entity.synced = True
        try:
            session.commit()
        except Exception:
            logger.exception("Could not mark %s %s as synced", entity_cls.__name__, entity_id)
            raise


def post_message(message_id: int, send_as: Literal[UserType.PROVIDER_MANAGER, UserType.COORDINATOR]) -> None:
    _wl_sync_wrapper(Message, message_id, lambda m: _post_message(m, send_as))


def change_order_status(order_id: int) -> None:
    _wl_sync_wrapper(Order, order_id, _change_order_status)
