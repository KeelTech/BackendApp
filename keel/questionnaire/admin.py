from django.contrib import admin
from django.db import models
from keel.Core.admin import CustomBaseModelAdmin

from .models import (AnsweredQuestionsModel, CheckBoxModel, DropDownModel,
                     Question, SpouseQuestion)


class CheckBoxAdminInline(admin.TabularInline):
    model = CheckBoxModel
    extra = 0
    readonly_fields = ('deleted_at', 'spouse_question')
    fk_name = 'question'

class DropDownAdminInline(admin.TabularInline):
    model = DropDownModel
    extra = 0
    readonly_fields = ('deleted_at', 'spouse_question')
    fk_name = 'question'
    

class QuestionAdmin(CustomBaseModelAdmin):
    list_display = ('question_text', 'index', 'is_active')
    readonly_fields = ('deleted_at',)
    inlines = (CheckBoxAdminInline, DropDownAdminInline, )


# class SpouseQuestionAdmin(CustomBaseModelAdmin):
#     list_display = ('question_text', )
#     readonly_fields = ('deleted_at',)
#     inlines = (CheckBoxAdminInline, DropDownAdminInline, )


admin.site.register(Question, QuestionAdmin)
# admin.site.register(SpouseQuestion, SpouseQuestionAdmin)
admin.site.register(DropDownModel)
admin.site.register(CheckBoxModel)
admin.site.register(AnsweredQuestionsModel)
