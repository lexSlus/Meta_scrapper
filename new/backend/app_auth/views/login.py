from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


@api_view(['POST'])
def loginUser(request):
    data = request.data
    email = data.get('email')
    password = data.get('password')
    if email is None or password is None:
        return Response({'detail': 'Please provide both email and password.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, email=email, password=password)

    if user is not None:
        if not user.is_active:
            return Response({'detail': 'User account is not active.'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            'email': user.email,
            'token': str(refresh.access_token),
            'refresh_token': str(refresh)
        }, status=status.HTTP_200_OK)
    else:
        return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
