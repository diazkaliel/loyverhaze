from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid5, NAMESPACE_URL

from django.db import transaction
from rest_framework.exceptions import ValidationError

from modules.catalog.models import Item
from modules.organization.models import Organization, Store
from modules.inventory.services import record_stock_movement
from .models import Sale, SaleLine


def _price(value):
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@transaction.atomic
def checkout(*, organization, store_id, lines, payment_method, cash_received, key, cashier):
    # Organization row serializes sale requests within this tenant, including retries.
    Organization.objects.select_for_update().get(pk=organization.pk)
    existing = Sale.objects.filter(organization=organization, idempotency_key=key).first()
    if existing is not None:
        # A retry must not be capable of silently changing the existing transaction.
        original = [(str(line.item_id), line.quantity) for line in existing.lines.order_by("item_id")]
        requested = sorted([(str(row["item_id"]), row["quantity"]) for row in lines])
        if (str(existing.store_id) != str(store_id) or original != requested
                or existing.payment_method != payment_method or existing.cash_received != cash_received):
            raise ValidationError({"idempotency_key": "Clave ya utilizada con otros datos."})
        return existing, False

    store = Store.objects.filter(pk=store_id, organization=organization, is_active=True).first()
    if store is None:
        raise ValidationError({"store_id": "Sucursal no disponible."})
    item_ids = [line["item_id"] for line in lines]
    items = {str(item.id): item for item in Item.objects.filter(
        organization=organization, id__in=item_ids, available_for_sale=True
    )}
    if len(items) != len(item_ids):
        raise ValidationError({"lines": "Hay artículos inexistentes o no disponibles."})

    snapshots = []
    total = Decimal("0.00")
    for row in lines:
        item = items[str(row["item_id"])]
        quantity = row["quantity"]
        amount = _price(item.price * quantity)
        total += amount
        snapshots.append((item, quantity, amount))
    if total > Decimal("999999999999.99"):
        raise ValidationError({"lines": "Total fuera del rango."})
    if cash_received < total:
        raise ValidationError({"cash_received": "El efectivo recibido es insuficiente."})

    sale = Sale.objects.create(
        organization=organization, store=store, cashier=cashier,
        idempotency_key=key, payment_method=payment_method, total=total,
        cash_received=cash_received, change_due=cash_received-total,
    )
    for item, quantity, amount in snapshots:
        SaleLine.objects.create(
            sale=sale, item=item, item_name=item.name, sku=item.sku,
            quantity=quantity, unit_price=item.price, line_total=amount,
        )
        # The same transaction rolls back sale, payment and every stock deduction on failure.
        stock_key = uuid5(NAMESPACE_URL, f"loyverhaze:sale:{sale.id}:item:{item.id}")
        record_stock_movement(
            organization=organization, item_id=item.id, store_id=store.id,
            delta=-quantity, reason="sale", note=f"Venta {sale.id}",
            key=stock_key, user=cashier,
        )
    return sale, True
