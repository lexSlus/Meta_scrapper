from django.urls import path, include

from rest_framework.routers import DefaultRouter
from api.views import CeleryHealthcheck, MessageRequestPage, MessageRequestView, Smoke
from api.views.fb_webhooks import MessageRequestView
from api.views.broker import BrokerView
from api.views.group import GroupView
from api.views.company import CompanyView
from api.views.CompanyBrokersGroupsView import CompanyBrokersGroupsView
from api.views.support import SupportRequestAPI
from api.views.manage_brokers import BrokerViewSet
from api.views.manage_groups import GroupViewSet

router = DefaultRouter()
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'brokers', BrokerViewSet, basename='broker')

urlpatterns = [
    path("", Smoke.as_view(), name="smoke"),
    path("celery", CeleryHealthcheck.as_view(), name="celery"),
    path("message_page/<str:broker_token>/", MessageRequestPage.as_view(), name="message-page"),
    path("message_view/", MessageRequestView.as_view(), name="message-view"),
    path('manage/', include(router.urls)),

    path('broker/', BrokerView.as_view(), name="brokers"),
    path('group/', GroupView.as_view(), name="groups"),
    path('company/', CompanyView.as_view(), name='company_manage'),
    path('company/details/', CompanyBrokersGroupsView.as_view(), name='company-brokers-groups'),
    path('support/', SupportRequestAPI.as_view(), name='support_api'),

]
