import bot_policy

from web_provider import WebProvider
from json_file import JsonFile
from thread_parser import ThreadParser


class Bot:
    def __init__(self, web_provider: WebProvider, settings: JsonFile):
        self._web_provider = web_provider
        self._settings = settings
        self._posts = {}
        self._policy = bot_policy.get_policy(settings['bot_policy'])

    def update(self):
        thread_url = self._settings['thread']
        page_html = self._web_provider.get(thread_url)
        posts = _parse_thread(page_html)
        self.update_posts(posts)

    def update_posts(self, posts):
        posts_to_remove = []
        for post in posts:
            if post.id not in self._posts:
                if self.is_post_allowed(post):
                    self._posts[post.id] = post
                else:
                    posts_to_remove.append(post)

        self._web_provider.delete_posts(posts_to_remove)

    def is_post_allowed(self, post):
        return self._policy.is_post_allowed(post, self._settings)


def _parse_thread(html):
    parser = ThreadParser()
    parser.feed(html)
    return parser.posts
