from keel.api.v1.auth import serializers
from keel.authentication.models import UserSecretKey
from django.contrib.auth import get_user_model
import logging
import jwt
import math
from keel.api.v1.admin import serializers
from keel.crm.constants import constants

from io import BytesIO
from rest_framework.response import Response
logger = logging.getLogger(__name__)
User = get_user_model()

from rest_framework.decorators import api_view
from rest_framework.response import Response
from keel.articles.serializers import ArticleImageSerializer
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image as Img
from keel.articles.models import ArticleImage
from keel.authentication.models import WhiteListedLoginTokens

@api_view(['POST'])
def upload(request):
    data = {}
    data['name'] = request.data.get('upload')
    uploaded_image = request.data.get('upload')
    max_allowed = 1000
    img = Img.open(uploaded_image)
    size = img.size

    if max(size)>max_allowed:
        size = tuple(math.floor(ti/(max(size)/max_allowed)) for ti in size)

    img = img.resize(size, Img.ANTIALIAS)

    if img.mode != 'RGB':
        img = img.convert('RGB')

    new_image_io = BytesIO()
    img.save(new_image_io, format='JPEG')

    image = InMemoryUploadedFile(new_image_io, None, uploaded_image.name, 'image/jpeg',
                                        new_image_io.tell(), None)
    ai = ArticleImage(name=image)
    ai.save()

    return Response({'uploaded': 1, 'url': request.build_absolute_uri(ai.name.url)})


def userlogin_via_agent(request):
    from django.http import JsonResponse
    from keel.authentication.backends import JWTAuthentication
    response = {'login': 0}
    if request.method != 'GET':
        return JsonResponse(response, status=405)

    serializer = serializers.AgentVerificationSerializer(data=request.GET)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    user_type = data["user_type"]

    if user_type == User.DOCTOR and not (request.user.is_superuser or request.user.groups.filter(name='provider_group').exists()):
        return JsonResponse(response, status=403)

    if user_type == User.CONSUMER and not request.user.groups.filter(name=constants['LAB_APPOINTMENT_MANAGEMENT_TEAM']).exists()  and \
            not request.user.groups.filter(name=constants['OPD_APPOINTMENT_MANAGEMENT_TEAM']).exists() and \
            not request.user.groups.filter(name=constants['SALES_CALLING_TEAM']).exists():
        return JsonResponse(response, status=403)

    user = User.objects.filter(phone_number=data['phone_number'], user_type=user_type).first()
    if not user and user_type == User.CONSUMER:
        user = User.objects.create(phone_number=data['phone_number'],
                                   is_phone_number_verified=False,
                                   user_type=User.CONSUMER, auto_created=True,
                                   source='Agent')

    if not user:
        return JsonResponse(response, status=400)

    can_book = False
    if request.user.groups.filter(name=constants['APPOINTMENT_OTP_BYPASS_AGENT_TEAM']).exists():
        can_book = True

    user_key = UserSecretKey.objects.get_or_create(user=user)
    payload = JWTAuthentication.appointment_agent_payload_handler(request, user, can_book=can_book)
    token = jwt.encode(payload, user_key[0].key)
    response = {
        "login": 1,
        "agent_id": request.user.id,
        "token": str(token, 'utf-8'),
        "expiration_time": payload['exp'],
        "refresh": False
    }
    return JsonResponse(response)
