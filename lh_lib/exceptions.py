

class InvalidDataException(Exception):
    pass


class NoReadableDataException(Exception):
    pass


class ConnectionClosedDownException(Exception):
    pass


class ProcessorSetupException(Exception):
    pass


class AcknowledgementException(Exception):
    pass


class CommunicationException(Exception):
    pass
