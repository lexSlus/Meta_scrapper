from rest_framework import serializers
from .models import CompanyUser, Company
from rest_framework_simplejwt.tokens import RefreshToken


class AccountSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())

    class Meta:
        model = CompanyUser
        fields = ['email', 'name', 'is_active', 'is_staff', 'is_superuser', 'company']


class AccountSerializerWithToken(AccountSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta(AccountSerializer.Meta):
        fields = AccountSerializer.Meta.fields + ['token']

    def get_token(self, obj):
        refresh = RefreshToken.for_user(obj)
        return str(refresh.access_token)
