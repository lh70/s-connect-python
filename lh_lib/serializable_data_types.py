
class Message:

    def serializable(self):
        raise Exception('Bare Message class is not serializable')


class ControlMessageResponseResult(Message):

    def __init__(self, json_serializable_data):
        self.data = json_serializable_data

    def serializable(self):
        return {'type': 'result', 'data': self.data}


class ControlMessageResponseError(Message):

    def __init__(self, exception):
        self.exception = exception

    def serializable(self):
        return {'type': 'error', 'error_class': type(self.exception).__name__, 'message': str(self.exception)}


class ControlMessageReboot(Message):

    def serializable(self):
        return {'type': 'reboot', 'content': None}


class ControlMessageFilesystem(Message):
    COMMAND_WRITE_FILE = 'write_file'
    COMMAND_READ_FILE = 'read_file'
    COMMAND_REMOVE_FILE = 'remove_file'
    COMMAND_STAT = 'path_stat'
    COMMAND_LIST_DIRECTORY = 'list_directory'
    COMMAND_MAKE_DIRECTORY = 'make_directory'
    COMMAND_REMOVE_DIRECTORY = 'remove_directory'

    ALL_COMMANDS = (COMMAND_WRITE_FILE, COMMAND_READ_FILE, COMMAND_REMOVE_FILE, COMMAND_STAT, COMMAND_LIST_DIRECTORY, COMMAND_MAKE_DIRECTORY, COMMAND_REMOVE_DIRECTORY)

    def __init__(self, command, path, content=None, mtime=None):
        if command not in ControlMessageFilesystem.ALL_COMMANDS:
            raise Exception(f'unknown filesystem command: {command}')

        if command == ControlMessageFilesystem.COMMAND_WRITE_FILE:
            if content is None or mtime is None:
                raise Exception('content to write into file and new modified time must be set')
        elif content is not None or mtime is not None:
            raise Exception('content and mtime may only be set when writing to a file')

        self.command = command
        self.path = path
        self.content = content
        self.mtime = mtime

    def serializable(self):
        serializable = {'type': 'remote_filesystem', 'content': {'command': self.command, 'path': self.path}}
        if self.command == ControlMessageFilesystem.COMMAND_WRITE_FILE:
            serializable['content']['content'] = self.content
            serializable['content']['mtime'] = self.mtime
        return serializable
