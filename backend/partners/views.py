from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.utils import get_client_ip

from .integrations import send_application_emails
from .serializers import PartnerApplicationCreateSerializer
from .throttles import PartnerApplicationThrottle


class PartnerApplicationCreateView(CreateAPIView):
    serializer_class = PartnerApplicationCreateSerializer
    permission_classes = [AllowAny]
    throttle_classes = [PartnerApplicationThrottle]

    def create(self, request, *args, **kwargs):
        # Stash the proxy-aware client IP on the request so the serializer
        # can pass it to Turnstile and so we can save it on the instance.
        request.client_ip = get_client_ip(request)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save(source_ip=request.client_ip)

        send_application_emails(application)

        return Response(
            {"id": application.id, "contact_name": application.contact_name},
            status=201,
        )
