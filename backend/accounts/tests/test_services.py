import pytest
from rest_framework.exceptions import ValidationError
from accounts.services import validate_password


class TestPasswordValidator:
    def test_valid_password_passes(self):
        # 9+ characters, 1 uppercase, 1 lowercase, 1 special
        assert validate_password("ValidPass1!") is True
        assert validate_password("SuperSecure#2026") is True

    def test_password_length_8_is_rejected(self):
        # Strictly more than 8 characters: length 8 must be rejected
        pw_len_8 = "Abc!5678"  # Exactly 8 characters
        assert len(pw_len_8) == 8
        with pytest.raises(ValidationError) as exc_info:
            validate_password(pw_len_8)
        errors = exc_info.value.detail
        assert any("more than 8 characters" in err for err in errors)

    def test_password_length_9_is_accepted(self):
        pw_len_9 = "Abc!56789"  # Exactly 9 characters
        assert len(pw_len_9) == 9
        assert validate_password(pw_len_9) is True

    def test_missing_uppercase_is_rejected(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_password("lowercase!123")
        errors = exc_info.value.detail
        assert any("uppercase" in err for err in errors)

    def test_missing_lowercase_is_rejected(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_password("UPPERCASE!123")
        errors = exc_info.value.detail
        assert any("lowercase" in err for err in errors)

    def test_missing_special_character_is_rejected(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_password("NoSpecialChar123")
        errors = exc_info.value.detail
        assert any("special character" in err for err in errors)

    def test_multiple_rule_failures_reported_together(self):
        # "short" fails length (< 9), uppercase, and special char
        with pytest.raises(ValidationError) as exc_info:
            validate_password("short")
        errors = exc_info.value.detail
        assert len(errors) >= 3
        err_text = " ".join(str(e) for e in errors)
        assert "more than 8 characters" in err_text
        assert "uppercase" in err_text
        assert "special character" in err_text


@pytest.mark.django_db
class TestPasswordResetServices:
    def test_request_password_reset_returns_none_whether_email_exists_or_not(self):
        from accounts.services import request_password_reset
        from django.core import mail
        
        # Nonexistent email
        mail.outbox.clear()
        assert request_password_reset("nonexistent@brightloop.com") is None
        assert len(mail.outbox) == 0

        # Existing user
        from accounts.models import User
        user = User.objects.create_user(email="reset_target@brightloop.com", password="OldPassword!123", name="Reset Target")
        assert request_password_reset("reset_target@brightloop.com") is None
        assert len(mail.outbox) == 1
        assert "reset_target@brightloop.com" in mail.outbox[0].to
        assert "reset" in mail.outbox[0].body.lower()

    def test_reset_password_success(self):
        from accounts.models import User
        from accounts.services import generate_reset_token, reset_password
        
        user = User.objects.create_user(email="reset_success@brightloop.com", password="OldPassword!123", name="Reset Success")
        uid, token = generate_reset_token(user)

        updated_user = reset_password(uid, token, "NewPassword!999")
        assert updated_user.check_password("NewPassword!999")

    def test_reset_password_single_use_token_rejected_on_reuse(self):
        from accounts.models import User
        from accounts.services import generate_reset_token, reset_password

        user = User.objects.create_user(email="single_use@brightloop.com", password="OldPassword!123")
        uid, token = generate_reset_token(user)

        # First use succeeds
        reset_password(uid, token, "NewPassword!999")

        # Second use fails because token is invalid/consumed
        with pytest.raises(ValidationError) as exc_info:
            reset_password(uid, token, "AnotherPassword!999")
        assert "token" in exc_info.value.detail or "expired" in str(exc_info.value.detail).lower()

    def test_reset_password_weak_password_rejected(self):
        from accounts.models import User
        from accounts.services import generate_reset_token, reset_password

        user = User.objects.create_user(email="weak_reset@brightloop.com", password="OldPassword!123")
        uid, token = generate_reset_token(user)

        with pytest.raises(ValidationError) as exc_info:
            reset_password(uid, token, "short")
        assert "new_password" in exc_info.value.detail or "password" in str(exc_info.value.detail).lower()


@pytest.mark.django_db
class TestStaffService:
    def test_create_staff_by_admin_success(self):
        from accounts.models import User
        from accounts.services import create_staff

        admin = User.objects.create_superuser(email="admin_creator@brightloop.com", password="AdminPassword!123", name="Super Admin")
        staff_user = create_staff(admin, {
            "email": "new_staff@brightloop.com",
            "password": "StaffPassword!123",
            "name": "Staff Member"
        })
        assert staff_user.id is not None
        assert staff_user.role == "staff"
        assert staff_user.is_staff is True
        assert staff_user.email == "new_staff@brightloop.com"

    def test_create_staff_by_non_admin_raises_permission_denied(self):
        from rest_framework.exceptions import PermissionDenied
        from accounts.models import User
        from accounts.services import create_staff

        staff = User.objects.create_user(email="staff1@brightloop.com", password="Password!123", role="staff")
        customer = User.objects.create_user(email="cust1@brightloop.com", password="Password!123", role="customer")

        with pytest.raises(PermissionDenied):
            create_staff(staff, {"email": "illegal1@brightloop.com", "password": "Password!123", "name": "Illegal"})

        with pytest.raises(PermissionDenied):
            create_staff(customer, {"email": "illegal2@brightloop.com", "password": "Password!123", "name": "Illegal"})
