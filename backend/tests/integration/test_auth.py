from backend.auth import current_user
from backend.models.tables import User, UserType


def test_current_user_creates_new_user(db_session):
    user_payload = {"name": "New User", "email": "new.user@example.com"}

    user = current_user(token=user_payload, session=db_session)

    assert isinstance(user, User)
    assert user.id is not None
    assert user.name == "New User"
    assert user.email == "new.user@example.com"
    assert user.user_type == [UserType.MP_USER]

    persisted = db_session.get(User, user.id)
    assert persisted is not None
    assert persisted.email == "new.user@example.com"


def test_current_user_returns_existing_user(db_session):
    existing = User(
        name="Existing User",
        email="existing.user@example.com",
        user_type=[UserType.ADMIN],
    )
    db_session.add(existing)
    db_session.commit()

    token = {"name": "Ignored Name", "email": "existing.user@example.com"}

    user = current_user(token=token, session=db_session)

    assert user.id == existing.id
    assert user.name == "Existing User"
    assert user.user_type == [UserType.ADMIN]
