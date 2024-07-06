from django.conf import settings
from django.shortcuts import render
from django.views import View


class MessageRequestPage(View):
    # Page to request broker consent for messaging

    def get(self, request, broker_token: str | None = None):
        context = {"app_id": settings.FB_APP_ID, "page_id": settings.FB_PAGE_ID, "broker_token": broker_token}
        return render(request, "api/fb_message_consent.html", context)
