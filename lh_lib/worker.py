import time

from lh_lib.base.logging import log
from lh_lib.assignment import Assignment
from lh_lib.base.exceptions import NoReadableDataException, ConnectionClosedDownException, InvalidDataException, AssignmentException, ExpectedException, print_traceback, CommunicationException
from lh_lib.base.network_stack.server import Server
from lh_lib.base.remote_filesystem import RemoteFilesystemHandler
from lh_lib.base.constants import RUNNING_MICROPYTHON


class Worker:

    def __init__(self, port, sensor_manager):
        self._server = Server(port)
        self.sensor_manager = sensor_manager

        self.general_connections = []
        self.pipe_connections = {}

        self.assignments = {}

        self.remote_filesystem_handler = RemoteFilesystemHandler()

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

        # update sensor values
        self.sensor_manager.update()

        # call/update assignment handlers
        # slicing does not work on dictionaries, but lists do
        # so we use list to get a distinct copy, so we can operate on the dictionary while iterating over it
        for assignment_id in list(self.assignments):
            try:
                self.assignments[assignment_id].update()
            except AssignmentException as e:
                self.assignments[assignment_id].cleanup()
                del self.assignments[assignment_id]
                log('removing assignment {} | reason: {} | num assignments: {}', assignment_id, e, len(self.assignments))

    def update_general_connections(self):
        for conn in self.general_connections[:]:  # copy used, so the list may be manipulated
            try:
                obj = conn.recv()
            except NoReadableDataException:
                pass
            except ConnectionClosedDownException as e:
                self.remove_general_connection(conn, 'remote closed connection: {}'.format(e))
            except InvalidDataException as e:
                self.remove_general_connection(conn, 'received invalid data: {}'.format(e))
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

            if message_type == 'add_assignment':
                assignment_id = message_content['id']

                if assignment_id in self.assignments:
                    raise AssignmentException('assignment-id {} is already in use'.format(assignment_id))

                self.assignments[assignment_id] = Assignment(message_content, self.sensor_manager)
                log('creating assignment {} | num assignments: {}', assignment_id, len(self.assignments))
            elif message_type == 'remove_assignment':
                assignment_id = message_content['id']

                if assignment_id in self.assignments:
                    self.assignments[assignment_id].cleanup()
                    del self.assignments[assignment_id]
                    log('removing assignment {} | reason: got request | num assignments: {}', assignment_id, len(self.assignments))
                else:
                    log('ignoring assignment {} removal request | reason: no such assignment | num assignments: {}', assignment_id, len(self.assignments))
            elif message_type == 'pipeline_request':
                assignment_id = message_content['assignment_id']
                pipe_id = message_content['pipe_id']
                time_frame_ms = message_content['time_frame_ms']
                heartbeat_ms = message_content['heartbeat_ms']

                if assignment_id in self.assignments:
                    self.assignments[assignment_id].assign_output_pipeline(conn, pipe_id, time_frame_ms, heartbeat_ms)
                    self.general_connections.remove(conn)
                    log('promoting general connection {} to output pipeline connection on assignment {} with pipe-id {} | num general connections: {}', conn.address, assignment_id, pipe_id, len(self.general_connections))
                else:
                    raise AssignmentException('assignment-id {} used for pipeline-id {} does not exist'.format(assignment_id, pipe_id))
            elif message_type == 'remote_filesystem':
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
            self.remove_general_connection(conn, 'error during processing control-message: {} {}'.format(type(e), e))
        except Exception as e:
            self.remove_general_connection(conn, 'unexpected error during processing control-message: {} {}'.format(type(e), e))
            print_traceback(e)
        else:
            try:
                if result is None:
                    conn.send_acknowledgement()
                else:
                    conn.send(result.serializable())
            except ConnectionClosedDownException as e:
                self.remove_general_connection(conn, 'remote unexpectedly closed down connection during sending acknowledgement: {} {}'.format(type(e), e))
            except Exception as e:
                self.remove_general_connection(conn, 'internal error on sending response: {} {}'.format(type(e), e))
