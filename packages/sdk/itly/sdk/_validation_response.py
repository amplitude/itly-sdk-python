class ValidationResponse(object):
    def __init__(self, valid, plugin_id, message):
        # type: (bool, str, str) -> None
        self.valid = valid  # type: bool
        self.plugin_id = plugin_id  # type: str
        self.message = message  # type: str

    @staticmethod
    def ok():
        # type: () -> ValidationResponse
        return ValidationResponse(valid=True, plugin_id='', message='')

    @staticmethod
    def error(plugin_id, message):
        # type: (str, str) -> ValidationResponse
        return ValidationResponse(valid=False, plugin_id=plugin_id, message=message)
