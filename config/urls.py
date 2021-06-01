
from django.urls import include, path
from django.conf.urls import url
from django.conf.urls.static import static

from django.contrib import admin
from django.conf import settings

# DEBUG = env.bool('DJANGO_DEBUG', default=True)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('keel.api.urls')),
] 

# path('', include('keel.random.urls', namespace='random')),
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ] 