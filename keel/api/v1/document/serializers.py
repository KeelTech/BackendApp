from rest_framework import serializers
from keel.document.models import Documents, DocumentType
from keel.document.utils import validate_files
from keel.Core.err_log import log_error


class ListDocumentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentType
        fields = ('id','doc_type_name')

class DocumentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Documents
        fields = ('original_name', 'doc_type','avatar','doc_pk')

class DocumentCreateSerializer(serializers.Serializer):

    doc_file = serializers.FileField()

    def validate_doc_file(self, value):

        err_msg = ''
        err_msg = validate_files(value)
        if err_msg:
            log_error("ERROR","DocumentCreateSerializer: validate_doc_file", "", err = str(e), value = value)
            raise serializers.ValidationError(err_msg)
        return err_msg

class DocumentTypeSerializer(serializers.Serializer):

    doc_type = serializers.CharField(max_length=255)

    def validate_doc_type(self, value):

        doc_type_obj = ''
        doc_type_id = value
        if not doc_type_id:
            doc_type_id = DocumentType.DEFAULT_PK_ID

        try:
            doc_type_obj = DocumentType.objects.get(id = doc_type_id)
        except DocumentType.DoesNotExist as e:
            log_error("ERROR","DocumentTypeSerializer: validate_doc_type", "", err = str(e), value = value)
            raise serializers.ValidationError("Invalid Document Type Id")

        return doc_type_obj


