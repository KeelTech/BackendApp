from django.contrib import admin
from django.db import models
from keel.Core.admin import CustomBaseModelAdmin
from .models import Question, CheckBoxModel, DropDownModel, AnsweredQuestionsModel

class CheckBoxAdminInline(admin.TabularInline):
    model = CheckBoxModel
    extra = 0
    readonly_fields = ()

class DropDownAdminInline(admin.TabularInline):
    model = DropDownModel
    extra = 0
    readonly_fields = ()

class QuestionAdmin(CustomBaseModelAdmin):
    list_display = ('question_text', )
    readonly_fields = ('deleted_at',)
    inlines = (CheckBoxAdminInline, DropDownAdminInline, )

admin.site.register(Question, QuestionAdmin)
admin.site.register(DropDownModel)
admin.site.register(CheckBoxModel)
admin.site.register(AnsweredQuestionsModel)