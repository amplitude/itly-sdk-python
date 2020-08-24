from typing import Optional

from itly.sdk import Plugin, Event, ValidationResponse, Properties, PluginOptions, Logger


class CustomPlugin(Plugin):
    def __init__(self):
        # type: () -> None
        self._logger = Logger.NONE  # type: Logger

    def id(self):
        # type: () -> str
        return 'custom'

    def load(self, options):
        # type: (PluginOptions) -> None
        self._logger = options.logger
        self._logger.info("load() environment='{0}'".format(options.environment.value))

    def alias(self, user_id, previous_id):
        # type: (str, Optional[str]) -> None
        self._logger.info("alias() user_id='{0}' previous_id='{1}'".format(user_id, previous_id))

    def identify(self, user_id, properties):
        # type: (str, Optional[Properties]) -> None
        self._logger.info("identify() user_id='{0}' properties={1}".format(user_id, properties))

    def group(self, user_id, group_id, properties):
        # type: (str, str, Optional[Properties]) -> None
        self._logger.info("group() user_id='{0}' group_id='{1}' properties={2}".format(user_id, group_id, properties))

    def page(self, user_id, category, name, properties):
        # type: (str, Optional[str], Optional[str], Optional[Properties]) -> None
        self._logger.info("page() user_id='{0}' category='{1}' name='{2}' properties={3}".format(user_id, category, name, properties))

    def track(self, user_id, event):
        # type: (str, Event) -> None
        self._logger.info("track() user_id='{0}' event='{1}' properties={2}".format(user_id, event.name, event.properties))

    # Validation methods

    def validate(self, event):
        # type: (Event) -> ValidationResponse
        self._logger.info("validate() event='{0}'".format(event.name))
        return ValidationResponse.ok()

    def validation_error(self, validation, event):
        # type: (ValidationResponse, Event) -> None
        self._logger.info("validation_error() event='{0}' message='{1}'".format(event.name, validation.message))

    def flush(self):
        # type: () -> None
        self._logger.info("flush()")

    def shutdown(self):
        # type: () -> None
        self._logger.info("shutdown()")
