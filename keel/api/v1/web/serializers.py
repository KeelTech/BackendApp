from keel.web.models import HomeLeads, WebsiteComponents, WebsiteContactData
from rest_framework import serializers


class WebsiteContactDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteContactData
        fields = ("id", "name", "email", "phone", "message")


class HomeLeadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeLeads
        fields = ("id", "email", "phone")


class WebsiteComponentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteComponents
        fields = ("id", "title", "component_name", "body", "blog_img")


class BlogListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteComponents
        fields = ("id", "title", "blog_img")
