from rest_framework.routers import DefaultRouter
from .management_views import StoreViewSet, EmployeeViewSet

router = DefaultRouter()
router.register("stores", StoreViewSet, basename="stores")
router.register("employees", EmployeeViewSet, basename="employees")
urlpatterns = router.urls
