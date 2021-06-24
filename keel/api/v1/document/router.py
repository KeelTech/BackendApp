from django.conf.urls import url

from .views import GetDocument

urlpatterns = [
	url(r'get-single-doc/(?P<doc_id>[^\s]+)',GetDocument.as_view({'get':'generate'}), name='get-a-doc'),
]