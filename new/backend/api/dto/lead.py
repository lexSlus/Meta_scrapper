import re
from dataclasses import dataclass


@dataclass
class Lead:
    user_link: str | None
    post_text: str | None
    post_link: str | None

    generated_message: str | None = None
    post_keywords: list[str] | None = None

    @property
    def post_id(self) -> str | None:
        if not self.post_link:
            return None
        return re.search(r"/([^/]+)/$", self.post_link).group(1)

    def __str__(self):
        actions = ", ".join(self.post_keywords) if self.post_keywords else None
        return (
            f"Generated message: {self.generated_message}\n"
            f"Post text: {self.post_text}\n"
            f"Post keywords: {actions}\n"
            f"Post link: {self.post_link}\n"
            f"User link: https://www.facebook.com{self.user_link}\n"
        )

    def __eq__(self, other):
        if not isinstance(other, Lead):
            return False
        return self.post_link == other.post_link

    def __hash__(self):
        return hash(self.post_link)

    def matches_keyword(self, keywords: list[str]) -> bool:
        """Returns True if any post_keyword is in keywords."""
        return any(keyword in keywords for keyword in self.post_keywords)
