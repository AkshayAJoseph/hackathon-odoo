import pytest
from unittest.mock import Mock
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory

from core.models import AuditLog
from core.services import log_transition, scoped_queryset
from core.permissions import IsAdmin, IsStaffOrAdmin, IsCustomerOwner
from core.pagination import StandardResultsSetPagination

User = get_user_model()


@pytest.mark.django_db
class TestAuditLogAndTransition:
    def test_create_audit_log_with_actor(self):
        user = User.objects.create_user(email='tester@brightloop.com', name='Tester User')
        log = log_transition(
            actor=user,
            entity='Subscription',
            entity_id='SUB-00001',
            from_status='draft',
            to_status='quotation'
        )
        assert log.id is not None
        assert log.actor == user
        assert log.entity == 'Subscription'
        assert log.entity_id == 'SUB-00001'
        assert log.from_status == 'draft'
        assert log.to_status == 'quotation'
        assert log.timestamp is not None

    def test_log_transition_system_actor_none(self):
        # Billing engine auto_close passes user=None
        log = log_transition(
            actor=None,
            entity='Subscription',
            entity_id='SUB-00002',
            from_status='active',
            to_status='closed'
        )
        assert log.id is not None
        assert log.actor is None
        assert log.from_status == 'active'
        assert log.to_status == 'closed'


@pytest.mark.django_db
class TestScopedQueryset:
    def test_anonymous_user_gets_none(self):
        user = User.objects.create_user(email='admin@brightloop.com', name='Admin User')
        log_transition(actor=user, entity='Subscription', entity_id='1', from_status='draft', to_status='active')
        
        anon = AnonymousUser()
        qs = scoped_queryset(anon, AuditLog.objects.all())
        assert qs.count() == 0

    def test_admin_and_staff_see_all(self):
        user1 = User.objects.create_user(email='u1@brightloop.com', name='User One')
        user2 = User.objects.create_user(email='u2@brightloop.com', name='User Two')
        log_transition(actor=user1, entity='Subscription', entity_id='1', from_status='draft', to_status='active')
        log_transition(actor=user2, entity='Subscription', entity_id='2', from_status='draft', to_status='active')

        admin_mock = Mock()
        admin_mock.is_authenticated = True
        admin_mock.is_superuser = False
        admin_mock.is_staff = False
        admin_mock.role = 'admin'

        staff_mock = Mock()
        staff_mock.is_authenticated = True
        staff_mock.is_superuser = False
        staff_mock.is_staff = False
        staff_mock.role = 'staff'

        assert scoped_queryset(admin_mock, AuditLog.objects.all()).count() == 2
        assert scoped_queryset(staff_mock, AuditLog.objects.all()).count() == 2

    def test_customer_scoped_to_own_records(self):
        u1 = User.objects.create_user(email='cust1@brightloop.com', name='Cust One')
        u2 = User.objects.create_user(email='cust2@brightloop.com', name='Cust Two')
        l1 = log_transition(actor=u1, entity='Subscription', entity_id='1', from_status='draft', to_status='active')
        l2 = log_transition(actor=u2, entity='Subscription', entity_id='2', from_status='draft', to_status='active')

        # Test with custom model user having role 'customer'
        cust_user = u1
        cust_user.role = 'customer'
        
        qs = scoped_queryset(cust_user, AuditLog.objects.all(), user_field='actor')
        assert qs.count() == 1
        assert qs.first().id == l1.id


class TestCorePermissions:
    def setup_method(self):
        self.factory = APIRequestFactory()

    def test_is_admin_permission(self):
        perm = IsAdmin()
        request = self.factory.get('/api/admin-only')
        
        anon = AnonymousUser()
        request.user = anon
        assert not perm.has_permission(request, None)

        staff = Mock(is_authenticated=True, role='staff', is_superuser=False)
        request.user = staff
        assert not perm.has_permission(request, None)

        customer = Mock(is_authenticated=True, role='customer', is_superuser=False)
        request.user = customer
        assert not perm.has_permission(request, None)

        admin = Mock(is_authenticated=True, role='admin', is_superuser=False)
        request.user = admin
        assert perm.has_permission(request, None)

        superuser = Mock(is_authenticated=True, role='other', is_superuser=True)
        request.user = superuser
        assert perm.has_permission(request, None)

    def test_is_staff_or_admin_permission(self):
        perm = IsStaffOrAdmin()
        request = self.factory.get('/api/staff-resource')

        customer = Mock(is_authenticated=True, role='customer', is_staff=False, is_superuser=False)
        request.user = customer
        assert not perm.has_permission(request, None)

        staff = Mock(is_authenticated=True, role='staff', is_staff=False, is_superuser=False)
        request.user = staff
        assert perm.has_permission(request, None)

        admin = Mock(is_authenticated=True, role='admin', is_staff=False, is_superuser=False)
        request.user = admin
        assert perm.has_permission(request, None)

    def test_is_customer_owner_permission(self):
        perm = IsCustomerOwner()
        request = self.factory.get('/api/resource/1')

        user1 = Mock(is_authenticated=True, role='customer', is_staff=False, is_superuser=False)
        user2 = Mock(is_authenticated=True, role='customer', is_staff=False, is_superuser=False)
        request.user = user1

        obj_owned = Mock(customer=user1)
        obj_other = Mock(customer=user2)

        assert perm.has_object_permission(request, None, obj_owned)
        assert not perm.has_object_permission(request, None, obj_other)


class TestPagination:
    def test_pagination_page_size(self):
        paginator = StandardResultsSetPagination()
        assert paginator.page_size == 25
        assert paginator.page_size_query_param == 'page_size'
        assert paginator.max_page_size == 100
