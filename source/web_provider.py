import logging
import subprocess
import multiprocessing
import docker

from paths import paths
from typing import List
from post import Post
from named_pipe import NamedPipe


class WebProvider:
    """
    Делегирует запросы в докер-образ.
    """
    def __init__(self, settings):
        self._logger = logging.getLogger()
        self._client = docker.from_env()

        self._image_tag = settings['docker-image-tag']
        self._password = settings['password']
        self._command_timeout = 20 # secs

        self._build_image()
        self._remove_old_containers()
        self._create_container()
        self._check_container_is_ok()

    def _build_image(self):
        """
        Пересобираем образ контейнера.
        """
        self._notice(f'Rebuilding docker image "{self._image_tag}"...')

        dockerfile_dir = str(paths.dirname_docker_image)
        self._client.images.build(path=dockerfile_dir, tag=self._image_tag)

        self._logger.info('The image is rebuilt')

    def _remove_old_containers(self):
        """
        Останавливает и удаляет контейнеры от предыдущих запусков, если это требуется.
        """
        for container in self._client.containers.list():
            container_is_ours = False
            for tag in container.image.tags:
                if self._image_tag in tag:
                    container_is_ours = True
                    break

            if not container_is_ours:
                continue

            try:
                self._logger.info(f'Trying to remove container {container.name}...')
                try:
                    container.kill()
                    self._logger.info('Old container was stopped')
                except docker.errors.APIError:
                    self._logger.info('Old container is already stopped')
                container.remove()
                self._logger.info('Old container was removed')
            except docker.errors.NotFound:
                self._logger.info("Old container wasn't found")

    def _create_container(self):
        """
        Создаёт и запускает контейнер.
        """
        container_pipe_in = "/tmp/in_pipe"
        container_pipe_out = "/tmp/out_pipe"
        host_pipe_in = "/tmp/in_pipe_1"
        host_pipe_out = "/tmp/out_pipe_1"

        self._logger.info(f'Creating pipes...')
        self._vm1_pipe_response = NamedPipe(host_pipe_in)
        self._vm1_pipe_request = NamedPipe(host_pipe_out)

        self._logger.info(f'Creating container from "{self._image_tag}"...')
        self._container = self._client.containers.run(
            image=self._image_tag,
            privileged=True,
            detach=True,
            volumes={
                self._vm1_pipe_request.name: {
                    'bind': container_pipe_in,
                    'mode': 'rw'
                },
                self._vm1_pipe_response.name: {
                    'bind': container_pipe_out,
                    'mode': 'rw'
                }
            }
        )

        self._logger.info('The container is created')

    def _check_container_is_ok(self):
        """
        Отсылает команду проверки статуса, проверяет результат.
        """
        result = self._execute_command('STATUS')
        if result != 'OK':
            raise Exception(f'Container STATUS check failed: "{result}"')

    def _notice(self, message):
        print(message)
        self._logger.info(message)

    def _execute_command(self, command):
        """
        Пытается выполнить команду до наступления таймаута, возвращает результат.
        """
        def implementation(cmd, resp_q):
            self._logger.debug(f'Executing command: "{cmd}"')
            self._vm1_pipe_request.write(cmd)
            self._logger.debug('Command sent...')

            response = self._vm1_pipe_response.read()
            self._logger.debug(f'Received response: "{response}"')
            resp_q.put(response)

        queue = multiprocessing.Queue()
        proc = multiprocessing.Process(target=implementation, args=(command, queue))
        proc.start()
        proc.join(self._command_timeout)

        if proc.is_alive():
            proc.kill()
            proc.join()
            raise Exception(f'Command execution timeout [{self._command_timeout}s] is reached for: "{command}"')

        response = queue.get()
        return response

    def get(self, url) -> str:
        result = self._execute_command(f'GET {url}')
        return 'TODO'
        # TODO
        pass

    def delete_posts(self, posts: List[Post]):
        if not posts:
            return

        cmd = f'DELETE {self._password}'
        for post in posts:
            self._logger.debug(f'Trying to delete post: {post}...')
            cmd = cmd + ' ' + post.id

        result = self._execute_command(cmd)
        # TODO
        pass
