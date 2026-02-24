import factory
from factory.alchemy import SQLAlchemyModelFactory

from backend.models.tables import Message, MessageScope, Order, Provider, User, UserType


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = None  # bound per-test via bind_factories fixture
        sqlalchemy_session_persistence = "flush"

    name = factory.Faker("name")
    email = factory.Sequence(lambda n: f"user{n}@test.com")
    user_type = factory.LazyFunction(lambda: [UserType.MP_USER])


class AdminUserFactory(UserFactory):
    email = factory.Sequence(lambda n: f"admin{n}@test.com")
    user_type = factory.LazyFunction(lambda: [UserType.ADMIN])


class CoordinatorUserFactory(UserFactory):
    email = factory.Sequence(lambda n: f"coordinator{n}@test.com")
    user_type = factory.LazyFunction(lambda: [UserType.COORDINATOR])


class ProviderManagerUserFactory(UserFactory):
    email = factory.Sequence(lambda n: f"pm{n}@test.com")
    user_type = factory.LazyFunction(lambda: [UserType.PROVIDER_MANAGER])


class ProviderFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Provider
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"

    name = factory.Sequence(lambda n: f"Provider {n}")
    website = factory.Faker("url")
    pid = factory.Sequence(lambda n: f"prov-{n:03d}")


class OrderFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Order
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"

    external_ref = factory.Sequence(lambda n: f"ext-{n:03d}")
    project_ref = factory.Sequence(lambda n: f"proj-{n:03d}")
    config = factory.LazyFunction(dict)
    platforms = factory.LazyFunction(lambda: ["linux"])
    resource_ref = factory.Sequence(lambda n: f"res-{n:03d}")
    resource_type = "vm"
    resource_name = factory.Faker("word")

    # M2M relationships: pass lists explicitly, e.g. OrderFactory(providers=[p], users=[u])
    @factory.post_generation
    def providers(self, create, extracted, **kwargs):
        if extracted:
            self.providers.extend(extracted)

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        if extracted:
            self.users.extend(extracted)


class MessageFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Message
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"

    content = factory.Faker("sentence")
    scope = MessageScope.PRIVATE
    order = factory.SubFactory(OrderFactory)
    author = factory.SubFactory(UserFactory)
