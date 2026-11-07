from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from modules.organization.models import Membership, Organization, Store
from .models import Category, Item


class CatalogAPITests(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Tienda A")
        self.other_org = Organization.objects.create(name="Tienda B")
        self.user = get_user_model().objects.create_user(username="cashier", password="example-test-password")
        Membership.objects.create(user=self.user, organization=self.org, role="cashier")
        self.client.force_authenticate(user=self.user)

    def use_role(self, role="owner"):
        member = Membership.objects.get(user=self.user, organization=self.org)
        member.role = role
        member.save(update_fields=["role"])

    def test_list_is_authenticated(self):
        self.assertEqual(self.client.get("/api/items/").status_code, 200)

    def test_cashier_cannot_create_item(self):
        self.assertEqual(self.client.post("/api/items/", {"name": "Cafe", "sku": "CAFE-1", "price": "2500.00"}).status_code, 403)

    def test_owner_can_create_item(self):
        self.use_role()
        category = Category.objects.create(organization=self.org, name="Bebidas")
        response = self.client.post("/api/items/", {"name": "Cafe", "sku": "CAFE-1", "price": "2500.00", "category": str(category.id)})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Item.objects.get(sku="CAFE-1").price, Decimal("2500.00"))
        self.assertEqual(Item.objects.get(sku="CAFE-1").organization_id, self.org.id)

    def test_negative_price_is_rejected(self):
        self.use_role()
        response = self.client.post("/api/items/", {"name": "Cafe", "sku": "CAFE-2", "price": "-1.00"})
        self.assertEqual(response.status_code, 400)

    def test_owner_updates_item_without_changing_uuid(self):
        self.use_role()
        item = Item.objects.create(organization=self.org, name="Agua", sku="AG-01", price=Decimal("1200.00"))
        response = self.client.patch(f"/api/items/{item.id}/", {"name": "Agua mineral", "price": "1300.00"})
        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.name, "Agua mineral")
        self.assertEqual(item.price, Decimal("1300.00"))

    def test_cashier_cannot_edit_item(self):
        item = Item.objects.create(organization=self.org, name="Jugo", sku="JG-01", price=Decimal("1500.00"))
        response = self.client.patch(f"/api/items/{item.id}/", {"price": "100.00"})
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_read_catalog(self):
        self.client.force_authenticate(user=None)
        self.assertIn(self.client.get("/api/items/").status_code, [401, 403])

    def test_other_organization_records_are_not_exposed(self):
        item = Item.objects.create(organization=self.other_org, name="Privado", sku="PRIVATE-1", price=Decimal("100.00"))
        response = self.client.get("/api/items/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(any(x["id"] == str(item.id) for x in response.data))
        self.assertEqual(self.client.get(f"/api/items/{item.id}/").status_code, 404)

    def test_foreign_category_cannot_be_used(self):
        self.use_role()
        category = Category.objects.create(organization=self.other_org, name="Privada")
        response = self.client.post("/api/items/", {"name": "Cafe", "sku": "CAFE-3", "price": "1000.00", "category": str(category.id)})
        self.assertEqual(response.status_code, 400)

    def test_same_sku_different_organizations(self):
        self.use_role()
        Item.objects.create(organization=self.other_org, name="Cafe B", sku="SHARED", price=Decimal("100.00"))
        response = self.client.post("/api/items/", {"name": "Cafe A", "sku": "SHARED", "price": "100.00"})
        self.assertEqual(response.status_code, 201)

    def test_no_membership_is_forbidden_even_for_superuser(self):
        admin = get_user_model().objects.create_superuser(username="no-org", password="example-test-password")
        self.client.force_authenticate(user=admin)
        self.assertEqual(self.client.get("/api/items/").status_code, 403)
