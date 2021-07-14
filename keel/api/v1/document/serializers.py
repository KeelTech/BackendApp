

from rest_framework import serializers
from keel.document.models import Documents, DocumentType

class ListDocumentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentType
        fields = ('id','doc_type_name')

class DocumentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Documents
        fields = ('original_name', 'doc_type','avatar','doc_pk')
