import json
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from api.services.fb_payload import FBMessengerPayloadService
from api.signals.activation import activation_signal

logger = logging.getLogger(__name__)


class VerificationView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Get method for FB webhook verification process."""
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        logger.info(f"MessageRequestView.get: {mode, token, challenge}")

        if mode == "subscribe" and token == settings.FB_VERIFICATION_TOKEN:
            return HttpResponse(challenge)
        else:
            return HttpResponseBadRequest("Invalid verification token")


class MessageRequestView(VerificationView):
    def post(self, request, *args, **kwargs):
        raw_payload = json.loads(request.body)

        payload = FBMessengerPayloadService(raw_payload)

        if payload.is_valid():
            activation_signal.send(sender=self.__class__, fb_id=payload.data.fb_id)

            return HttpResponse("Broker verified")

        return HttpResponseBadRequest("Invalid verification information")
