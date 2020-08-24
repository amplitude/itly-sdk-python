class ValidationOptions(object):
    def __init__(self, disabled, track_invalid, error_on_invalid):
        # type: (bool, bool, bool) -> None
        self.disabled = disabled  # type: bool
        self.track_invalid = track_invalid  # type: bool
        self.error_on_invalid = error_on_invalid  # type: bool
