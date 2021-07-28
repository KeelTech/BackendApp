from django.http import FileResponse

from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response

from .serializers import ListDocumentTypeSerializer

from keel.document.models import Documents, DocumentType
from keel.authentication.backends import JWTAuthentication
from keel.Core.err_log import log_error

from .serializers import DocumentsSerializer

class GetDocumentTypeChoices(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def docTypeList(self, request, format = 'json'):

        response = {
                "status": 0,
                "message":"Document Type List fetched successfully",
                "data": ""
        }

        doc_types = DocumentType.objects.all()
        response['data'] = ListDocumentTypeSerializer(doc_types, many = True).data
        return Response(response, status = status.HTTP_200_OK)

class GetDocument(GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def generate(self, request, format = 'json', **kwargs):
        
        response = {
                "status": 0,
                "message":"Document Fetched successfully",
                "data": ""
        }
        resp_status = status.HTTP_200_OK
        doc_id = kwargs.get('doc_id')
        user = request.user
        if not doc_id:
            log_error('ERROR', 'GetDocument/generate', str(user.id), msg = "doc_id missing")
            response['status'] = 1
            response['message'] = "Invalid Request Data"
            resp_status = status.HTTP_400_BAD_REQUEST
            return Response(response, status = resp_status)

        try:
            doc = Documents.objects.get(doc_pk = doc_id, deleted_at__isnull = True)
        except Documents.DoesNotExist:
            log_error('ERROR', 'GetDocument/generate',str(user.id), doc_id = str(doc_id), msg = "Documents.DoesNotExist")
            response['status'] = 1
            response['message'] = "Document Id is invalid"
            resp_status = status.HTTP_400_BAD_REQUEST
            return Response(response, status = resp_status)
        # doc_serializer = DocumentsSerializer(doc)
        # response_data = doc_serializer.data
        # response["data"] = response_data
        try:
            file_handle = doc.avatar.open()
        except FileNotFoundError as e:
            log_error('ERROR', 'GetDocument/generate', str(user.id), msg = 'FileNotFoundError', doc_id = str(doc_id),
                                            err = str(e))
            response['status'] = 1
            response['message'] = "File Not Found"
            resp_status = status.HTTP_400_BAD_REQUEST
            return Response(response, status = resp_status)

        response = FileResponse(file_handle, content_type='whatever')
        response['Content-Length'] = doc.avatar.size
        response['Content-Disposition'] = 'attachment; filename="%s"' % doc.avatar.name

        return response
       
