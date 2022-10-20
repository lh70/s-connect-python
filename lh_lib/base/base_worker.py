"""
Minimal worker implementation. Needs only the base module. Allows remote filesystem manipulation.
"""
import time

from lh_lib.base.logging import log
from lh_lib.base.network_stack.server import Server
from lh_lib.base.remote_filesystem import RemoteFilesystemHandler
from lh_lib.base.exceptions import print_traceback, CommunicationException, ConnectionClosedDownException, ExpectedException, InvalidDataException, NoReadableDataException
from lh_lib.base.constants import RUNNING_MICROPYTHON


class Worker:

    def __init__(self, port):
        self._server = Server(port)

        self.remote_filesystem_handler = RemoteFilesystemHandler()

        self.general_connections = []

    def remove_general_connection(self, conn, reason):
        conn.close()
        self.general_connections.remove(conn)
        log('removing general connection: {} | reason: {} | num general connections: {}', conn.address, reason, len(self.general_connections))

    def update(self):
        # accept any new connection into the pool
        conn = self._server.accept()
        while conn:
            self.general_connections.append(conn)
            log('new general connection: {} | num general connections: {}', conn.address, len(self.general_connections))
            conn = self._server.accept()

        # update general connections and check for control messages
        self.update_general_connections()

    def update_general_connections(self):
        for conn in self.general_connections[:]:  # copy used, so the list may be manipulated
            try:
                obj = conn.recv()
            except NoReadableDataException:
                pass
            except ConnectionClosedDownException as e:
                self.remove_general_connection(conn, f'remote closed connection: {e}')
            except InvalidDataException as e:
                self.remove_general_connection(conn, f'received invalid data: {e}')
            else:
                if isinstance(obj, dict):
                    self.handle_control_message(obj, conn)
                else:
                    self.remove_general_connection(conn, 'error: received data message on general connection')

    def handle_control_message(self, d, conn):
        result = None

        try:
            message_type = d['type']
            message_content = d['content']

            if message_type == 'remote_filesystem':
                result = self.remote_filesystem_handler.handle_control_message(message_content)
            elif message_type == 'reboot':
                if RUNNING_MICROPYTHON:
                    conn.send_acknowledgement()
                    log('reboot requested. rebooting...')
                    time.sleep(1)
                    import machine
                    machine.reset()
                else:
                    raise CommunicationException('reboot is only allowed on micropython')
            else:
                raise Exception('invalid control message kind')
        except ExpectedException as e:
            self.remove_general_connection(conn, f'error during processing control-message: {type(e)} {e}')
        except Exception as e:
            self.remove_general_connection(conn, f'unexpected error during processing control-message: {type(e)} {e}')
            print_traceback(e)
        else:
            try:
                if result is None:
                    conn.send_acknowledgement()
                else:
                    conn.send(result.serializable())
            except ConnectionClosedDownException as e:
                self.remove_general_connection(conn, f'remote unexpectedly closed down connection during sending acknowledgement: {type(e)} {e}')
            except Exception as e:
                self.remove_general_connection(conn, f'internal error on sending response: {type(e)} {e}')
