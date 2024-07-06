import logging
from dataclasses import dataclass
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from api.models import Broker

logger = logging.getLogger(__name__)


@dataclass
class FBMessengerPayload:
    actual_id: UUID | None = None
    fb_id: str | None = None
    broker: Broker | None = None


class FBMessengerPayloadService:
    """Class is responsible for processing this payload
    from FB Messenger event after a broker presses
    the 'Subscribe in messenger':

    data = {
        "object":"page",
        "entry":[
            {
                "id":"215452144981555",
                "time":1705573172814,
                "messaging":[
                    {
                        "recipient":{"id":"215452144981555"},
                        "timestamp":1705573172814,
                        "sender":{"id":"24567101576268711"},
                        "optin":{
                            "ref":"ADDITIONAL_USER_INFO|47a48014-13de-4132-8db6-664472dd8db0"
                        }
                    }
                ]
            }
        ]
    }
    """

    def __init__(self, payload: dict):
        self.payload = payload
        self.data = FBMessengerPayload()

    def is_valid(self) -> bool:
        try:
            info = self.payload["entry"][0]["messaging"][0]

            self.data.fb_id = info["sender"]["id"]
            self.data.actual_id = UUID(info["optin"]["ref"])
        except (KeyError, IndexError):
            logger.warning(f"FBMessengerPayloadService, not valid FB response: {self.payload}")
            return False

        try:
            self.data.broker = Broker.objects.get(id=self.data.actual_id)
            self.data.broker.fb_id = self.data.fb_id
            self.data.broker.is_activated = True
            self.data.broker.save()

            return True
        except ObjectDoesNotExist:
            return False
