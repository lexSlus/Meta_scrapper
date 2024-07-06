from django.contrib import admin

from api.models import PVA, Broker, BrokerGroup, Company, Group, Keyword, KeywordBroker

admin.site.register(Company)
admin.site.register(Broker)
admin.site.register(Group)
admin.site.register(PVA)
admin.site.register(Keyword)
admin.site.register(KeywordBroker)
admin.site.register(BrokerGroup)
