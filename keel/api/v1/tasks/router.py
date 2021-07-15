from django.urls import path
from django.conf.urls import url
from .views import ListTask, GetTaskDetails

urlpatterns = [
    path('list', ListTask.as_view({'get' : 'list'}), name='list-task'),
    path('create', ListTask.as_view({'post' : 'createTask'}), name='create-task'),
    path('edit/<str:task_id>', ListTask.as_view({'put' : 'updateTask'}), name='edit-task'),    
    path('taskDetails/<str:task_id>', GetTaskDetails.as_view({'get':'taskDetails'}), name = 'task_details'),
]
