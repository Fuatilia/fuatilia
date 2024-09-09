import pytest
from apps.users.models import User
from tests.factories import UserFactory


pytestmark = pytest.mark.django_db


def test_user_factory(user_factory):
    assert user_factory is UserFactory


def test_super_user(super_user_fixt):
    assert super_user_fixt.username == "test_superuser"
    assert isinstance(super_user_fixt, User)


def test_admin_user(admin_user_fixt):
    assert admin_user_fixt.username == "test_adminuser"
    assert isinstance(admin_user_fixt, User)


def test_app_user(app_user_fixt):
    app_data = app_user_fixt.get("data")
    assert app_data.get("username") == "test_appuser"
    assert app_data.get("client_id") is not None
    assert app_data.get("client_secret") is not None
