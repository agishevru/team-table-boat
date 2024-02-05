# -*- coding: utf-8 -*-
# -----------------------------------------------------
#        Цветное логирование - подсвечены уровни      |
# -----------------------------------------------------

import logging
import colorlog


# Объект логгера
log = logging.getLogger()
log.setLevel(logging.WARNING)

# Форматтеры
formatter_file = logging.Formatter("%(asctime)s-%(levelname)-s  modul:%(module)s  func:%(funcName)s  ln:%(lineno)d| %(message)s")
formatter_console = colorlog.ColoredFormatter(
    fmt="%(log_color)s%(asctime)s-%(levelname)-8s  modul:%(module)s  func:%(funcName)s ln:%(lineno)d| %(message)s",
    datefmt='%d.%m.%y-%H:%M:%S',
    reset=True,
    secondary_log_colors={},
    style='%',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'white', #'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'light_white,bg_red'})

# Обработчик для консольного вывода
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter_console)

# Обработчик для записи в файл
file_handler = logging.FileHandler('bot.log', encoding='UTF-8')  # Замените 'example.log' на путь к вашему файлу логов
file_handler.setFormatter(formatter_file)

# Подключение обработчиков к логгеру
log.addHandler(console_handler)
log.addHandler(file_handler)


# Пример записи логов
if __name__ == '__main__':
    log.debug("Debug message")
    log.info("Info message")
    log.warning("Warning message")
    log.error("Error message")
    log.critical("Critical message")

