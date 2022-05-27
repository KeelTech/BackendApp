# from rest_framework import routers
from django.urls import path

from .views import (
    BlogListView,
    HomeLeadsView,
    WebsiteComponentsView,
    WebsiteContactDataView,
)

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
    path("blog-list", BlogListView.as_view({"get": "list"}), name="blog-list"),
    path(
        "blog-list/<int:pk>",
        BlogListView.as_view({"get": "retrieve"}),
        name="blog-list-detail",
    ),
]
