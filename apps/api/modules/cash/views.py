from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from modules.organization.context import current_membership
from .models import CashMovement, CashShift
from .serializers import (CashShiftSerializer, CashMovementSerializer,
                          ShiftOpenSerializer, ShiftCloseSerializer, MovementCreateSerializer)
from .services import cash_movement, close_shift, open_shift


class CashPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        member = current_membership(request)
        if request.method in permissions.SAFE_METHODS:
            return True
        if isinstance(view, ShiftCloseView):
            return member.role in ("owner", "manager")
        return member.role in ("owner", "manager", "cashier")


class ShiftView(APIView):
    permission_classes = [CashPermission]

    def get(self, request):
        org = current_membership(request).organization
        shifts = CashShift.objects.filter(organization=org).select_related("store", "opened_by", "closed_by").order_by("-opened_at")[:100]
        return Response(CashShiftSerializer(shifts, many=True).data)

    def post(self, request):
        serializer = ShiftOpenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shift = open_shift(organization=current_membership(request).organization,
                           user=request.user, **serializer.validated_data)
        return Response(CashShiftSerializer(shift).data, status=status.HTTP_201_CREATED)


class ShiftCloseView(APIView):
    permission_classes = [CashPermission]

    def post(self, request, shift_id):
        serializer = ShiftCloseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shift = close_shift(organization=current_membership(request).organization,
                            shift_id=shift_id, user=request.user, **serializer.validated_data)
        return Response(CashShiftSerializer(shift).data)


class MovementView(APIView):
    permission_classes = [CashPermission]

    def get(self, request):
        org = current_membership(request).organization
        movements = CashMovement.objects.filter(shift__organization=org).select_related("performed_by").order_by("-created_at")[:200]
        return Response(CashMovementSerializer(movements, many=True).data)

    def post(self, request):
        serializer = MovementCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        movement = cash_movement(organization=current_membership(request).organization,
                                  user=request.user, **serializer.validated_data)
        return Response(CashMovementSerializer(movement).data, status=status.HTTP_201_CREATED)
