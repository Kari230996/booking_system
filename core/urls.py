from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from bookings.views import RoomViewSet, BookingViewSet


router = DefaultRouter()
router.register(r"rooms", RoomViewSet, basename="room")
router.register(r"bookings", BookingViewSet, basename="booking")

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include(router.urls)),

    # OpenAPI/Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # djoser
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.jwt")),

]
