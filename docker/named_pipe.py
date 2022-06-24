import os


class NamedPipe:
    def __init__(self, name):
        self.name = name
        self._create_named_pipe(name)

    def read(self):
        command = ''

        with open(self.name, "r") as fifo:
            while True:
                data = fifo.read()
                if len(data) != 0:
                    command = command + data
                else:
                    break

        return command

    def write(self, string):
        pipe = open(self.name, "w")
        pipe.write(string)
        pipe.flush()
        pipe.close()

    @staticmethod
    def _create_named_pipe(name):
        try:
            os.stat(name)
            pipe_exists = True
        except OSError:
            pipe_exists = False

        if not pipe_exists:
            os.mkfifo(name, mode=0o777)
