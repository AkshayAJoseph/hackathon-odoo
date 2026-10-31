import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_defaults_to_customer(self):
        user = User.objects.create_user(
            email="CUSTOMER@BrightLoop.com",
            password="StrongPassword!123",
            name="Alice Customer"
        )
        assert user.id is not None
        assert user.email == "customer@brightloop.com"
        assert user.name == "Alice Customer"
        assert user.role == "customer"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password("StrongPassword!123")

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@brightloop.com",
            password="AdminPassword!123",
            name="Admin User"
        )
        assert admin.role == "admin"
        assert admin.is_staff is True
        assert admin.is_superuser is True

    def test_duplicate_email_case_insensitive_rejected(self):
        User.objects.create_user(
            email="user@brightloop.com",
            password="Password!123",
            name="User One"
        )
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="USER@brightloop.com",
                password="Password!456",
                name="User Two"
            )
