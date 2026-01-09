import json

from utils import FileManager
from .enums import GPTRole
from utils.enum_path import Path


class GPTMessage:

    def __init__(self, prompt: str, message_list: list[dict[str, str]] | None = None):
        self._prompt_path = prompt
        self.message_list = message_list if message_list else self._init_message()

    def _init_message(self) -> list[dict[str, str]]:
        message = {
            'role': GPTRole.SYSTEM.value,
            'content': self._load_prompt(),
        }
        return [message]

    def _load_prompt(self) -> str:
        prompt = FileManager.read_txt(Path.PROMPTS, self._prompt_path)
        return prompt

    def update(self, role: GPTRole, message: str):
        message = {
            'role': role.value,
            'content': message,
        }
        self.message_list.append(message)

    def json(self):
        item = json.dumps(
            self,
            default=lambda i: i.__dict__,
            ensure_ascii=False,
            indent=4
        )
        return item

    @classmethod
    def from_json(cls, data: str):
        json_data = json.loads(data)
        return cls(json_data['_prompt_name'], json_data['message_list'])