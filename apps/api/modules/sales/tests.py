from decimal import Decimal
from uuid import uuid4
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from modules.organization.models import Organization, Store, Membership
from modules.catalog.models import Item
from modules.inventory.models import StockBalance, StockMovement
from .models import Sale


class CheckoutTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cashier-pos", password="test-password")
        self.org = Organization.objects.create(name="Main")
        self.foreign = Organization.objects.create(name="Foreign")
        Membership.objects.create(user=self.user, organization=self.org, role="cashier")
        self.store = Store.objects.create(organization=self.org, name="Main Store")
        self.other_store = Store.objects.create(organization=self.foreign, name="Other Store")
        self.item = Item.objects.create(organization=self.org, name="Cafe", sku="CAF-1", price=Decimal("1500.00"))
        self.other_item = Item.objects.create(organization=self.foreign, name="Secret", sku="SECRET", price=Decimal("1500.00"))
        StockBalance.objects.create(item=self.item, store=self.store, quantity=Decimal("10.000"))
        self.client.force_authenticate(self.user)

    def payload(self, key=None, quantity="2.000", item=None, store=None, cash="5000.00"):
        return {"store_id":str(store or self.store.id),"idempotency_key":str(key or uuid4()),
                "payment_method":"cash", "cash_received":cash,
                "lines":[{"item_id":str(item or self.item.id),"quantity":quantity}]}

    def test_cash_checkout_and_stock_debit(self):
        response = self.client.post("/api/sales/checkout/", self.payload(), format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(Decimal(response.data["total"]), Decimal("3000.00"))
        self.assertEqual(Decimal(response.data["change_due"]), Decimal("2000.00"))
        self.assertEqual(StockBalance.objects.get(item=self.item).quantity, Decimal("8.000"))
        self.assertEqual(StockMovement.objects.filter(reason="sale").count(), 1)
        self.assertEqual(Sale.objects.count(), 1)

    def test_retry_does_not_duplicate_sale_or_stock(self):
        key = uuid4()
        payload = self.payload(key=key)
        self.assertEqual(self.client.post("/api/sales/checkout/", payload, format="json").status_code, 201)
        self.assertEqual(self.client.post("/api/sales/checkout/", payload, format="json").status_code, 200)
        self.assertEqual(Sale.objects.count(), 1)
        self.assertEqual(StockBalance.objects.get(item=self.item).quantity, Decimal("8.000"))

    def test_idempotency_key_reuse_with_different_payload_rejected(self):
        key = uuid4()
        self.assertEqual(self.client.post("/api/sales/checkout/", self.payload(key=key), format="json").status_code, 201)
        self.assertEqual(self.client.post("/api/sales/checkout/", self.payload(key=key, quantity="3.000"), format="json").status_code, 400)

    def test_insufficient_stock_rolls_back_sale(self):
        response = self.client.post("/api/sales/checkout/", self.payload(quantity="11.000", cash="30000.00"), format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Sale.objects.count(), 0)
        self.assertEqual(StockBalance.objects.get(item=self.item).quantity, Decimal("10.000"))

    def test_insufficient_cash_is_rejected(self):
        self.assertEqual(self.client.post("/api/sales/checkout/", self.payload(cash="2000.00"), format="json").status_code, 400)
        self.assertEqual(Sale.objects.count(), 0)

    def test_other_organization_blocked(self):
        self.assertEqual(self.client.post("/api/sales/checkout/", self.payload(item=self.other_item.id), format="json").status_code, 400)
        self.assertEqual(self.client.post("/api/sales/checkout/", self.payload(store=self.other_store.id), format="json").status_code, 400)

    def test_cashier_cannot_view_backoffice_sales(self):
        self.assertEqual(self.client.get("/api/sales/").status_code, 403)

    def test_invalid_duplicate_line_rejected(self):
        payload = self.payload()
        payload["lines"].append(payload["lines"][0].copy())
        self.assertEqual(self.client.post("/api/sales/checkout/", payload, format="json").status_code, 400)

    def test_zero_quantity_rejected(self):
        self.assertEqual(self.client.post("/api/sales/checkout/", self.payload(quantity="0"), format="json").status_code, 400)
