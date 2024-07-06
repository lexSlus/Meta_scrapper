import boto3
from django.conf import settings


def send_support_email(subject, message, recipient_email):
    ses_client = boto3.client(
        'ses',
        region_name=settings.AWS_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

    response = ses_client.send_email(
        Source=settings.DEFAULT_SUPPORT_EMAIL,
        Destination={'ToAddresses': [recipient_email]},
        Message={
            'Subject': {'Data': subject},
            'Body': {
                'Text': {'Data': message}
            }
        }
    )
    return response
