from django.conf import settings
from django.dispatch import Signal, receiver

from api.services.fb_messenger import FBMessengerService

activation_signal = Signal()


@receiver(activation_signal)
def send_initial_message(sender, fb_id, **kwargs):
    messenger = FBMessengerService()
    messenger.send_message(settings.INITIAL_MESSAGE, fb_id)
