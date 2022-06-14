import requests
import logging

from post import Post
from json_file import JsonFile


class WebProvider:
    def __init__(self):
        self._logger = logging.getLogger()

    def get(self, url):
        self._logger.info(f'Trying to load the page: {url}...')

        response = requests.get(url)
        if not response:
            raise Exception(f"Couldn't load page: {response.status_code}")

        self._logger.info(f'The page is successfully loaded')
        return response.content.decode("utf-8")

    def delete_post(self, post: Post, settings: JsonFile):
        self._logger.info(f'Trying to delete post: {post}...')

        data = {
            'board': 'rf',
            f'delete_{post.id}': 'on',
            'filenum': '0',
            'password': settings['password'],
            'delete': 'Удалить',
            'reason': ''
        }

        response = requests.post(settings['post_addr'], data=data)
        if not response:
            raise Exception(f"Couldn't delete post: {response.status_code}")
        self._logger.info('The post is successfully deleted')
