from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Group
from api.serializers import GroupSerializer
from rest_framework.permissions import IsAuthenticated


class GroupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        id = request.data.get('id') or request.query_params.get('id')
        if id is None:
            return Response({'error': 'Missing group ID'}, status=status.HTTP_400_BAD_REQUEST)

        group = get_object_or_404(Group, id=id)
        serializer = GroupSerializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        id = request.data.get('id') or request.query_params.get('id')
        if id:
            group = get_object_or_404(Group, id=id)
            group.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Missing group ID'}, status=status.HTTP_400_BAD_REQUEST)
