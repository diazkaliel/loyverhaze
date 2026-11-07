from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.organization.context import current_membership
from .models import Sale
from .serializers import CheckoutSerializer, SaleSerializer
from .services import checkout


class SalesPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        current_membership(request)
        return True


class CheckoutView(APIView):
    permission_classes = [SalesPermission]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sale, created = checkout(
            organization=current_membership(request).organization,
            cashier=request.user, **serializer.validated_data,
        )
        sale = Sale.objects.prefetch_related("lines").select_related("store").get(pk=sale.pk)
        return Response(SaleSerializer(sale).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class SaleListView(APIView):
    permission_classes = [SalesPermission]

    def get(self, request):
        membership = current_membership(request)
        if membership.role not in ("owner", "manager"):
            return Response({"detail": "Permiso insuficiente."}, status=403)
        queryset = Sale.objects.filter(organization=membership.organization).select_related("store").prefetch_related("lines").order_by("-created_at")[:100]
        return Response(SaleSerializer(queryset, many=True).data)
