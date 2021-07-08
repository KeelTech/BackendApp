from django.db import models

from keel.Core.models import TimeStampedModel, SoftDeleteModel
from keel.cases.models import Case

# Create your models here.

class Chat(TimeStampedModel, SoftDeleteModel):

    user = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='users_cases')
    agent = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='agents_cases')
	message = models.TextField(null=True, blank=True, default=None)
	case = models.ForeignKey(Case,on_delete=models.deletion.DO_NOTHING, related_name='cases_chats')	

