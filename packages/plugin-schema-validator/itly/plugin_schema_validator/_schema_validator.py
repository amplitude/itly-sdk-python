import json
from typing import Dict

import jsonschema

from itly.sdk import Plugin, Event, ValidationResponse, PluginLoadOptions


class SchemaValidatorPlugin(Plugin):
    def __init__(self, schemas):
        # type: (Dict[str, str]) -> None
        self._schemas = schemas  # type: Dict[str, str]
        self._validators = {}  # type: Dict[str, jsonschema.Draft7Validator]

    def id(self):
        # type: () -> str
        return 'schema-validator'

    def load(self, options):
        # type: (PluginLoadOptions) -> None
        for schema_key, raw_schema in self._schemas.items():
            schema = json.loads(raw_schema)
            jsonschema.Draft7Validator.check_schema(schema)
            self._validators[schema_key] = jsonschema.Draft7Validator(schema)

    def validate(self, event):
        # type: (Event) -> ValidationResponse
        schema_key = self._get_schema_key(event)
        # Check that we have a schema for this event
        if schema_key not in self._schemas:
            raise ValueError("Event '{0}' not found in tracking plan.".format(event.name))

        event_properties = event.properties.to_json() if event.properties is not None else {}
        try:
            self._validators[schema_key].validate(instance=event_properties)
        except jsonschema.ValidationError as ex:
            return self._create_invalid_response(
                message="Passed in {0} properties did not validate against your tracking plan. {1}".format(event.name, ex)
            )
        except Exception as ex:
            return self._create_invalid_response(
                message="Passed in {0} properties did not validate against your tracking plan. An unknown error occurred during validation. {1}".format(event.name, ex)
            )

        return self._create_valid_response()

    @staticmethod
    def _get_schema_key(event):
        # type: (Event) -> str
        return event.name
