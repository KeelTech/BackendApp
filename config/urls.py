
from django.urls import include, path
from django.conf.urls import url
from django.conf.urls.static import static

from django.contrib import admin
from django.conf import settings

# DEBUG = env.bool('DJANGO_DEBUG', default=True)


urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/', include('keel.api.urls')),
]  +  static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# path('', include('keel.random.urls', namespace='random')),

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ] 