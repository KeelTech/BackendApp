from django.urls import path
from django.conf.urls import url
from .views import ListTask, GetTaskDetails, CommentService, TaskStatusChange, TaskAdminOperations, GetTemplateTask

urlpatterns = [
    path('list', ListTask.as_view({'get' : 'list'}), name='list-task'),
    path('edit/<str:task_id>', ListTask.as_view({'put' : 'updateTask'}), name='edit-task'),    
    path('create', TaskAdminOperations.as_view({'post' : 'createTask'}), name='create-task'),
    path('delete/<str:task_id>', TaskAdminOperations.as_view({'delete' : 'deleteTask'}), name='delete-task'),    
    path('taskDetails/<str:task_id>', GetTaskDetails.as_view({'get':'taskDetails'}), name = 'task_details'),
    path('comments/create', CommentService.as_view({'post' : 'postComments'}), name='post-comments'),
    path('comments/<int:comment_id>', CommentService.as_view({'delete' : 'deleteComments'}), name='delete-comments'),
    path('taskStatus/<str:task_id>', TaskStatusChange.as_view({'put':'StatusEdit'}), name = 'task-status-change'),
    path('template-task', GetTemplateTask.as_view({'get':'get_templated_task'}), name="template-task")
]
