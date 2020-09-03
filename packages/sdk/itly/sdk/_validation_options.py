class ValidationOptions(object):
    def __init__(self, disabled=False, track_invalid=False, error_on_invalid=False):
        # type: (bool, bool, bool) -> None
        self.disabled = disabled  # type: bool
        self.track_invalid = track_invalid  # type: bool
        self.error_on_invalid = error_on_invalid  # type: bool
