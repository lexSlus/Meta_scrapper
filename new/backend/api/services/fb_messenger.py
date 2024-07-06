import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class FBMessengerService:
    page_id = settings.FB_PAGE_ID
    access_token = settings.FB_PAGE_ACCESS_TOKEN

    def send_message(self, text: str, recipient: str) -> dict:
        url = f"https://graph.facebook.com/v15.0/{self.page_id}/messages?access_token={self.access_token}"
        data = {
            "recipient": {"id": recipient},
            "messaging_type": "MESSAGE_TAG",
            "message": {"text": text},
            "tag": "CONFIRMED_EVENT_UPDATE",
        }
        try:
            result = requests.post(url, json=data, timeout=settings.RESPONSE_TIMEOUT).json()
            logger.warning(f"Message result {recipient}: {result}")
            return result
        except Exception as e:
            logger.error(f"FBMessengerService.send_message: {e}")
            raise e

    def send_posts(self, posts: list[str], recipient: str) -> None:
        messages = []
        current_message = ""

        for post in posts:
            if len(current_message + post) + len("\n") <= 2000:
                current_message += post + "\n"
            else:
                # Remove trailing newline
                messages.append(current_message.rstrip("\n"))
                current_message = post + "\n"

        # Add the remaining string if any
        if current_message:
            messages.append(current_message.rstrip("\n"))

        for message in messages:
            self.send_message(message, recipient)
