import requests
from thread_parser import ThreadParser


class Bot:
    def __init__(self, web_provider, rules, settings):
        self._web_provider = web_provider
        self._settings = settings
        self._rules = rules
        self._posts = {}

    def update(self):
        thread_url = self._settings['thread']
        page_html = self._web_provider.get(thread_url)
        posts = _parse_thread(page_html)
        self.update_posts(posts)

    def update_posts(self, posts):
        for post in posts:
            if post.id not in self._posts:
                if self.is_post_allowed(post):
                    self._posts[post.id] = post
                else:
                    self.delete_post(post)

    def is_post_allowed(self, post):
        if post.trip in self._rules['mods']:
            return True
        if post.trip in self._rules['whitelist']:
            return True
        if post.id <= self._rules['last_post']:
            return True
        return False

    def delete_post(self, post):
        self._web_provider.delete_post(post)


def _parse_thread(html):
    parser = ThreadParser()
    parser.feed(html)
    return parser.posts
