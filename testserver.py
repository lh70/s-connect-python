from communication import Server

from sensors.esp32.dummy import Dummy


def run():
    dummy_sensor = Dummy()

    server = Server(8090, dummy_sensor)

    while True:
        server.update()


if __name__ == '__main__':
    run()
