from typing import Optional

from itly.sdk import Plugin, PluginOptions, Event, ValidationResponse, Properties


class CustomPlugin(Plugin):
    def id(self):
        # type: () -> str
        return 'custom'

    def load(self, options):
        # type: (PluginOptions) -> None
        pass

    def alias(self, user_id, previous_id):
        # type: (str, str) -> None
        pass

    def identify(self, user_id, properties):
        # type: (str, Optional[Properties]) -> None
        pass

    def group(self, user_id, group_id, properties):
        # type: (str, str, Optional[Properties]) -> None
        pass

    def page(self, user_id, category, name, properties):
        # type: (str, Optional[str], Optional[str], Optional[Properties]) -> None
        pass

    def track(self, user_id, event):
        # type: (str, Event) -> None
        pass

    def flush(self):
        # type: () -> None
        pass

    def shutdown(self):
        # type: () -> None
        pass

    # Validation methods

    def validate(self, event):
        # type: (Event) -> ValidationResponse
        return self._create_valid_response()

    def on_validation_error(self, validation, event):
        # type: (ValidationResponse, Event) -> None
        pass
