from django.urls import path

from .views import GetDocument

urlpatterns = [
	path(r'get-single-doc/<str:doc_id>',GetDocument.as_view({'get':'generate'}), name='get-a-doc'),
]