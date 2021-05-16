from django.contrib.auth.models import Permission
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin






class CustomUserAdmin(UserAdmin):
    list_display = ('email',)
    list_filter = ('is_staff', 'is_superuser')
    ordering = []
    inlines = [
        StaffProfileInline
        # UserNumberUpdateInline
    ]
    search_fields = ['email', 'phone_number']
    list_display = ('email','phone_number', 'is_active')
    list_select_related = ('staffprofile',)
    form = CustomUserChangeForm

    def save_model(self, request, obj, form, change):
        if not obj.email:
            obj.email = None
        super().save_model(request, obj, form, change)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return ((None, {'fields': ('email', 'phone_number','groups','user_type','is_staff','is_active','password1','password2')}),)
        return ((None, {'fields': ('email', 'phone_number','groups', 'is_active','is_staff','password')}),)

    # readonly_fields = ['user_type']
    # exclude = ['last_login','is_superuser','user_type','is_phone_number_verified','is_staff']

    # def user_name(self, object):
       # return object.staffprofile

    def get_queryset(self, request):
        # use our manager, rather than the default one
        qs = self.model.objects.get_queryset()

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_changeform_initial_data(self, request):
        return {'user_type': 1}

