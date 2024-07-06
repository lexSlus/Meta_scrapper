import ast
from typing import Dict

from openai import OpenAI


class OpenAIService:
    def __init__(self) -> None:
        self.client = OpenAI()
        self.model = "gpt-3.5-turbo"

    def generate_response(self, text: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a virtual assistant. You help users generate a response "
                    "to their message as if you are interested in helping them out.",
                },
                {"role": "user", "content": text},
            ],
        )

        return completion.choices[0].message.content

    def classify_action(self, text: str, actions: Dict[str, str]) -> list[str]:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a virtual assistant. You need to classify "
                    f"the action users are interested in. Allowed actions and their description: {actions}. "
                    "Respond in Python list format like this ['<action>', ...]. Where <action> is a key from the actions above. "
                    "If action is not related to the real estate, respond as ['None']. "
                    "If you can't detect any action from the list, respond as ['None'].",
                },
                {"role": "user", "content": text},
            ],
        )

        return ast.literal_eval(completion.choices[0].message.content)
