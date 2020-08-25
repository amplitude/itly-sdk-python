class ValidationResponse(object):
    def __init__(self, valid, plugin_id, message):
        # type: (bool, str, str) -> None
        self.valid = valid  # type: bool
        self.plugin_id = plugin_id  # type: str
        self.message = message  # type: str
