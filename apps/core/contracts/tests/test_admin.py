import io
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.core.files.base import ContentFile

from apps.core.models import Tenant
from apps.core.contracts.models import Contract
from apps.core.contracts.admin import ContractAdmin


class DummyAdminSite(AdminSite):
    site_header = "Test Admin"


class ContractAdminTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = DummyAdminSite()
        self.admin = ContractAdmin(Contract, self.site)
        self.tenant = Tenant.objects.create(name="T1", subdomain="t1", is_active=True)
        User = get_user_model()
        self.user = User.objects.create_user(username="staff", password="x", is_staff=True)
        setattr(self.user, "tenant", self.tenant)

    def test_save_model_autoassigns_tenant(self):
        request = self.factory.post("/admin/")
        request.user = self.user
        contract = Contract(
            title="C1",
            contract_type="PHOTO",
            status="DRAFT",
            amount=0,
            start_date="2024-01-01",
            client_name="Cliente X",
        )
        self.admin.save_model(request, contract, form=None, change=False)
        self.assertEqual(contract.tenant, self.tenant)

    def test_queryset_filtered_by_tenant(self):
        request = self.factory.get("/admin/")
        request.user = self.user
        c1 = Contract.objects.create(
            tenant=self.tenant,
            title="C1",
            contract_type="PHOTO",
            status="DRAFT",
            amount=10,
            start_date="2024-01-01",
            client_name="Cliente X",
        )
        t2 = Tenant.objects.create(name="T2", subdomain="t2", is_active=True)
        Contract.objects.create(
            tenant=t2,
            title="C2",
            contract_type="FRAME",
            status="ACTIVE",
            amount=20,
            start_date="2024-02-01",
            client_name="Cliente Y",
        )
        qs = self.admin.get_queryset(request)
        self.assertEqual(list(qs), [c1])