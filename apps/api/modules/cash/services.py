from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from modules.organization.models import Organization, Store
from .models import CashMovement, CashShift


@transaction.atomic
def open_shift(*, organization, store_id, opening_amount, user):
    Organization.objects.select_for_update().get(pk=organization.pk)
    store = Store.objects.filter(organization=organization, pk=store_id, is_active=True).first()
    if store is None:
        raise ValidationError({"store_id": "La sucursal no existe o está desactivada."})
    if CashShift.objects.filter(store=store, status=CashShift.Status.OPEN).exists():
        raise ValidationError({"store_id": "Ya existe una caja abierta en esta sucursal."})
    return CashShift.objects.create(organization=organization, store=store, opened_by=user,
                                    opening_amount=opening_amount, expected_amount=opening_amount)


@transaction.atomic
def cash_movement(*, organization, shift_id, kind, amount, note, user):
    Organization.objects.select_for_update().get(pk=organization.pk)
    shift = CashShift.objects.select_for_update().filter(pk=shift_id, organization=organization, status=CashShift.Status.OPEN).first()
    if shift is None:
        raise ValidationError({"shift_id": "Caja no disponible o cerrada."})
    delta = amount if kind == CashMovement.Kind.IN else -amount
    expected = shift.expected_amount + delta
    if expected < Decimal("0"):
        raise ValidationError({"amount": "La caja no puede quedar con efectivo esperado negativo."})
    movement = CashMovement.objects.create(shift=shift, kind=kind, amount=amount, note=note, performed_by=user)
    shift.expected_amount = expected
    shift.save(update_fields=["expected_amount"])
    return movement


@transaction.atomic
def close_shift(*, organization, shift_id, counted_amount, user):
    Organization.objects.select_for_update().get(pk=organization.pk)
    shift = CashShift.objects.select_for_update().filter(pk=shift_id, organization=organization, status=CashShift.Status.OPEN).first()
    if shift is None:
        raise ValidationError({"shift_id": "La caja ya está cerrada o no existe."})
    shift.counted_amount = counted_amount
    shift.difference = counted_amount - shift.expected_amount
    shift.closed_at = timezone.now()
    shift.closed_by = user
    shift.status = CashShift.Status.CLOSED
    shift.save(update_fields=["counted_amount", "difference", "closed_at", "closed_by", "status"])
    return shift
