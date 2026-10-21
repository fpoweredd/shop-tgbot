from tgbot.data.config import PATH_TEXTS
import json


def get_texts(text_category):
    with open(PATH_TEXTS, 'r', encoding='utf-8') as f:
        texts = json.load(f)
        return texts['texts'][text_category]

def update_texts(text_category, text):
    with open(PATH_TEXTS, 'r', encoding='utf-8') as f:
        texts = json.load(f)
        texts['texts'].pop(text_category)
        texts['texts'][text_category] = text
    with open(PATH_TEXTS, 'w', encoding='utf-8') as f:
        json.dump(texts,  f,ensure_ascii=False, indent=4)
