import openai
from aiogram import Bot

import config
from .enums import GPTModel
from .messages import GPTMessage


class GPTService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model: GPTModel = GPTModel.GPT_4_TURBO):
        self._gpt_token = config.AI_TOKEN
        self._client = self._create_client()
        self._model = model.value

    def _create_client(self):
        gpt_client = openai.AsyncOpenAI(
            api_key=self._gpt_token
        )
        return gpt_client

    async def request(self, message_list: GPTMessage, bot: Bot) -> str:
        try:
            response = await self._client.chat.completions.create(
                messages=message_list.message_list,
                model=self._model,
            )
            return response.choices[0].message.content
        except Exception as e:
            await bot.send_message(
                chat_id=config.ADMIN_ID,
                text=str(e),
            )
