import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class SessionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="manager", password="StrongTestPassword-123", is_staff=True)
        self.client = Client(enforce_csrf_checks=True)

    def csrf(self):
        response = self.client.get("/api/session/")
        self.assertEqual(response.status_code, 200)
        return self.client.cookies["csrftoken"].value

    def test_login_logout_roundtrip(self):
        token = self.csrf()
        response = self.client.post("/api/login/", json.dumps({"username": "manager", "password": "StrongTestPassword-123"}),
                                    content_type="application/json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["authenticated"])
        token = self.client.cookies["csrftoken"].value
        response = self.client.post("/api/logout/", content_type="application/json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client.get("/api/session/").json()["authenticated"])

    def test_invalid_credentials(self):
        token = self.csrf()
        response = self.client.post("/api/login/", json.dumps({"username": "manager", "password": "bad"}),
                                    content_type="application/json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 401)

    def test_login_without_csrf_is_forbidden(self):
        response = self.client.post("/api/login/", json.dumps({"username": "manager", "password": "StrongTestPassword-123"}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 403)

    def test_logout_without_csrf_is_forbidden(self):
        self.client.force_login(self.user)
        response = self.client.post("/api/logout/", content_type="application/json")
        self.assertEqual(response.status_code, 403)
