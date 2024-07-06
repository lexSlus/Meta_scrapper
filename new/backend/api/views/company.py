from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Company
from api.serializers import CompanySerializer
from rest_framework.permissions import IsAuthenticated


class CompanyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        id = request.data.get('id') or request.query_params.get('id')
        if id is None:
            return Response({'error': 'Missing company ID'}, status=status.HTTP_400_BAD_REQUEST)

        company = get_object_or_404(Company, id=id)
        serializer = CompanySerializer(company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        id = request.data.get('id') or request.query_params.get('id')
        if id:
            company = get_object_or_404(Company, id=id)
            company.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'Missing company ID'}, status=status.HTTP_400_BAD_REQUEST)
