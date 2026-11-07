from decimal import Decimal
from uuid import uuid4

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from modules.catalog.models import Item
from modules.organization.models import Membership, Organization, Store
from .models import StockBalance, StockMovement


class InventoryTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="owner", password="test-password")
        self.org = Organization.objects.create(name="Negocio A")
        self.other_org = Organization.objects.create(name="Negocio B")
        self.membership = Membership.objects.create(organization=self.org, user=self.user, role="owner")
        self.store = Store.objects.create(organization=self.org, name="Principal")
        self.other_store = Store.objects.create(organization=self.other_org, name="Ajena")
        self.item = Item.objects.create(organization=self.org, name="Cafe", sku="CAFE", price="1500.00")
        self.other_item = Item.objects.create(organization=self.other_org, name="Privado", sku="CAFE", price="1500.00")
        self.client.force_authenticate(self.user)

    def post(self, *, delta="5.000", item=None, store=None, key=None, reason="receipt"):
        return self.client.post("/api/inventory/movements/", {
            "item_id": str(item or self.item.id), "store_id": str(store or self.store.id),
            "quantity_delta": delta, "reason": reason, "idempotency_key": str(key or uuid4()),
        }, format="json")

    def test_receipt_updates_balance_and_ledger(self):
        response = self.post()
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(StockBalance.objects.get(item=self.item, store=self.store).quantity, Decimal("5.000"))
        self.assertEqual(StockMovement.objects.count(), 1)

    def test_repeated_request_is_idempotent(self):
        key = uuid4()
        self.assertEqual(self.post(key=key).status_code, 201)
        self.assertEqual(self.post(key=key).status_code, 200)
        self.assertEqual(StockMovement.objects.count(), 1)
        self.assertEqual(StockBalance.objects.get(item=self.item).quantity, Decimal("5.000"))

    def test_reusing_key_with_other_payload_rejected(self):
        key = uuid4()
        self.post(key=key)
        self.assertEqual(self.post(key=key, delta="6.000").status_code, 400)

    def test_negative_stock_rejected_without_ledger(self):
        response = self.post(delta="-1", reason="adjustment")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(StockMovement.objects.count(), 0)

    def test_foreign_item_and_store_rejected(self):
        self.assertEqual(self.post(item=self.other_item.id).status_code, 400)
        self.assertEqual(self.post(store=self.other_store.id).status_code, 400)
        self.assertEqual(StockMovement.objects.count(), 0)

    def test_cashier_cannot_post_movements(self):
        self.membership.role = "cashier"
        self.membership.save(update_fields=["role"])
        self.assertEqual(self.post().status_code, 403)

    def test_read_is_scoped_to_organization(self):
        self.assertEqual(self.post().status_code, 201)
        response = self.client.get("/api/inventory/stock/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["item_name"], "Cafe")
        self.assertEqual(len(self.client.get("/api/inventory/movements/").data), 1)

    def test_zero_quantity_is_rejected(self):
        self.assertEqual(self.post(delta="0").status_code, 400)

    def test_negative_receipt_is_rejected(self):
        self.assertEqual(self.post(delta="-1", reason="receipt").status_code, 400)
