from rest_framework import routers
from django.urls import path, include

from .views import WebsiteContactDataView, HomeLeadsView

router = routers.DefaultRouter()
router.register(r"website-contact", WebsiteContactDataView)
router.register(r"home-lead", HomeLeadsView)

urlpatterns = [
    path("", include(router.urls)),
]
