import requests

from os.path import dirname, abspath
from time import sleep

from thread_parser import ThreadParser
from bot import Bot
from json_file import JsonFile

script_dir = dirname(abspath(__file__))
settings_filename = f"{script_dir}/settings.json"
rules_filename = f"{script_dir}/rules.json"


def parse_thread(html):
    parser = ThreadParser()
    parser.feed(html)
    return parser.posts


def main():
    settings = JsonFile(settings_filename)
    rules = JsonFile(rules_filename)
    bot = Bot(rules, settings)

    print("Working...")

    while True:
        try:
            response = requests.get(settings['thread'])
            if response:
                posts = parse_thread(response.content.decode("utf-8"))
                bot.update_posts(posts)
            else:
                print("Couldn't load page:", response.status_code)
        except Exception as e:
            print(getattr(e, 'message', repr(e)))

        sleep(settings['timeout'])


main()
