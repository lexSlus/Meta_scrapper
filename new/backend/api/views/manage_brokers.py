from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction

from api.models import Broker
from api.serializers import BrokerSerializer


class BrokerViewSet(viewsets.ModelViewSet):
    queryset = Broker.objects.all()
    serializer_class = BrokerSerializer

    @action(detail=False, methods=['patch'], url_path='batch-update')
    def batch_update(self, request, *args, **kwargs):
        if not request.data:
            return Response({"error": "No data provided"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            data = request.data
            errors = []
            for broker_data in data:
                try:
                    broker = Broker.objects.get(pk=broker_data['id'])
                    serializer = self.get_serializer(broker, data=broker_data, partial=True)
                    if serializer.is_valid(raise_exception=False):
                        serializer.save()
                    else:
                        errors.append({broker_data['id']: serializer.errors})
                except Broker.DoesNotExist:
                    errors.append({broker_data['id']: "Broker not found"})
                except Exception as e:
                    errors.append({broker_data['id']: str(e)})

            if errors:
                return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Batch update successful"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], url_path='batch-delete')
    def batch_delete(self, request, *args, **kwargs):
        ids = request.data.get('ids')
        if not ids:
            return Response({"error": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count = Broker.objects.filter(id__in=ids).delete()[0]
        if deleted_count == 0:
            return Response({"error": "No brokers found with the provided IDs"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": f"Successfully deleted {deleted_count} brokers"}, status=status.HTTP_204_NO_CONTENT)
