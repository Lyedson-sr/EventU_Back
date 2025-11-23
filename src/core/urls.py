from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView
from core import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("docs/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path(f"api/{settings.API_MAJOR}/auth/", include("apps.authentication.urls")),
    path(f"api/{settings.API_MAJOR}/users/", include("apps.users.urls")),
    path(f"api/{settings.API_MAJOR}/groups/", include("apps.groups.urls")),
    path(f"api/{settings.API_MAJOR}/events/", include("apps.events.urls")),
]
