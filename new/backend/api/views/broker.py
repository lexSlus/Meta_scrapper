from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app_auth.models import CompanyUser
from api.models import Broker, Company
from api.serializers import BrokerSerializer
from rest_framework.permissions import IsAuthenticated


class BrokerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        brokers = Broker.objects.all()
        serializer = BrokerSerializer(brokers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BrokerSerializer(data=request.data)
        if serializer.is_valid():
            user = CompanyUser.objects.first()
            company = Company.objects.first()
            serializer.save(user=user, company=company)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        id = request.data.get('id') or request.query_params.get('id')
        if id is None:
            return Response({'error': 'Missing broker ID'}, status=status.HTTP_400_BAD_REQUEST)

        broker = get_object_or_404(Broker, id=id)
        serializer = BrokerSerializer(broker, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        id = request.data.get('id') or request.query_params.get('id')
        if id:
            broker = get_object_or_404(Broker, id=id)
            broker.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Missing broker ID'}, status=status.HTTP_400_BAD_REQUEST)
