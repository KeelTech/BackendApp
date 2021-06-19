from django.db import models

# Create your models here.
class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_on = models.DateTimeField(auto_now=True, db_index=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

