from django.conf.urls import url, include
from django.urls import path

from .v1.doctor.router import urlpatterns as doctor_url
from .v1.auth.router import urlpatterns as auth_url
from .v1.diagnostic.router import urlpatterns as diag_url
from .v1.chat.router import urlpatterns as chat_url
from .v1.notification.router import urlpatterns as noti_url
from .v1.payout.router import urlpatterns as payout_url
from .v1.article.router import urlpatterns as article_url
from .v1.admin.router import urlpatterns as admin_url
from .v1.web.router import urlpatterns as web_url
from .v1.common.router import urlpatterns as common_url
from .v1.location.router import urlpatterns as location_url
from .v1.tracking.router import urlpatterns as track_url
from .v1.ratings.router import urlpatterns as rating_url
from .v1.geoip.router import urlpatterns as geoip_url
from .v1.insurance.router import urlpatterns as insurance_url
from .v1.matrix.router import urlpatterns as matrix_url
# from .v1.account.router import urlpatterns as acct_url
from .v1.coupon.router import urlpatterns as coupon_url
from .v1.procedure.router import urlpatterns as procedure_url
from .v1.banner.router import urlpatterns as banner_url
from .v1.cart.router import urlpatterns as cart_url
from .v1.screen.router import urlpatterns as screen_url
from .v1.subscription_plan.router import urlpatterns as subscription_plan_url

from .v2.doctor.router import urlpatterns as doctor_v2_url
from .v2.lab.router import urlpatterns as lab_v2_url
from .v1.integrations.router import urlpatterns as integrations_url
from .v1.prescription.router import urlpatterns as prescription_url
from .v1.salespoint.router import urlpatterns as salespoint_url
from .v1.plus.router import urlpatterns as plus_url
from .v1.bookinganalytics.router import urlpatterns as bookinganalytics_url


urlpatterns = [
    path('v1/doctor/', include(doctor_url)),
    path('v1/user/', include(auth_url)),
    path('v1/diagnostic/', include(diag_url)),
    path('v1/chat/', include(chat_url)),
    path('v1/notification/', include(noti_url)),
    # path('v1/account/', include(acct_url)),
    path('v1/payout/', include(payout_url)),
    path('v1/article/', include(article_url)),
    path('v1/web/', include(web_url)),
    path('v1/admin/', include(admin_url)),
    path('v1/common/', include(common_url)),
    path('v1/location/', include(location_url)),
    path('v1/tracking/', include(track_url)),
    path('v1/ratings/', include(rating_url)),
    path('v1/geoip/', include(geoip_url)),
    path('v1/insurance/', include(insurance_url)),
    path('v1/coupon/', include(coupon_url)),
    path('v1/procedure/', include(procedure_url)),
    path('v1/matrix/', include(matrix_url)),
    path('v1/banner/', include(banner_url)),
    path('v1/cart/', include(cart_url)),
    path('v1/screen/', include(screen_url)),
    path('v1/subscription_plan/', include(subscription_plan_url)),
    path('v2/doctor/', include(doctor_v2_url)),
    path('v2/lab/', include(lab_v2_url)),
    path('v1/integrations/', include(integrations_url)),
    path('v1/prescription/', include(prescription_url)),
    path('v1/salespoint/', include(salespoint_url)),
    path('v1/plus/', include(plus_url)),
    path('v1/bookinganalytics/', include(bookinganalytics_url))
]
