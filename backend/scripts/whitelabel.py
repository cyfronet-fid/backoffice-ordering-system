from sqlmodel import select

from backend.config import get_settings
from backend.db import get_session
from backend.models.tables import Message, Order, UserType
from backend.services.call_whitelabel import change_order_status, post_message
from scripts.utils import run_command


def generate_client() -> None:
    # Run and then copy only what you need from ./out/whitelabel_client into $ROOT_DIR$/whitelabel_client
    # Also, you have to have openapi-generator installed and in PATH (https://openapi-generator.tech/docs/installation)
    run_command(
        (
            f"openapi-generator generate "
            f"-i {get_settings().whitelabel_endpoint}/api_docs/swagger/v1/ordering_swagger.json "
            f"-o ./out "
            f"-g python "
            f"--additional-properties=generateSourceCodeOnly=true,packageName=whitelabel_client "
        )
    )
    print("Client generated in ./out dir...")


def retry_sync() -> None:
    with get_session() as session:
        unsync_orders = session.exec(select(Order).where(Order.synced == False)).all()

    for o in unsync_orders:
        print(f"Syncing order {o.id}...")
        change_order_status(order_id=o.id)

    with get_session() as session:
        unsync_messages = session.exec(select(Message).where(Message.synced == False)).all()
        unsync_messages_send_as = [
            # "strongest" (coordinator) role takes precedent
            UserType.COORDINATOR if UserType.COORDINATOR in m.author.user_type else UserType.PROVIDER_MANAGER
            for m in unsync_messages
        ]

    for m, send_as in zip(unsync_messages, unsync_messages_send_as):
        print(f"Syncing message {m.id}...")
        post_message(message_id=m.id, send_as=send_as)

    print("Everything is synced!")
