import json
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from .models import Membership, Organization, Store


class OrganizationSelectionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="owner", password="example-test-password")
        self.org1 = Organization.objects.create(name="Negocio Uno")
        self.org2 = Organization.objects.create(name="Negocio Dos")
        Membership.objects.create(organization=self.org1, user=self.user, role="owner")
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.user)

    def csrf(self):
        self.client.get("/api/session/")
        return self.client.cookies["csrftoken"].value

    def test_can_select_a_member_organization(self):
        token = self.csrf()
        response = self.client.post("/api/organization/select/", json.dumps({"organization_id": str(self.org1.id)}),
                                    content_type="application/json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/session/").json()["active_organization_id"], str(self.org1.id))

    def test_cannot_select_another_business(self):
        token = self.csrf()
        response = self.client.post("/api/organization/select/", json.dumps({"organization_id": str(self.org2.id)}),
                                    content_type="application/json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 403)

    def test_switch_requires_csrf(self):
        response = self.client.post("/api/organization/select/", json.dumps({"organization_id": str(self.org1.id)}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 403)


from rest_framework.test import APITestCase


class ManagementAPITests(APITestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="org-owner", password="SampleTestingPassword!123")
        self.other = Organization.objects.create(name="Competidor")
        self.org = Organization.objects.create(name="Nuestra empresa")
        Membership.objects.create(organization=self.org, user=self.owner, role="owner")
        Store.objects.create(organization=self.other, name="Sucursal ajena")
        self.client.force_authenticate(user=self.owner)

    def test_owner_creates_store_with_correct_organization(self):
        response = self.client.post("/api/stores/", {"name": "Centro", "is_active": True})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Store.objects.get(name="Centro").organization_id, self.org.id)

    def test_other_organization_stores_are_hidden(self):
        response = self.client.get("/api/stores/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(any(s["name"] == "Sucursal ajena" for s in response.data))

    def test_owner_creates_employee(self):
        response = self.client.post("/api/employees/", {
            "username": "new-cashier", "password": "StrongSamplePassword!123", "role": "cashier"
        })
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password", response.data)
        self.assertEqual(Membership.objects.get(user__username="new-cashier").organization_id, self.org.id)

    def test_reject_weak_employee_password(self):
        response = self.client.post("/api/employees/", {
            "username": "new-cashier", "password": "1234", "role": "cashier"
        })
        self.assertEqual(response.status_code, 400)

    def test_manager_cannot_create_employees(self):
        membership = Membership.objects.get(user=self.owner, organization=self.org)
        membership.role = "manager"
        membership.save(update_fields=["role"])
        response = self.client.post("/api/employees/", {
            "username": "new-cashier", "password": "StrongSamplePassword!123", "role": "cashier"
        })
        self.assertEqual(response.status_code, 403)

    def test_prevent_removing_last_owner(self):
        member = Membership.objects.get(user=self.owner, organization=self.org)
        response = self.client.patch(f"/api/employees/{member.id}/", {"role": "cashier"})
        self.assertEqual(response.status_code, 400)
        member.refresh_from_db()
        self.assertEqual(member.role, "owner")

    def test_cannot_change_other_organization_employee(self):
        outsider = get_user_model().objects.create_user(username="outsider", password="SampleTestingPassword!123")
        member = Membership.objects.create(organization=self.other, user=outsider, role="manager")
        response = self.client.patch(f"/api/employees/{member.id}/", {"role": "cashier"})
        self.assertEqual(response.status_code, 404)

    def test_cashier_cannot_read_management_records(self):
        member = Membership.objects.get(user=self.owner, organization=self.org)
        member.role = "cashier"
        member.save(update_fields=["role"])
        self.assertEqual(self.client.get("/api/employees/").status_code, 403)
        self.assertEqual(self.client.get("/api/stores/").status_code, 403)
