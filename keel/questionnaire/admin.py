from django.contrib import admin
from django.db import models
from keel.Core.admin import CustomBaseModelAdmin
from .models import Question, Answer, CustomerAnswers

class AnswerAdminInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ()

class QuestionAdmin(CustomBaseModelAdmin):
    readonly_fields = ('deleted_at',)
    inlines = (AnswerAdminInline, )

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(CustomerAnswers)