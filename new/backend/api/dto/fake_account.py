from dataclasses import dataclass

from django.conf import settings

from api.dto import GroupDTO


@dataclass
class FakeAccount:
    username: str
    password: str
    cookies: list[dict]
    proxy_ip: str
    proxy_username: str
    proxy_password: str
    groups: list[GroupDTO]

    new_cookies: list[dict] | None = None

    @property
    def proxy_url(self) -> str:
        return f"http://{self.proxy_username}:{self.proxy_password}@{self.proxy_ip}"
