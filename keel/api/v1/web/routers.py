# from rest_framework import routers
from django.urls import path

from .views import HomeLeadsView, WebsiteComponentsView, WebsiteContactDataView

# router = routers.DefaultRouter()
# router.register(r"website-contact", WebsiteContactDataView)
# router.register(r"home-lead", HomeLeadsView)

urlpatterns = [
    path(
        "website-contact",
        WebsiteContactDataView.as_view({"post": "create"}),
        name="website-contact",
    ),
    path("home-lead", HomeLeadsView.as_view({"post": "create"}), name="home-lead"),
    path(
        "website-components",
        WebsiteComponentsView.as_view({"get": "list"}),
        name="website-components",
    ),
]
