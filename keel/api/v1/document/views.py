from django.http import FileResponse

from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response

from .serializers import ListDocumentTypeSerializer

from keel.document.models import Documents, DocumentType
from keel.authentication import models as auth_models
from keel.authentication.backends import JWTAuthentication
from keel.Core.err_log import log_error

from .serializers import DocumentsSerializer

import magic
import base64 


class GetDocumentTypeChoices(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def docTypeList(self, request, format='json'):

        response = {
                "status": 0,
                "message": "Document Type List fetched successfully",
                "data": ""
        }

        doc_types = DocumentType.objects.all()
        response['data'] = ListDocumentTypeSerializer(doc_types, many=True).data
        return Response(response)

    def user_uploaded_docs(self, request):

        response = {
                "status": 0,
                "message": "User Uploaded Document Type List fetched successfully",
        }
        user = request.user
        doc_types = DocumentType.objects.all()
        user_docs = auth_models.UserDocument.objects.select_related('doc', 'doc__doc_type'). \
            filter(user_id=user.id, deleted_at__isnull=True).order_by("-updated_at")
        user_doc_map = {}
        for u_doc in user_docs:
            user_doc_map[u_doc.doc.doc_type.doc_type_name] = 1
        for d_type in doc_types:
            if d_type.doc_type_name not in user_doc_map:
                user_doc_map[d_type.doc_type_name] = 0
        response['status'] = 1
        response['data'] = user_doc_map
        return Response(response)


class GetDocument(GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def generate(self, request, **kwargs):
        
        response = {
                "status": 0,
        }
        doc_id = kwargs.get('doc_id')
        user = request.user
        if not doc_id:
            log_error('ERROR', 'GetDocument/generate', str(user.id), msg="doc_id missing")
            response['message'] = "DOC ID missing"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            doc = Documents.objects.get(doc_pk=doc_id, deleted_at__isnull=True)
            file_object = base64.b64encode(doc.avatar.open().read())
        except Documents.DoesNotExist:
            log_error('ERROR', 'GetDocument/generate', str(user.id), doc_id=str(doc_id), msg="Documents.DoesNotExist")
            response['message'] = "Document Id is invalid"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        content_type = magic.from_buffer(doc.avatar.open().read(2048), mime=True)
        
        resp_data = {"file_data": file_object, "content_type": content_type}
        response = Response(resp_data)
        response['Content-Length'] = doc.avatar.size
        response['Content-Disposition'] = 'attachment; filename="%s"' % doc.avatar.name
        response['Original-File-Name'] = doc.original_name

        return response

    def update_doc_status(self, request):
        response = {
            "status": 0,
        }
        req_data = request.data
        doc_id = req_data.get('doc_id')
        new_status = req_data.get('status')
        try:
            Documents.objects.filter(doc_pk=doc_id, deleted_at__isnull=True).update(verification_status=new_status)
        except Exception as e:
            response['message'] = str(e)
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response['status'] = 1
        response['message'] = 'Status Updated Successfully'
        return Response(response)

