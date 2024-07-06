from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.tasks import healthcheck


class Smoke(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Running..."}, status=status.HTTP_200_OK)


class CeleryHealthcheck(APIView):
    def get(self, request, *args, **kwargs):
        healthcheck.delay()
        return Response({"message": "Running..."}, status=status.HTTP_200_OK)
