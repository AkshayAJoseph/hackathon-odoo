import pytest
from rest_framework.test import APIClient
from rest_framework.exceptions import ValidationError
from accounts.models import User
from accounts.services import signup


@pytest.mark.django_db
class TestSignupService:
    def test_successful_signup_creates_customer(self):
        user = signup(
            email="NewCustomer@BrightLoop.com",
            password="StrongPassword!123",
            name="Charlie Customer"
        )
        assert user.id is not None
        assert user.email == "newcustomer@brightloop.com"
        assert user.name == "Charlie Customer"
        assert user.role == "customer"
        assert user.check_password("StrongPassword!123")

    def test_signup_rejects_duplicate_email_case_insensitively(self):
        signup("duplicate@brightloop.com", "Password!123", "First User")
        with pytest.raises(ValidationError) as exc_info:
            signup("DUPLICATE@brightloop.com", "Password!456", "Second User")
        assert "email" in exc_info.value.detail

    def test_signup_validates_weak_password(self):
        with pytest.raises(ValidationError) as exc_info:
            signup("weak@brightloop.com", "short", "Weak User")
        assert "password" in exc_info.value.detail or any("more than 8" in str(e) for e in exc_info.value.detail)


@pytest.mark.django_db
class TestAuthViews:
    def setup_method(self):
        self.client = APIClient()

    def test_signup_endpoint_success(self):
        response = self.client.post('/api/auth/signup', {
            "email": "api_cust@brightloop.com",
            "password": "SecurePassword!999",
            "name": "API Customer"
        }, format='json')
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "api_cust@brightloop.com"
        assert data["role"] == "customer"
        assert "password" not in data

    def test_signup_endpoint_duplicate_email_returns_400(self):
        self.client.post('/api/auth/signup', {
            "email": "first@brightloop.com",
            "password": "SecurePassword!999",
            "name": "First"
        }, format='json')
        response = self.client.post('/api/auth/signup', {
            "email": "FIRST@brightloop.com",
            "password": "SecurePassword!999",
            "name": "Second"
        }, format='json')
        assert response.status_code == 400
        assert "email" in response.json()
        assert isinstance(response.json()["email"], list)

    def test_signup_endpoint_weak_password_returns_400(self):
        response = self.client.post('/api/auth/signup', {
            "email": "badpw@brightloop.com",
            "password": "weak",
            "name": "Bad Pw"
        }, format='json')
        assert response.status_code == 400
        assert "password" in response.json()
        assert isinstance(response.json()["password"], list)

    def test_jwt_login_contract_returns_access_refresh_role_name(self):
        # Anjali's Frontend Contract: { access, refresh, role, name }
        signup("jwt_user@brightloop.com", "SecurePassword!123", "JWT User")
        response = self.client.post('/api/auth/login', {
            "email": "jwt_user@brightloop.com",
            "password": "SecurePassword!123"
        }, format='json')
        assert response.status_code == 200
        data = response.json()
        assert "access" in data
        assert "refresh" in data
        assert data["role"] == "customer"
        assert data["name"] == "JWT User"

    def test_jwt_login_case_insensitive_email(self):
        signup("case_test@brightloop.com", "SecurePassword!123", "Case Tester")
        response = self.client.post('/api/auth/login', {
            "email": "CASE_TEST@brightloop.com",
            "password": "SecurePassword!123"
        }, format='json')
        assert response.status_code == 200
        assert response.json()["role"] == "customer"

    def test_jwt_login_invalid_credentials_returns_401(self):
        response = self.client.post('/api/auth/login', {
            "email": "nonexistent@brightloop.com",
            "password": "WrongPassword!123"
        }, format='json')
        assert response.status_code == 401

    def test_auth_me_endpoint_requires_token(self):
        # Unauthenticated request returns 401
        res_unauth = self.client.get('/api/auth/me')
        assert res_unauth.status_code == 401

        # Authenticated with JWT returns profile
        user = signup("me_user@brightloop.com", "SecurePassword!123", "Me User")
        login_res = self.client.post('/api/auth/login', {
            "email": "me_user@brightloop.com",
            "password": "SecurePassword!123"
        }, format='json')
        token = login_res.json()["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res_auth = self.client.get('/api/auth/me')
        assert res_auth.status_code == 200
        me_data = res_auth.json()
        assert me_data["id"] == user.id
        assert me_data["email"] == "me_user@brightloop.com"
        assert me_data["name"] == "Me User"
        assert me_data["role"] == "customer"

    def test_forgot_password_endpoint_always_200_same_response(self):
        # Enumeration safe: same response for existing and non-existing email
        res1 = self.client.post('/api/auth/forgot', {"email": "does_not_exist@brightloop.com"}, format='json')
        assert res1.status_code == 200
        msg1 = res1.json().get("message")

        signup("exists@brightloop.com", "Password!123", "Exists")
        res2 = self.client.post('/api/auth/forgot', {"email": "exists@brightloop.com"}, format='json')
        assert res2.status_code == 200
        msg2 = res2.json().get("message")

        assert msg1 == msg2

    def test_reset_password_endpoint_success(self):
        from accounts.services import generate_reset_token
        user = signup("reset_endpoint@brightloop.com", "OldPassword!123", "Reset Tester")
        uid, token = generate_reset_token(user)

        res = self.client.post('/api/auth/reset', {
            "uid": uid,
            "token": token,
            "new_password": "BrandNewPassword!999"
        }, format='json')
        assert res.status_code == 200
        assert "message" in res.json()

        # Login with new password works
        login_res = self.client.post('/api/auth/login', {
            "email": "reset_endpoint@brightloop.com",
            "password": "BrandNewPassword!999"
        }, format='json')
        assert login_res.status_code == 200

    def test_staff_create_admin_only_and_list(self):
        from accounts.models import User
        # 1. Anonymous returns 401
        res = self.client.post('/api/staff', {"email": "s1@brightloop.com", "password": "Password!123", "name": "S1"}, format='json')
        assert res.status_code == 401

        # 2. Customer gets 403
        cust = User.objects.create_user(email="cust_staff@brightloop.com", password="Password!123", role="customer")
        self.client.force_authenticate(user=cust)
        res_cust = self.client.post('/api/staff', {"email": "s2@brightloop.com", "password": "Password!123", "name": "S2"}, format='json')
        assert res_cust.status_code == 403

        # 3. Staff gets 403 on POST (Only admin can create staff)
        staff_u = User.objects.create_user(email="existing_staff@brightloop.com", password="Password!123", role="staff", is_staff=True)
        self.client.force_authenticate(user=staff_u)
        res_staff_post = self.client.post('/api/staff', {"email": "s3@brightloop.com", "password": "Password!123", "name": "S3"}, format='json')
        assert res_staff_post.status_code == 403

        # 4. Admin succeeds on POST
        admin = User.objects.create_superuser(email="admin_staff@brightloop.com", password="Password!123", name="Boss Admin")
        self.client.force_authenticate(user=admin)
        res_admin = self.client.post('/api/staff', {
            "email": "new_internal_staff@brightloop.com",
            "password": "SecureStaffPassword!123",
            "name": "Internal Staff Person"
        }, format='json')
        assert res_admin.status_code == 201
        data = res_admin.json()
        assert data["email"] == "new_internal_staff@brightloop.com"
        assert data["role"] == "staff"

        # 5. GET /api/staff lists staff members
        res_list = self.client.get('/api/staff')
        assert res_list.status_code == 200
        # Results are paginated: { "count": ..., "results": [...] }
        results = res_list.json().get("results", res_list.json())
        assert any(u["email"] == "new_internal_staff@brightloop.com" for u in results)
