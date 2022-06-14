import requests
import json
from post import Post

from os.path import dirname, abspath
from time import sleep

from html.parser import HTMLParser


script_dir = dirname(abspath(__file__))
settings_filename = f"{script_dir}/settings.json"
rules_filename = f"{script_dir}/rules.json"


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

    response = requests.post(settings['post_addr'], data=data)
    if not response:
        print("Couldn't delete post:", response.status_code)


def contain_values(attrs, req_attr_key, req_attr_values):
    if not req_attr_key in attrs:
        return False

    values = attrs[req_attr_key].split(' ')

    for required_value in req_attr_values:
        if required_value not in values:
            return False

    return True


class ThreadParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.posts = []
        self.deepness = 0
        self.post = None
        self.post_deepness = -1
        self.reading_attr = None
        self.counting_tags = ['div', 'span']

    def handle_starttag(self, tag, attrs):
        if tag in self.counting_tags:
            self.deepness = self.deepness + 1

        attrs = dict(attrs)

        if not self.post:
            if tag == 'div':
                if contain_values(attrs, 'class', ['post', 'reply']):
                    self.post = Post()
                    self.post_deepness = self.deepness
                    self.posts.append(self.post)
        else:
            # Мы внутри поста
            if tag == 'a':
                if 'id' in attrs and contain_values(attrs, 'class', ['post_anchor']):
                    self.post.id = int(attrs['id'])
            if tag == 'span':
                if contain_values(attrs, 'class', ['name']):
                    self.reading_attr = 'name'
                if contain_values(attrs, 'class', ['trip']):
                    self.reading_attr = 'trip'

    def handle_endtag(self, tag):
        if tag in self.counting_tags:
            if self.post and self.deepness == self.post_deepness:
                self.post = None
                self.post_deepness = -1

            self.deepness = self.deepness - 1
            self.reading_attr = None

    def handle_data(self, data):
        if self.reading_attr == 'name':
            self.post.name = data
        if self.reading_attr == 'trip':
            self.post.trip = data


def parse_thread(html):
    parser = ThreadParser()
    parser.feed(html)
    return parser.posts


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
                    print("Trying to delete post: ", post)
                    self.delete_post(post)

    def is_post_allowed(self, post):
        if post.trip in self.rules['mods']:
            return True
        if post.trip in self.rules['whitelist']:
            return True
        if post.id <= self.rules['last_post']:
            return True
        return False

    def delete_post(self, post):
        delete_post(post.id, self.settings)


def main():
    settings = load_settings()
    bot = Bot(rules_filename, settings)

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
