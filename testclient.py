from communication import Client


def run():
    client = Client('127.0.0.1', 8090)

    client.request_data('dummy', 10)

    while True:
        client.receive_and_print_data()


if __name__ == '__main__':
    run()
