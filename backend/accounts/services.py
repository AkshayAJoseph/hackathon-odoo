import re
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from accounts.models import User

token_generator = PasswordResetTokenGenerator()

def generate_reset_token(user: User) -> tuple[str, str]:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    return uid, token

def request_password_reset(email: str) -> None:
    """
    Sends a signed single-use reset token to the given email if it exists.
    Always returns None to prevent email enumeration.
    """
    if not email:
        return None
    email_clean = email.strip().lower()
    try:
        user = User.objects.get(email__iexact=email_clean, is_active=True)
        uid, token = generate_reset_token(user)
        reset_link = f"/auth/reset-password?uid={uid}&token={token}"
        send_mail(
            subject="Password Reset Request - Brightloop",
            message=f"Hello {user.name or 'Customer'},\n\nClick the link below to reset your password:\n{reset_link}\n\nThis link is valid for 30 minutes.",
            from_email="noreply@brightloop.com",
            recipient_list=[user.email],
            fail_silently=True,
        )
    except User.DoesNotExist:
        pass
    return None

def reset_password(uid: str, token: str, new_password: str) -> User:
    """
    Validates token and single-use constraint, checks new password strength,
    and updates the user's password.
    """
    try:
        validate_password(new_password)
    except ValidationError as e:
        raise ValidationError({"new_password": e.detail if isinstance(e.detail, list) else [str(e)]})

    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        raise ValidationError({"token": ["Invalid or expired reset token."]})

    if not token_generator.check_token(user, token):
        raise ValidationError({"token": ["Invalid or expired reset token."]})

    user.set_password(new_password)
    user.save(update_fields=['password'])
    return user


def create_staff(admin_user: User, data: dict) -> User:
    """
    Creates a new staff user. Only admins can create staff.
    """
    if not admin_user or not getattr(admin_user, 'is_authenticated', False):
        raise PermissionDenied("Authentication required.")
    if getattr(admin_user, 'role', None) != 'admin' and not getattr(admin_user, 'is_superuser', False):
        raise PermissionDenied("Only administrators can create staff accounts.")

    email = data.get('email', '')
    if not email:
        raise ValidationError({"email": ["Email address is required."]})
    email_clean = email.strip().lower()

    if User.objects.filter(email__iexact=email_clean).exists():
        raise ValidationError({"email": ["An account with this email already exists."]})

    password = data.get('password', '')
    try:
        validate_password(password)
    except ValidationError as e:
        raise ValidationError({"password": e.detail if isinstance(e.detail, list) else [str(e)]})

    name = data.get('name', '')
    if isinstance(name, str):
        name = name.strip()
    else:
        name = ''

    return User.objects.create_user(
        email=email_clean,
        password=password,
        name=name,
        role='staff',
        is_staff=True
    )


def validate_password(password: str) -> bool:
    """
    Validates password against Brightloop security rules:
    - Strictly more than 8 characters (8 is rejected, 9+ accepted).
    - At least 1 uppercase letter (A-Z).
    - At least 1 lowercase letter (a-z).
    - At least 1 special character.
    Returns True if valid, or raises ValidationError with a list of all broken rules.
    """
    if not isinstance(password, str):
        raise ValidationError(["Password must be a valid string."])

    errors = []

    # Rule 1: Strictly more than 8 characters (length > 8)
    if len(password) <= 8:
        errors.append("Password must be more than 8 characters long.")

    # Rule 2: At least 1 uppercase letter
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter.")

    # Rule 3: At least 1 lowercase letter
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter.")

    # Rule 4: At least 1 special character (non-alphanumeric)
    if not re.search(r'[^A-Za-z0-9]', password):
        errors.append("Password must contain at least one special character.")

    if errors:
        raise ValidationError(errors)

    return True


def signup(email: str, password: str, name: str = '') -> User:
    """
    Creates a new user with customer role.
    Validates password and ensures email uniqueness (case-insensitive).
    """
    if not email:
        raise ValidationError({"email": ["Email address is required."]})
    email_clean = email.strip().lower()

    if User.objects.filter(email__iexact=email_clean).exists():
        raise ValidationError({"email": ["An account with this email already exists."]})

    try:
        validate_password(password)
    except ValidationError as e:
        raise ValidationError({"password": e.detail if isinstance(e.detail, list) else [str(e)]})

    return User.objects.create_user(
        email=email_clean,
        password=password,
        name=name.strip() if name else '',
        role='customer'
    )

