from django.contrib.gis import admin
# from keel.lead.models import UserLead
from .user import CustomUserAdmin

User = get_user_model()

# Admin Site config
admin.site.site_header = 'keel CRM'
admin.site.site_title = 'keel CRM'
admin.site.site_url = None
admin.site.index_title = 'CRM Administration'


admin.site.register(User, CustomUserAdmin)
