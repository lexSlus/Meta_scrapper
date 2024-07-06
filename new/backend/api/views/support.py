from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.send_email import send_support_email
from api.serializers import SupportRequestSerializer


class SupportRequestAPI(APIView):
    def post(self, request):
        serializer = SupportRequestSerializer(data=request.data)
        if serializer.is_valid():
            support_request = serializer.save()
            send_support_email(
                subject=f"New Support Request: {support_request.topic}",
                message=f"From: {support_request.contact_email}\n\nDetails: {support_request.details}",
                recipient_email=settings.DEFAULT_SUPPORT_EMAIL
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
