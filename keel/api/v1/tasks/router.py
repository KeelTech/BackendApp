from django.urls import path
from django.conf.urls import url
from .views import ListTask, GetTaskDetails

urlpatterns = [
    path('', ListTask.as_view({'get' : 'list'}), name='list-task'),
    url(r'get-task/(?P<task_id>[^\s]+)', GetTaskDetails.as_view({'get':'fetch'}), name = 'get-a-task'),
]
