import requests


class Bot:
    def __init__(self, rules, settings):
        self._settings = settings
        self._rules = rules
        self._posts = {}

    def update_posts(self, posts):
        for post in posts:
            if post.id not in self._posts:
                if self.is_post_allowed(post):
                    self._posts[post.id] = post
                else:
                    print("Trying to delete post: ", post)
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
        delete_post(post.id, self._settings)


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
