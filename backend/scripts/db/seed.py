from config import get_settings
from sqlmodel import Session, create_engine

from app.models.tables import Message, Order, OrderStatus, User, UserType, Provider

if __name__ == "__main__":
    engine = create_engine(get_settings().db_connection_string)

    with Session(engine) as session:
        admin = User(name="admin", email="admin@cyfronet.pl", user_type=[UserType.ADMIN])
        coordinator = User(name="coordinator", email="coordinator@cyfronet.pl", user_type=[UserType.COORDINATOR])
        alice_provider = User(name="alice", email="alice@provider.com", user_type=[UserType.PROVIDER_MANAGER])
        bob_provider = User(name="bob", email="bob@provider.com", user_type=[UserType.PROVIDER_MANAGER])
        joe = User(name="joe moe", email="joe@gmail.com", user_type=[UserType.MP_USER])
        jane = User(name="jane doe", email="jane@gmail.com", user_type=[UserType.MP_USER])

        gcp_provider = Provider(
            name="Google Cloud Platform",
            website="https://cloud.google.com",
            managers=[alice_provider],
        )
        aws_provider = Provider(
            name="AWS",
            website="https://aws.amazon.com",
            managers=[alice_provider, bob_provider],
        )

        order1 = Order(
            external_ref="/project/joes_project/order/1",
            project_ref="/project/joes_project",
            status=OrderStatus.SUBMITTED,
            config={"cpus": 2, "memory": 4},
            platforms=[],
            resource_ref="resources/cool_resource",
            resource_type="order_required",
            resource_name="Google Compute Engine",
            users=[joe, alice_provider, coordinator],
            providers=[gcp_provider],
        )

        message1 = Message(content="Ey where my resource at?!", author=joe, order=order1)
        message2 = Message(content="Worry not, my child. Your access is coming.", author=alice_provider, order=order1)
        message3 = Message(content="What the hell is going on here?", author=coordinator, order=order1)

        order2 = Order(
            external_ref="/project/janes_project/order/1",
            project_ref="/project/janes_project",
            status=OrderStatus.PROCESSING,
            config={"cpus": 256, "memory": 1024},
            platforms=["my plat"],
            resource_ref="resources/nice_resource",
            resource_type="order_required",
            resource_name="EC2",
            users=[jane, alice_provider, bob_provider],
            providers=[aws_provider],
        )

        message4 = Message(content="The configuration you want is outrageous...", author=alice_provider, order=order2)
        message5 = Message(content="+1", author=bob_provider, order=order2)

        session.add_all(
            [
                admin,
                coordinator,
                alice_provider,
                bob_provider,
                joe,
                jane,
                gcp_provider,
                aws_provider,
                order1,
                order2,
                message1,
                message2,
                message3,
                message4,
                message5,
            ]
        )
        session.commit()
