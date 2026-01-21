from utils import FileManager
from utils.enum_path import Path


def build_topic_map(file_path: Path, file_name: str):
    """
        Создаёт словарь на основе файла с данными
    """
    topic_map = {}
    lines = FileManager.read_txt(file_path, file_name).splitlines()
    for line in lines:
        line = line.strip()
        if not line or ":" not in line:
            continue
        category, genres_str = line.split(":", 1)
        category = category.strip()
        topic_name  = f"{category.lower()}"
        genres_list = [g.strip() for g in genres_str.split(",")]

        topic_map[topic_name] = {
            "category": category,
            "genres": [g for g in genres_list]
        }

    return topic_map

