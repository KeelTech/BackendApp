from django.contrib import admin
from .models import StudentEducation, StudentProfile
from keel.Core.admin import CustomBaseModelAdmin


class StudentProfileAdmin(CustomBaseModelAdmin):
    pass


class StudentEducationAdmin(CustomBaseModelAdmin):
    pass


admin.site.register(StudentProfile, StudentProfileAdmin)
admin.site.register(StudentEducation, StudentEducationAdmin)
