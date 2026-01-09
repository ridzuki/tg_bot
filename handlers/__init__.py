from aiogram import Router

from .handlers import command_router
from .fsm_handlers import fsm_router
from .inline_handlers import inline_router

main_router = Router()

main_router.include_routers(

    fsm_router,
    inline_router,
    command_router,
)