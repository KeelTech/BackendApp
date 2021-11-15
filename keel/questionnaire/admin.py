from django.contrib import admin
from django.db import models
from keel.Core.admin import CustomBaseModelAdmin
from .models import Question, AnsweredQuestionnaires, Option

class OptionAdminInline(admin.TabularInline):
    model = Option
    extra = 0
    readonly_fields = ()

class QuestionAdmin(CustomBaseModelAdmin):
    list_display = ('question', )
    readonly_fields = ('deleted_at',)
    inlines = (OptionAdminInline, )

admin.site.register(Question, QuestionAdmin)
admin.site.register(Option)
admin.site.register(AnsweredQuestionnaires)