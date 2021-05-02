from lh_lib.communication import Client


def run():
    # client = Client('192.168.2.200', 8090)
    client = Client('192.168.2.177', 8090)
    # client = Client('127.0.0.1', 8090)

    client.request_data('dht11', 100)

    while True:
        data = client.receive_data()
        if data:
            print("len: {} | {}".format(len(data), data), flush=True)


if __name__ == '__main__':
    run()
