from .gpt_client import GPTService
from .enums import GPTModel

chat_gpt = GPTService(text_model=GPTModel.GPT_4_TURBO, image_model=GPTModel.GPT_IMAGE)
