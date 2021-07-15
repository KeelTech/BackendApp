from django.urls import path
from django.conf.urls import url
from .views import ListTask, GetTaskDetails, CommentService

urlpatterns = [
    path('list', ListTask.as_view({'get' : 'list'}), name='list-task'),
    path('taskDetails/<str:task_id>', GetTaskDetails.as_view({'get':'taskDetails'}), name = 'task_details'),
    path('comments/create', CommentService.as_view({'post' : 'postComments'}), name='post-comments'),
    path('comments/<int:comment_id>', CommentService.as_view({'delete' : 'deleteComments'}), name='delete-comments'),
]
