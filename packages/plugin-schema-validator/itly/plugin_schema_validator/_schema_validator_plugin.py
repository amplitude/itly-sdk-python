import json
from typing import Dict, Optional, Callable

import jsonschema

from itly.sdk import Plugin, Event, ValidationResponse, PluginOptions

SYSTEM_EVENTS = ['identify', 'context', 'group', 'page']

ValidationResponseHandler = Callable[[ValidationResponse, Event, Optional[str]], None]


class SchemaValidatorPlugin(Plugin):
    def __init__(self, schemas, validation_error_handler=None):
        # type: (Dict[str, str], Optional[ValidationResponseHandler]) -> None
        self._schemas = schemas  # type: Dict[str, str]
        self._validation_error_handler = validation_error_handler  # type: Optional[ValidationResponseHandler]
        self._validators = {}  # type: Dict[str, jsonschema.Draft7Validator]

    def id(self):
        # type: () -> str
        return 'schema-validator'

    def load(self, options):
        # type: (PluginOptions) -> None
        for schema_key, raw_schema in self._schemas.items():
            schema = json.loads(raw_schema)
            jsonschema.Draft7Validator.check_schema(schema)
            self._validators[schema_key] = jsonschema.Draft7Validator(schema)

    def validate(self, event):
        # type: (Event) -> ValidationResponse
        schema_key = self._get_schema_key(event)
        # Check that we have a schema for this event
        if schema_key not in self._schemas:
            if self._is_system_event(schema_key):
                # pass system events by default
                if self._is_empty_event(event):
                    return ValidationResponse.ok()
                return ValidationResponse.error(
                    plugin_id=self.id(),
                    message="'{0}' schema is empty but properties were found. properties={1}".format(event.name, event.properties)
                )

            return ValidationResponse.error(
                plugin_id=self.id(),
                message="Event {0} not found in tracking plan.".format(event.name)
            )

        if self._is_empty_event(event):
            return ValidationResponse.ok()

        try:
            self._validators[schema_key].validate(instance=event.properties.to_json())
        except jsonschema.ValidationError as ex:
            return ValidationResponse.error(
                plugin_id=self.id(),
                message="Passed in {0} properties did not validate against your tracking plan. {1}".format(event.name, ex)
            )
        except Exception as ex:
            return ValidationResponse.error(
                plugin_id=self.id(),
                message="Passed in {0} properties did not validate against your tracking plan. An unknown error occurred during validation. {1}".format(event.name, ex)
            )

        return ValidationResponse.ok()

    def validation_error(self, validation, event):
        # type: (ValidationResponse, Event) -> None
        if self._validation_error_handler is not None:
            schema_key = self._get_schema_key(event)
            self._validation_error_handler(validation, event, self._schemas.get(schema_key, None))

    @staticmethod
    def _get_schema_key(event):
        # type: (Event) -> str
        return event.name

    @staticmethod
    def _is_system_event(name):
        # type: (str) -> bool
        return name in SYSTEM_EVENTS

    @staticmethod
    def _is_empty_event(event):
        # type: (Event) -> bool
        return event.properties is None or len(event.properties) == 0
