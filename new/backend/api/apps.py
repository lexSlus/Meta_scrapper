from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        # Import celery app now that Django is mostly ready.
        # This initializes Celery and autodiscovers tasks
        pass
