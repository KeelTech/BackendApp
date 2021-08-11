from django.conf.urls import include
from django.urls import path

from .auth.router import urlpatterns as auth_url
from .calendly.router import urlpatterns as calendly_url
from .cases.router import urlpatterns as cases_url
from .chats.router import urlpatterns as chats_url
from .document.router import urlpatterns as documents_url
from .eligibility_calculator.router import urlpatterns as eligibility_url
from .leads.router import urlpatterns as leads_url
from .plans.router import urlpatterns as plans_url
from .tasks.router import urlpatterns as tasks_url
from .core.router import urlpatterns as core_url

urlpatterns = [

    path('user/', include(auth_url), name="authentication"),
    path('leads/', include(leads_url)),
    path('eligibility/', include(eligibility_url)),
    path('doc/', include(documents_url)),
    path('tasks/', include(tasks_url)),
    path('chats/', include(chats_url)),
    path('cases/', include(cases_url)),
    path('plans/', include(plans_url)),
    path('calendly/', include(calendly_url)),
    path('core/', include(core_url)),
]
