from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Company
from api.serializers import CompanyDetailSerializer


class CompanyBrokersGroupsView(APIView):
    def get(self, request):
        company_id = request.data.get('company_id') or request.query_params.get('company_id')

        if not company_id:
            return Response({"error": "Missing company_id in request"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            company = get_object_or_404(Company, id=company_id)
            company_data = CompanyDetailSerializer(company).data
            return Response(company_data)
        except ValueError:
            return Response({"error": "Invalid company_id format"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
