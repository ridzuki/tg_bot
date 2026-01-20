from aiogram.filters.callback_data import CallbackData

class CallbackMenu(CallbackData, prefix='CM'):
    button: str


class CallbackTalk(CallbackData, prefix='CT'):
    button: str
    celebrity: str


class CallbackQUIZ(CallbackData, prefix='CQ'):
    button: str
    subject: str


class CallbackTranslate(CallbackData, prefix="CTLang"):
    button: str
    language: str


class CallbackRecommend(CallbackData, prefix="CR"):
    button: str
    category: str | None = None
    genre: str | None = None
    item: str | None = None