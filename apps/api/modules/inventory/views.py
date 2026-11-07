from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from modules.catalog.models import Item
from modules.organization.context import current_membership
from modules.organization.models import Store
from .models import StockBalance, StockMovement
from .serializers import StockMovementCreateSerializer, StockMovementSerializer
from .services import record_stock_movement


class InventoryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        member = current_membership(request)
        return request.method in permissions.SAFE_METHODS or member.role in ("owner", "manager")


class StockView(APIView):
    permission_classes = [InventoryPermission]

    def get(self, request):
        org = current_membership(request).organization
        stores = list(Store.objects.filter(organization=org).order_by("name").values("id", "name", "is_active"))
        items = list(Item.objects.filter(organization=org).order_by("name").values("id", "name", "sku"))
        balances = StockBalance.objects.filter(store__organization=org, item__organization=org)
        amounts = {(b.item_id, b.store_id): b.quantity for b in balances}
        # Each item/store combination is shown, including explicit zero stock.
        rows = [{"item_id": str(i["id"]), "item_name": i["name"], "sku": i["sku"],
                 "store_id": str(s["id"]), "store_name": s["name"], "store_active": s["is_active"],
                 "quantity": str(amounts.get((i["id"], s["id"]), 0))}
                for i in items for s in stores]
        return Response(rows)


class MovementListCreateView(APIView):
    permission_classes = [InventoryPermission]

    def get(self, request):
        org = current_membership(request).organization
        movements = StockMovement.objects.filter(organization=org).select_related(
            "item", "store", "performed_by"
        ).order_by("-created_at", "-id")[:200]
        return Response(StockMovementSerializer(movements, many=True).data)

    def post(self, request):
        serializer = StockMovementCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        movement, created = record_stock_movement(
            organization=current_membership(request).organization,
            item_id=data["item_id"], store_id=data["store_id"],
            delta=data["quantity_delta"], reason=data["reason"],
            note=data.get("note", ""), key=data["idempotency_key"], user=request.user,
        )
        return Response(StockMovementSerializer(movement).data,
                        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
