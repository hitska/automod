import requests


class WebProvider:
    def get(self, url):
        response = requests.get(url)
        if not response:
            raise Exception(f"Couldn't load page: {response.status_code}")

        return response.content.decode("utf-8")
