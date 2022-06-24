import logging

from sys import exc_info
from time import sleep

from bot import Bot
from json_file import JsonFile
from web_provider import WebProvider
from paths import paths


def init_logger():
    logger = logging.getLogger()
    formatter = logging.Formatter("#### %(asctime)s — %(name)s — %(levelname)s — %(message)s ####")
    handler = logging.FileHandler(paths.filename_log, mode='w')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def main():
    logger = init_logger()

    settings = JsonFile(paths.filename_settings)
    web_provider = WebProvider(settings)
    bot = Bot(web_provider, settings)

    print("Working...")

    while True:
        try:
            bot.update()

        except Exception as exc:
            logger.exception(exc)

            exc_type, value, _ = exc_info()
            print(f'{exc_type.__name__} raised: "{value}"')

        sleep(settings['timeout'])


if __name__ == "__main__":
    main()
