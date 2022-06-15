import logging
from time import sleep
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from post import Post
from json_file import JsonFile


class WebProvider:
    def __init__(self, settings: JsonFile):
        self._settings = settings
        self._logger = logging.getLogger()

        chrome_options = Options()
        # Пытаемся отрубить загрузку картинок
        prefs = { "profile.managed_default_content_settings.images": 2 }
        chrome_options.add_experimental_option("prefs", prefs)
        # А это необходимо чтобы он вообще запустился
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')

        self._browser = webdriver.Chrome(chrome_options=chrome_options)

        # Раз в определённое количество обновлений мы перезагружаем страницу на всякий случай.
        self._page_update_counter = 0
        self._page_update_max_count = 100

    def get(self, url) -> str:
        self._logger.info(f'Trying to load the page: {url}...')

        try:
            if url != self._browser.current_url or self._page_update_counter >= self._page_update_max_count:
                self._page_update_counter = 0
                self._browser.get(url)

                # Отрубаем автообновление. Если элемент не найден - словим исключение.
                auto_update_checkbox = self._browser.find_element(By.ID, "auto_update_status")
                if auto_update_checkbox.is_selected():
                    auto_update_checkbox.click()

                self._logger.info(f'The page is successfully loaded')

            else:
                self._page_update_counter = self._page_update_counter + 1

                updating_str = 'Обновление...'
                update_status = self._browser.find_element(By.ID, "update_secs")
                self._browser.execute_script(f"document.getElementById('update_secs').innerHTML='{updating_str}'")
                update_button = self._browser.find_element(By.ID, "update_thread")
                update_button.click()

                # Ждём пока подсосёт новые посты.
                max_tries = 20
                for i in range(max_tries + 1):
                    sleep(0.5)
                    innerHTML = update_status.get_attribute('innerHTML')
                    if innerHTML != updating_str:
                        self._logger.info(f'The page is successfully updated')
                        break
                    if i == max_tries:
                        self._logger.info(f"Can't update the page, reloading...")
                        self._page_update_counter = self._page_update_max_count

            return self._browser.page_source

        except NoSuchElementException as e:
            # Мы загрузили, но что-то не то.
            # По идее, тут можно обработать ввод каптчи в Cloudflare, если причина именно в нём.
            self._logger.warning(f'Failed page source: "{self._browser.page_source}"')
            raise e

    def delete_posts(self, posts: List[Post]):
        if not posts:
            return

        # Удаляем всех оптом.
        for post in posts:
            self._logger.info(f'Trying to delete post: {post}...')

            post_checkbox = self._browser.find_element(By.ID, f'delete_{post.id}')
            if not post_checkbox.is_selected():
                post_checkbox.click()

        password_txtbox = self._browser.find_element(By.ID, 'password')
        password_txtbox.clear()
        password_txtbox.send_keys(self._settings['password'])

        self._browser.find_element(By.NAME, 'delete').click()

        # Перезагружаем страницу при следующем обновлении, чтобы удалённые посты исчезли из html.
        self._page_update_counter = self._page_update_max_count
        # Дадим скриптам время на удаление.
        # Когда-нибудь, возможно, я перепишу ожидание удаления нормально...
        sleep(0.5)
