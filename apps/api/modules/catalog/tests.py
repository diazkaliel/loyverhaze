from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from .models import Category, Item

class CatalogAPITests(APITestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="cashier", password="example-test-password")
        self.client.force_authenticate(user=user)

    def test_list_is_authenticated(self):
        response = self.client.get("/api/items/")
        self.assertEqual(response.status_code, 200)

    def test_non_staff_cannot_create_item(self):
        response = self.client.post("/api/items/", {"name": "Cafe", "sku": "CAFE-1", "price": "2500.00"})
        self.assertEqual(response.status_code, 403)

    def test_staff_can_create_item(self):
        user = get_user_model().objects.create_user(username="manager", password="example-test-password", is_staff=True)
        self.client.force_authenticate(user=user)
        category = Category.objects.create(name="Bebidas")
        response = self.client.post("/api/items/", {"name": "Cafe", "sku": "CAFE-1", "price": "2500.00", "category": str(category.id)})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Item.objects.get().price, Decimal("2500.00"))

    def test_negative_price_is_rejected(self):
        user = get_user_model().objects.create_user(username="manager2", password="example-test-password", is_staff=True)
        self.client.force_authenticate(user=user)
        response = self.client.post("/api/items/", {"name": "Cafe", "sku": "CAFE-2", "price": "-1.00"})
        self.assertEqual(response.status_code, 400)
