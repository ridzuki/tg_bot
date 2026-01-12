import openai
import config

from aiogram import Bot
from .enums import GPTModel
from .messages import GPTMessage
from logger import logger


class GPTService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, text_model: GPTModel.GPT_4_TURBO, image_model: GPTModel.GPT_IMAGE):
        self._gpt_token = config.AI_TOKEN
        self._client = self._create_client()
        self._text_model = text_model.value
        self._image_model = image_model.value

    def _create_client(self):
        gpt_client = openai.AsyncOpenAI(
            api_key=self._gpt_token
        )
        return gpt_client

    async def request(self, message_list: GPTMessage, bot: Bot) -> str:
        try:
            response = await self._client.chat.completions.create(
                messages=message_list.message_list,
                model=self._text_model,
            )
            logger.info(f"[GPT] Success request: {response.choices[0].message.content}")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"[GPT] Error request processing: {e}")
            await bot.send_message(
                chat_id=config.ADMIN_ID,
                text=str(e),
            )

    async def generate_image(self, prompt: str, bot: Bot) -> str:
        try:
            image = await self._client.images.generate(
                model=self._image_model,
                prompt=prompt,
                size="1024x1024"
            )
            logger.info(f"[GPT] Success image generation: {image.data[0].url}")
            return image.data[0].url
        except Exception as e:
            logger.error(f"[GPT] Error image generation: {e}")
            await bot.send_message(
                chat_id=config.ADMIN_ID,
                text=str(e),
            )
            raise
