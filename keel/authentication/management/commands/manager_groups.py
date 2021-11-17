from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Q
from keel.cases.models import Case, Program
from keel.chats.models import Chat, ChatRoom
from keel.tasks.models import Task, TaskComments


class Command(BaseCommand):

    # def __init__(self, stdout, stderr, no_color, force_color):
    #     super().__init__(stdout=stdout, stderr=stderr, no_color=no_color, force_color=force_color)
    
    help = "Create default groups"

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name="manager_team")
        group.permissions.clear()
        content_types = ContentType.objects.get_for_models(Case, Chat, Task, Program, ChatRoom, TaskComments)
        
        for cl, ct in content_types.items():
            permissions = Permission.objects.filter(
                    Q(content_type=ct),
                    Q(codename='add_' + ct.model) |
                    Q(codename='change_' + ct.model)|
                    Q(codename='delete_' + ct.model))
            group.permissions.add(*permissions)
