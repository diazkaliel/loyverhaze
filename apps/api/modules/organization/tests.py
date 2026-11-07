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
