from rest_framework.routers import SimpleRouter

from .views import ForecastViewSet

router = SimpleRouter()
router.register("forecasts", ForecastViewSet, basename="forecast")
urlpatterns = router.urls
