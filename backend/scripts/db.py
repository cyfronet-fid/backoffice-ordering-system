from sqlmodel import delete, SQLModel

from backend.db import get_session
from backend.models.tables import Message, Order, OrderStatus, Provider, User, UserType, MessageScope


def seed():
    with get_session() as session:
        admin = User(name="HAL 9000", email="admin@cyfronet.pl", user_type=[UserType.ADMIN, UserType.COORDINATOR])
        coordinator = User(name="Mr. Uptight", email="coordinator@cyfronet.pl", user_type=[UserType.COORDINATOR])
        alice_provider = User(name="Alice", email="alice@provider.com", user_type=[UserType.PROVIDER_MANAGER])
        bob_provider = User(name="Bob", email="bob@provider.com", user_type=[UserType.PROVIDER_MANAGER])
        joe = User(name="Joe Moe", email="joe@gmail.com", user_type=[UserType.MP_USER])
        jane = User(name="Jane Doe", email="jane@gmail.com", user_type=[UserType.MP_USER])

        gcp_provider = Provider(
            name="Google Cloud Platform",
            website="https://cloud.google.com",
            managers=[alice_provider],
            pid="gcp",
        )
        aws_provider = Provider(
            name="AWS", website="https://aws.amazon.com", managers=[alice_provider, bob_provider], pid="aws"
        )
        null_provider = Provider(name="Lonely", website="https://example.com", pid="lone")

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
        message2 = Message(
            content="Worry not, my child. Your access is coming.",
            author=alice_provider,
            order=order1,
            scope=MessageScope.PUBLIC,
        )
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

        order3 = Order(
            external_ref="additional",
            project_ref="additional",
            status=OrderStatus.COMPLETED,
            config={"cpus": 256, "memory": 1024, "GPU": "H100"},
            platforms=["my plat"],
            resource_ref="additional",
            resource_type="order_required",
            resource_name="EC2-AI-Training",
            users=[jane, bob_provider],
            providers=[aws_provider],
        )

        message4 = Message(
            content="The configuration you want is outrageous...",
            author=alice_provider,
            order=order2,
            scope=MessageScope.PUBLIC,
        )
        message5 = Message(content="+1", author=bob_provider, order=order2)

        patryk = User(
            email="patryk@gmail.com",
            name="Patryk",
            user_type=[UserType.PROVIDER_MANAGER, UserType.MP_USER],
        )
        egi = Provider(name="EGI", website="https://egi-federation.com/", managers=[patryk], pid="egi-federation")

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
                null_provider,
                order1,
                order2,
                order3,
                message1,
                message2,
                message3,
                message4,
                message5,
                patryk,
                egi,
            ]
        )
        session.commit()


def clear():
    with get_session() as session:
        for table in reversed(SQLModel.metadata.sorted_tables):  # Reverse order to respect FK constraints
            session.exec(delete(table))
        session.commit()
