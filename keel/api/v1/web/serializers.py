from keel.web.models import HomeLeads, WebsiteComponents, WebsiteContactData, IeltsData
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
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = WebsiteComponents
        exclude = ("deleted_at", )

    def get_updated_at(self, obj):
        return obj.updated_at.strftime("%B %d, %Y")


class BlogListSerializer(serializers.ModelSerializer):
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = WebsiteComponents
        fields = ("id", "title", "highlight", "blog_img", "updated_at")

    def get_updated_at(self, obj):
        return obj.updated_at.strftime("%B %d, %Y")


class IeltsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = IeltsData
        fields = ("title", "day", "start_time", "end_time", "exam_type", "module", "ielts_img")
