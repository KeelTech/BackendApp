from django.contrib import admin
# from .user import CustomUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

# Admin Site config
admin.site.site_header = 'keel CRM'
admin.site.site_title = 'keel CRM'
# admin.site.site_url = None
admin.site.index_title = 'CRM Administration'


# admin.site.register(User)
