import sys

RUNNING_MICROPYTHON = sys.implementation.name == 'micropython'

if not RUNNING_MICROPYTHON:
    import traceback


def print_traceback(e):
    if RUNNING_MICROPYTHON:
        sys.print_exception(e)
    else:
        traceback.print_exc()


class ExpectedException(Exception):
    pass


class InvalidDataException(ExpectedException):
    pass


class NoReadableDataException(ExpectedException):
    pass


class ConnectionClosedDownException(ExpectedException):
    pass


class AcknowledgementException(ExpectedException):
    pass


class CommunicationException(ExpectedException):
    pass


class AssignmentException(ExpectedException):
    pass
