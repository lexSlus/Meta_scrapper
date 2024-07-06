# Generated by Django 5.0.1 on 2024-03-12 15:26

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0008_company_alter_pva_cookies"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="group",
            name="fb_link",
        ),
        migrations.RemoveField(
            model_name="group",
            name="last_post_link",
        ),
        migrations.AddField(
            model_name="broker",
            name="company",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to="api.company"),
        ),
        migrations.AddField(
            model_name="group",
            name="fb_id",
            field=models.CharField(default="", max_length=30),
        ),
        migrations.AddField(
            model_name="group",
            name="last_post_id",
            field=models.CharField(default="", max_length=30),
        ),
        migrations.CreateModel(
            name="BrokerGroup",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("broker", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.broker")),
                ("group", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.group")),
            ],
        ),
        migrations.AddField(
            model_name="broker",
            name="groups",
            field=models.ManyToManyField(related_name="groups", through="api.BrokerGroup", to="api.group"),
        ),
    ]
