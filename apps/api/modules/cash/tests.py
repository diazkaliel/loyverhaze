from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from modules.organization.models import Membership, Organization, Store
from .models import CashShift, CashMovement


class CashTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="till-user", password="sample-test-password")
        self.org = Organization.objects.create(name="My Shop")
        self.other_org = Organization.objects.create(name="Other Shop")
        self.store = Store.objects.create(organization=self.org, name="Main")
        self.foreign_store = Store.objects.create(organization=self.other_org, name="Foreign")
        self.membership = Membership.objects.create(organization=self.org, user=self.user, role="owner")
        self.client.force_authenticate(self.user)

    def open(self):
        return self.client.post("/api/cash/shifts/", {"store_id": str(self.store.id), "opening_amount": "100.00"}, format="json")

    def test_open_deposit_withdraw_and_close(self):
        opened = self.open()
        self.assertEqual(opened.status_code, 201, opened.data)
        shift_id = opened.data["id"]
        self.assertEqual(self.client.post("/api/cash/movements/", {"shift_id":shift_id,"kind":"in","amount":"50.00","note":"Fondos adicionales"},format="json").status_code,201)
        self.assertEqual(self.client.post("/api/cash/movements/", {"shift_id":shift_id,"kind":"out","amount":"20.00","note":"Gasto"},format="json").status_code,201)
        self.assertEqual(self.client.get("/api/cash/shifts/").data[0]["expected_amount"], "130.00")
        closed = self.client.post(f"/api/cash/shifts/{shift_id}/close/",{"counted_amount":"125.00"},format="json")
        self.assertEqual(closed.status_code,200, closed.data)
        self.assertEqual(Decimal(closed.data["difference"]),Decimal("-5.00"))
        self.assertEqual(CashMovement.objects.count(),2)

    def test_only_one_open_shift_per_store(self):
        self.assertEqual(self.open().status_code,201)
        self.assertEqual(self.open().status_code,400)

    def test_cannot_open_on_other_organization_store(self):
        response=self.client.post("/api/cash/shifts/",{"store_id":str(self.foreign_store.id),"opening_amount":"10.00"},format="json")
        self.assertEqual(response.status_code,400)

    def test_cashier_cannot_close_shift(self):
        shift_id=self.open().data["id"]
        self.membership.role="cashier"
        self.membership.save(update_fields=["role"])
        response=self.client.post(f"/api/cash/shifts/{shift_id}/close/",{"counted_amount":"100.00"},format="json")
        self.assertEqual(response.status_code,403)

    def test_cannot_move_cash_after_closure(self):
        shift_id=self.open().data["id"]
        self.client.post(f"/api/cash/shifts/{shift_id}/close/",{"counted_amount":"100.00"},format="json")
        response=self.client.post("/api/cash/movements/",{"shift_id":shift_id,"kind":"in","amount":"20.00","note":"Tarde"},format="json")
        self.assertEqual(response.status_code,400)

    def test_reject_withdrawal_above_expected(self):
        shift_id=self.open().data["id"]
        response=self.client.post("/api/cash/movements/",{"shift_id":shift_id,"kind":"out","amount":"101.00","note":"Demasiado"},format="json")
        self.assertEqual(response.status_code,400)
        self.assertEqual(CashShift.objects.get(pk=shift_id).expected_amount,Decimal("100.00"))
