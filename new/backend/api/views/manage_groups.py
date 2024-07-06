from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction

from api.models import Group
from api.serializers import GroupSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    @action(detail=False, methods=['post'], url_path='batch-create')
    def batch_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'], url_path='batch-update')
    def batch_update(self, request, *args, **kwargs):
        with transaction.atomic():
            data = request.data
            for group_data in data:
                instance = Group.objects.get(pk=group_data['id'])
                serializer = self.get_serializer(instance, data=group_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"status": "batch update successful"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], url_path='batch-delete')
    def batch_delete(self, request, *args, **kwargs):
        ids = request.data['ids']
        Group.objects.filter(id__in=ids).delete()
        return Response({"status": "batch delete successful"}, status=status.HTTP_204_NO_CONTENT)
