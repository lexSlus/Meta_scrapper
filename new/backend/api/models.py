"""Note:
- is_active fields means if the object should be used AKA if blocked
"""

from uuid import uuid4

from django.db import models


class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    name = models.CharField(max_length=70)

    # Is a LeadTrek property
    is_staff = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    fb_id = models.CharField(max_length=30, unique=True)

    last_post_id = models.CharField(max_length=30, default="")

    is_active = models.BooleanField(default=True)


class Broker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    fb_id = models.CharField(max_length=50, default="", blank=True)

    # is_activated means if bot notifications are set
    is_activated = models.BooleanField(default=False)
    fb_link = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group, through="BrokerGroup", related_name="groups")


class PVA(models.Model):
    """FakeAccounts, PVA - phone verified account."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    proxy_ip = models.CharField(max_length=20)

    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    cookies = models.CharField(max_length=3000, default="[]")

    is_active = models.BooleanField(default=True)


class Keyword(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)

    name = models.CharField(max_length=20)
    description = models.CharField(max_length=1000)
    brokers = models.ManyToManyField(Broker, through="KeywordBroker", related_name="keywords")

    is_active = models.BooleanField(default=True)


class KeywordBroker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)

    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)

    is_active = models.BooleanField(default=True)


class BrokerGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)

    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    is_active = models.BooleanField(default=True)

class SupportRequest(models.Model):
    contact_email = models.EmailField()
    topic = models.CharField(max_length=255)
    details = models.TextField()

    def __str__(self):
        return f"{self.topic} by {self.contact_email}"