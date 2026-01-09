import asyncio
from aiogram import Bot
from aiogram.enums import ChatAction
from aiogram.types import Message


class LoadingController:
    def __init__(
        self,
        bot: Bot,
        chat_id: int,
        message: Message,
        text: str = "Текст",
        animation_delay: float = 0.5,
        typing_delay: float = 4.0,
    ):
        self.bot = bot
        self.chat_id = chat_id
        self.message = message
        self.text = text
        self.animation_delay = animation_delay
        self.typing_delay = typing_delay

        self._running = False
        self._animation_task: asyncio.Task | None = None
        self._typing_task: asyncio.Task | None = None

    async def _loading_animation(self):
        dots = ["", ".", "..", "..."]
        i = 0
        while self._running:
            try:
                await self.bot.edit_message_caption(
                    chat_id=self.chat_id,
                    message_id=self.message.message_id,
                    caption=f"{self.text}{dots[i % len(dots)]}",
                )
            except:
                pass
            i += 1
            await asyncio.sleep(self.animation_delay)

    async def _typing_loop(self):
        while self._running:
            try:
                await self.bot.send_chat_action(
                    chat_id=self.chat_id,
                    action=ChatAction.TYPING,
                )
            except:
                pass
            await asyncio.sleep(self.typing_delay)

    async def start(self):
        self._running = True
        self._animation_task = asyncio.create_task(self._loading_animation())
        self._typing_task = asyncio.create_task(self._typing_loop())

    async def stop(self):
        self._running = False

        if self._animation_task:
            await self._animation_task
        if self._typing_task:
            await self._typing_task

    def update_text(self, new_text: str):
        self.text = new_text
