from uuid import UUID

import pytest

from api.models import Broker, Company
from api.services.fb_payload import FBMessengerPayloadService


@pytest.fixture
def payload(broker_id: Broker, fb_id):
    return {
        "object": "page",
        "entry": [
            {
                "id": "215452144981555",
                "time": 1705573172814,
                "messaging": [
                    {
                        "recipient": {"id": "215452144981555"},
                        "timestamp": 1705573172814,
                        "sender": {"id": fb_id},
                        "optin": {"ref": f"{broker_id}"},
                    }
                ],
            }
        ],
    }


@pytest.fixture
def fb_id():
    return "24567101576268711"


@pytest.fixture
def broker_id():
    return UUID("472e8b8f-f054-40a9-b376-2c270b92e061")


class TestFBMessengerPayload:
    @pytest.mark.django_db
    def test_create_success(self, broker_id, payload, fb_id):
        test_company = Company.objects.create()
        Broker.objects.create(id=broker_id, company=test_company)
        payload = FBMessengerPayloadService(payload)

        payload.is_valid()

        assert payload.data.fb_id == fb_id
        assert payload.data.actual_id == broker_id
