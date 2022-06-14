from traceback import format_tb
from sys import exc_info
from os.path import dirname, abspath
from time import sleep

from bot import Bot
from json_file import JsonFile
from web_provider import WebProvider

script_dir = dirname(abspath(__file__))
settings_filename = f"{script_dir}/settings.json"
rules_filename = f"{script_dir}/rules.json"

def main():
    web_provider = WebProvider()
    settings = JsonFile(settings_filename)
    rules = JsonFile(rules_filename)
    bot = Bot(web_provider, rules, settings)

    print("Working...")

    while True:
        try:
            bot.update()

        except Exception:
            print('--------------------------------')
            exc_type, value, tb = exc_info()
            print(f"Exception raised: {exc_type.__name__}, message: {value}")
            print('-- Stack trace: ----------------')
            for line in format_tb(tb):
                print(line)
            print('--------------------------------')

        sleep(settings['timeout'])


main()
