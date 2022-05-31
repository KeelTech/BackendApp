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
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = WebsiteComponents
        exclude = ("updated_at", "deleted_at")

    def get_created_at(self, obj):
        return obj.created_at.strftime("%B %d, %Y")


class BlogListSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = WebsiteComponents
        fields = ("id", "title", "blog_img", "created_at")

    def get_created_at(self, obj):
        return obj.created_at.strftime("%B %d, %Y")
