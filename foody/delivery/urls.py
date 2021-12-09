from rest_framework import routers
from delivery.views import DeliveryTimeViewSet

router = routers.SimpleRouter()
router.register(r"api/v1", DeliveryTimeViewSet, basename="get-delivery-time")
urlpatterns = []
urlpatterns += router.urls