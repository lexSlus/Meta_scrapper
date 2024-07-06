from rest_framework import serializers

from .models import Company, Group, Broker, PVA, Keyword, KeywordBroker, BrokerGroup, SupportRequest
from app_auth.models import CompanyUser


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'is_staff', 'is_active']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'fb_id', 'last_post_id', 'is_active']


class BrokerSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=CompanyUser.objects.all(),
                                              default=serializers.CurrentUserDefault())
    groups = serializers.SerializerMethodField()

    class Meta:
        model = Broker
        fields = ['id', 'fb_id', 'is_activated', 'fb_link', 'is_active', 'company', 'groups', 'user']

    def get_groups(self, obj):
        groups = Group.objects.filter(brokergroup__broker=obj)
        return GroupSerializer(groups, many=True).data


class PVASerializer(serializers.ModelSerializer):
    class Meta:
        model = PVA
        fields = ['id', 'proxy_ip', 'username', 'password', 'cookies', 'is_active']


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ['id', 'name', 'description', 'brokers', 'is_active']
        depth = 1


class KeywordBrokerSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeywordBroker
        fields = ['id', 'broker', 'keyword', 'is_active']


class BrokerGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrokerGroup
        fields = ['id', 'broker', 'group', 'is_active']


class CompanyDetailSerializer(serializers.ModelSerializer):
    brokers = BrokerSerializer(many=True, read_only=True, source='companies')

    class Meta:
        model = Company
        fields = ['id', 'name', 'is_staff', 'is_active', 'brokers']

class SupportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequest
        fields = ['contact_email', 'topic', 'details']