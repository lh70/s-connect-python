import lh_lib.network

from lh_lib.logging import log
from v2.assignments.sensor_read import ReadRawSensorData
from v2.assignments.printout import SensorPrintout
from v2.assignments.pass_through import PassThrough
from lh_lib.assignment import GeneralAssignment
from lh_lib.exceptions import NoReadableDataException, ConnectionClosedDownException, InvalidDataException, AssignmentException

PORT = 8090


class Worker:

    def __init__(self, port, sensor_manager):
        self._server = lh_lib.network.Server(port)
        self.sensor_manager = sensor_manager

        self.general_connections = []
        self.pipe_connections = {}

        self.assignments = {}

    def remove_general_connection(self, conn, reason):
        conn.socket.close()
        self.general_connections.remove(conn)
        log("removing general connection: {} | reason: {} | num general connections: {}", conn.address, reason, len(self.general_connections))

    def update(self):
        # accept any new connection into the pool
        conn = self._server.accept()
        while conn:
            self.general_connections.append(conn)
            log("new general connection: {} | num general connections: {}", conn.address, len(self.general_connections))
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
                log("removing assignment {} | reason: {} | num assignments: {}", assignment_id, e, len(self.assignments))

    def update_general_connections(self):
        for conn in self.general_connections[:]:  # copy used, so the list may be manipulated
            try:
                obj = conn.recv()
            except NoReadableDataException:
                pass
            except ConnectionClosedDownException as e:
                self.remove_general_connection(conn, "remote closed connection: {}".format(e))
            except InvalidDataException as e:
                self.remove_general_connection(conn, "received invalid data: {}".format(e))
            else:
                if isinstance(obj, dict):
                    self.handle_control_message(obj, conn)
                else:
                    self.remove_general_connection(conn, "error: received data message on general connection")

    def handle_control_message(self, d, conn):
        try:
            if 'processing-assignment' in d:
                setup_obj = d['processing-assignment']

                assignment_kind = setup_obj['assignment-kind']
                assignment_id = setup_obj['assignment-id']

                if assignment_id in self.assignments:
                    raise AssignmentException("assignment-id {} is already in use".format(assignment_id))

                if assignment_kind == 'general':
                    self.assignments[assignment_id] = GeneralAssignment(setup_obj, self.sensor_manager)
                elif assignment_kind == 'raw-sensor-data':
                    self.assignments[assignment_id] = ReadRawSensorData(setup_obj, self.sensor_manager)
                elif assignment_kind == 'sensor-printout':
                    self.assignments[assignment_id] = SensorPrintout(setup_obj)
                elif assignment_kind == 'pass-through':
                    self.assignments[assignment_id] = PassThrough(setup_obj)
                else:
                    raise AssignmentException("assignment-kind {} is not supported".format(assignment_kind))
                log("creating assignment {} | num assignments: {}", assignment_id, len(self.assignments))
            elif 'remove-assignment' in d:
                assignment_id = d['remove-assignment']['assignment-id']

                if assignment_id in self.assignments:
                    self.assignments[assignment_id].cleanup()
                    del self.assignments[assignment_id]
                    log("removing assignment {} | reason: got request | num assignments: {}", assignment_id, len(self.assignments))
                else:
                    log("ignoring assignment {} removal request | reason: no such assignment | num assignments: {}", assignment_id, len(self.assignments))
            elif 'pipeline-request' in d:
                assignment_id = d['pipeline-request']['assignment-id']
                pipe_id = d['pipeline-request']['pipe-id']
                time_frame = d['pipeline-request']['time-frame']
                values_per_time_frame = d['pipeline-request']['values-per-time-frame']

                if assignment_id in self.assignments:
                    if pipe_id in self.assignments[assignment_id].possible_output_pipelines:
                        self.assignments[assignment_id].assign_output_pipeline(conn, pipe_id, time_frame, values_per_time_frame)
                        self.general_connections.remove(conn)
                        log("promoting general connection {} to output pipeline connection on assignment {} with pipe-id {} | num general connections: {}", conn.address, assignment_id, pipe_id, len(self.general_connections))
                    else:
                        raise AssignmentException("pipe-id {} does not exists in outputs of assignment {}".format(pipe_id, assignment_id))
                else:
                    raise AssignmentException("assignments {} used for pipe-id {} does not exist".format(assignment_id, pipe_id))
            else:
                raise Exception("invalid control-message kind")
        except Exception as e:
            self.remove_general_connection(conn, "error during processing control-message: {}".format(e))
        else:
            conn.send_acknowledgement()
