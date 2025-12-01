from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventsViewSet, EventOccurrencesViewSet

router = DefaultRouter()
router.register(r"", EventsViewSet, basename="events")
router.register(r"occurrences", EventOccurrencesViewSet, basename="occurrences")

urlpatterns = [
    path("", include(router.urls)),
]
