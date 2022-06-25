import datetime

from imageboard import Imageboard
from named_pipe import NamedPipe

tmp_file = "/tmp/files/exchange.bin"
pipe_in_path = "/tmp/in_pipe"
pipe_out_path = "/tmp/out_pipe"


def server_main():
    print('Creating pipes...')
    pipe_in = NamedPipe(pipe_in_path)
    pipe_out = NamedPipe(pipe_out_path)

    print('Starting browser...')
    aib = Imageboard()

    print('Working...')
    # TODO: обработка исключений
    # TODO: сообщение о проблемах вызывающей стороне
    while True:
        request = pipe_in.read()
        print(datetime.datetime.now(), 'Request received:', request)
        response = execute_command(aib, request)
        pipe_out.write(response)
        print(datetime.datetime.now(), 'Done.')


def execute_command(aib, request):
    args = request.split()
    command = args[0]

    if command == 'STATUS':
        return 'OK'
    elif command == 'GET':
        url = args[1]
        html = aib.get(url)

        print(datetime.datetime.now(), 'Writing HTML...')
        with open(tmp_file, "w") as file:
            file.write(html)
        print(datetime.datetime.now(), 'Written.')
        return 'DONE'
    elif command == 'DELETE':
        password = args[1]
        post_nums = args[2:]
        print("DEL:", post_nums)
        aib.delete_posts(post_nums, password)
        return 'DONE'
    else:
        raise Exception(f'Unknown command: {command}')


if __name__ == "__main__":
    server_main()
