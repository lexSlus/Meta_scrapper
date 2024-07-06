from backend.settings.dev_settings import *

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ["DB_HOST"],
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASS"],
    }
}

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

AWS_S3_ACCESS_KEY_ID = os.environ("AWS_S3_ACCESS_KEY_ID")
AWS_S3_SECRET_ACCESS_KEY = os.environ("AWS_S3_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ("AWS_STORAGE_BUCKET_NAME")

AWS_DEFAULT_ACL = None

AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

# s3 static settings
STATICFILES_STORAGE = "backend.s3_backends.StaticS3Storage"

# s3 public media settings
DEFAULT_FILE_STORAGE = "backend.s3_backends.MediaS3Storage"


AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION_NAME = os.environ.get("AWS_REGION_NAME")
DEFAULT_SUPPORT_EMAIL = 'support@example.com'
