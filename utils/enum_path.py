import os
from enum import Enum


class Path(Enum):
    PROMPTS = os.path.join('resources', 'prompts')
    MESSAGES = os.path.join('resources', 'messages')
    IMAGES = os.path.join('resources', 'images', '{file}.jpg')