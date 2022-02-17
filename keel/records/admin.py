from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from keel.cases.models import Case
from keel.Core.admin import CustomBaseModelAdmin

User = get_user_model()

from .models import SalesUser


class SalesUserAdmin(CustomBaseModelAdmin):
    readonly_fields = ("deleted_at", "created_by")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(user_type=User.CUSTOMER)
        if db_field.name == "agent":
            kwargs["queryset"] = User.objects.filter(user_type=User.RCIC)
        if db_field.name == "account_manager":
            kwargs["queryset"] = User.objects.filter(user_type=User.ACCOUNT_MANAGER)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        created_by = request.user
        obj.created_by = created_by

        email = obj.email
        check_email = User.objects.filter(email=email)
        
        if len(check_email) == 0:
            user = User.objects.create_user(email=email, password="password@123")

            # create case instance
            case = Case(user=user, agent=obj.agent, plan=obj.plan)
            case.save()
            return super().save_model(request, obj, form, change)
        
        else:
            self.message_user(
                request, "Email already exists.", level=messages.ERROR
            )
            return HttpResponseRedirect(request.path)


admin.site.register(SalesUser, SalesUserAdmin)
