from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from app_auth.models import CompanyUser
from app_auth.serializers import AccountSerializerWithToken


@api_view(['POST'])
def registerUser(request):
    data = request.data
    required_fields = ['email', 'password', 'name']
    if not all(field in data for field in required_fields):
        return Response({'detail': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    if CompanyUser.objects.filter(email=data['email']).exists():
        return Response({'detail': 'Account with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CompanyUser.objects.create_user(
            email=data['email'],
            password=data['password'],
            name=data['name']
        )
        if 'company' in data:
            user.company_id = data['company']
            user.save()

        serializer = AccountSerializerWithToken(user, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        message = {'detail': str(e)}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
