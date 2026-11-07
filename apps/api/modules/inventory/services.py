from decimal import Decimal
from django.db import transaction
from rest_framework.exceptions import ValidationError
from modules.catalog.models import Item
from modules.organization.models import Store
from .models import StockBalance, StockMovement


@transaction.atomic
def record_stock_movement(*, organization, item_id, store_id, delta, reason, note, key, user):
    # Serializing all writes to an item also protects creation of its first stock row.
    item = Item.objects.select_for_update().filter(id=item_id, organization=organization).first()
    store = Store.objects.filter(id=store_id, organization=organization, is_active=True).first()
    if item is None or store is None:
        raise ValidationError({"detail": "Artículo o sucursal no disponible."})
    existing = StockMovement.objects.filter(organization=organization, idempotency_key=key).first()
    if existing is not None:
        if (existing.item_id, existing.store_id, existing.quantity_delta, existing.reason, existing.note) != (item.pk, store.pk, delta, reason, note):
            raise ValidationError({"idempotency_key": "La clave ya se utilizó con otros datos."})
        return existing, False
    balance, _ = StockBalance.objects.select_for_update().get_or_create(
        item=item, store=store, defaults={"quantity": Decimal("0")}
    )
    resulting = balance.quantity + delta
    if resulting < 0:
        raise ValidationError({"quantity_delta": "El movimiento dejaría existencias negativas."})
    if resulting > Decimal("999999999999999.999"):
        raise ValidationError({"quantity_delta": "Cantidad fuera del rango permitido."})
    movement = StockMovement.objects.create(
        organization=organization, item=item, store=store,
        quantity_delta=delta, resulting_quantity=resulting,
        reason=reason, note=note, idempotency_key=key, performed_by=user,
    )
    balance.quantity = resulting
    balance.save(update_fields=["quantity"])
    return movement, True
