import json
import os


def load_json(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as fh:  # открываем файл на чтение
            data = json.load(fh)
            return data

    except Exception as exception:
        raise exception


def get_processor_settings():
    settings_file_name = 'settings.json'
    settings = load_json(settings_file_name)
    return settings


def get_temp_directory():
    return get_processor_settings()['temp_directory']


settings = get_processor_settings()


