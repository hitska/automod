import requests
import json
import re

from os.path import dirname, abspath
from time import sleep


script_dir = dirname(abspath(__file__))
settings_filename = f"{script_dir}/settings.json"
rules_filename = f"{script_dir}/rules.json"


class Post:
    def __init__(self, id='', name='', trip='', text=''):
        self.id = id
        self.name = name
        self.trip = trip
        self.text = text


def load_settings():
    with open(settings_filename, encoding='utf-8') as file:
        source = file.read()
        return json.loads(source)


def delete_post(post_id, settings):
    data = {
        'board': 'rf',
        f'delete_{post_id}': 'on',
        'filenum': '0',
        'password': settings['password'],
        'delete': 'Удалить',
        'reason': ''
    }

    # response = requests.post(...)
    # if not response: ... (залогировать?)
    requests.post(settings['post_addr'], data=data)


def parse_thread(html):
    post_pattern = r'<\s*div\s+class\s*=\s*"post\s+reply"\s*id\s*=\s*"reply_(.*?)"\s*>(.*?)<\s*\/\s*div\s*>\s*<\s*br\s*\/\s*>'
    posts = []

    matches = re.findall(post_pattern, html)
    for match in matches:
        post = Post(match[0])

        body_pattern = r'<\s*div\s+class\s*=\s*"body"\s*>(.*?)<\s*\/\s*div\s*>'
        body = re.search(body_pattern, match[1])
        if body:
            post.text = body.group(1)

        name_pattern = r'<\s*span\s+class\s*=\s*"name"\s*>(.*?)<\s*\/\s*span\s*>'
        name = re.search(name_pattern, match[1])
        if name:
            post.name = name.group(1)

        trip_pattern = r'<\s*span\s+class\s*=\s*"trip"\s*>(.*?)<\s*\/\s*span\s*>'
        trip = re.search(trip_pattern, match[1])
        if trip:
            post.trip = trip.group(1)

        posts.append(post)

    return posts


class Bot:
    def __init__(self, rules_file_name, settings):
        self.settings = settings
        self.posts = {}

        with open(rules_file_name, encoding='utf-8') as file:
            source = file.read()
            self.rules = json.loads(source)

    def update_posts(self, posts):
        for post in posts:
            if post.id not in self.posts:
                if self.is_post_allowed(post):
                    self.posts[post.id] = post
                else:
                    self.delete_post(post)

                #self.rules['last_post'] ...
                # На 1 запуск, нет поддержки перезапуска
                # Нет поддержки команд
                # Оптимизация: не перебирать посты меньше определённого номера

    def is_post_allowed(self, post):
        if post.trip in self.rules['mods']:
            return True
        if post.trip in self.rules['whitelist']:
            return True
        return False

    def delete_post(self, post):
        delete_post(post.id, self.settings)


def main():
    settings = load_settings()
    bot = Bot(rules_filename, settings)

    while True:
        try:
            response = requests.get(settings['thread'])
            if response:
                posts = parse_thread(response.content.decode("utf-8"))
                bot.update_posts(posts)
        except:
            pass

        sleep(settings['timeout'])

main()
