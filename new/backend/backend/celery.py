import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.dev_settings")
# Create a Celery instance and configure it using the Django settings.
app = Celery("backend")

# Load task modules from all registered Django app configs.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()
