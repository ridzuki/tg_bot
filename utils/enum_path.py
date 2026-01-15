import os
from enum import Enum


class Path(Enum):
    PROMPTS = os.path.join('resources', 'prompts')
    IMG_DIR = os.path.join('resources', 'images')
    MESSAGES = os.path.join('resources', 'messages')
    IMAGES = os.path.join('resources', 'images', '{file}.jpg')
    OTHER = os.path.join('resources', 'other')
