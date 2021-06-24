

from rest_framework import serializers
from keel.document.models import Documents

class DocumentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Documents
        fields = ('original_name', 'doc_type','avatar','doc_pk')