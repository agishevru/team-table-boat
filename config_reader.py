""" Модуль загрузки конфигурации """
import os
from environs import Env
from dataclasses import dataclass

@dataclass
class Settings:
    """ Основной класс с настройками """
    bot_token: str
    google_credentials_file_path: str
    db_url: str
    fsm_memory_redis: bool


    # db_config: dict

def get_settings() -> Settings:
    """ Вытаскивает данные из .env и заполняет датакласс Settings """
    env = Env()
    env.read_env()

    return Settings(bot_token=env.str('BOT_TOKEN'),
                    google_credentials_file_path=env.str('GOOGLE_CREDENTIALS_FILE_PATH'),
                    db_url=env.str('DB_URL'),
                    fsm_memory_redis=env.bool('FSM_MEMORY_REDIS')
                    )

# инициализируем класс с настройками
config = get_settings()

# tok = os.getenv("BOT_TOKEN")
# print(tok)





