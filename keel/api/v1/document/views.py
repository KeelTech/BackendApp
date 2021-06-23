from django.http import FileResponse

from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response

from keel.document.models import Documents

from .serializers import DocumentsSerializer



class GetDocument(GenericViewSet):

    def generate(self, request, format = 'json', **kwargs):
        
        response = {
                "status": 0,
                "message":"Document Fetched successfully",
                "data": ""
        }

        doc_id = kwargs.get('doc_id')

        if not doc_id:
        	response['status'] = 1
        	response['message'] = "Document Id is invalid"
        	return Response(response)


        doc = Documents.objects.get(doc_pk = doc_id)

        # doc_serializer = DocumentsSerializer(doc)
        # response_data = doc_serializer.data
        # response["data"] = response_data
        file_handle = doc.avatar.open()
        response = FileResponse(file_handle, content_type='whatever')
        response['Content-Length'] = doc.avatar.size
        response['Content-Disposition'] = 'attachment; filename="%s"' % doc.avatar.name

        return response
       



