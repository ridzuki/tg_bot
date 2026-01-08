import asyncio
from aiogram import Bot, Dispatcher
from handlers import main_router
import config
import misc


bot = Bot(token=config.TG_TOKEN)
dp = Dispatcher()


async def start_bot():
    dp.startup.register(misc.on_start)
    dp.shutdown.register(misc.on_stop)
    dp.include_router(main_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        pass