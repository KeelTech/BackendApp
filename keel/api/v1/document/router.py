from django.urls import path

from .views import GetDocument, GetDocumentTypeChoices

urlpatterns = [
	path(r'get-single-doc/<str:doc_id>', GetDocument.as_view({'get': 'generate'}), name='get-a-doc'),
	path('doc-type-list', GetDocumentTypeChoices.as_view({'get': 'docTypeList'}), name='get-doc-type-list'),
	path('user-uploaded-docs', GetDocumentTypeChoices.as_view({'get': 'user_uploaded_docs'}), name='user-uploaded-docs'),
	path('status-update', GetDocument.as_view({'post': 'update_doc_status'}), name='update-doc-status'),
]