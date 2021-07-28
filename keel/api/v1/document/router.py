from django.urls import path

from .views import GetDocument, GetDocumentTypeChoices

urlpatterns = [
	path(r'get-single-doc/<str:doc_id>',GetDocument.as_view({'get':'generate'}), name='get-a-doc'),
	path('doc-type-list', GetDocumentTypeChoices.as_view({'get':'docTypeList'}), name = 'get-doc-type-list'),
]