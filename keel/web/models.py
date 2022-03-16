from ckeditor.fields import RichTextField
from keel.Core.models import TimeStampedModel, SoftDeleteModel
# Create your models here.


class HtmlField(TimeStampedModel, SoftDeleteModel):
    body = RichTextField()

    class Meta:
        abstract = True


class Web(HtmlField):
    pass

    def __str__(self):
        return str(self.pk)
