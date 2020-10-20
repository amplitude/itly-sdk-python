import json
from typing import Dict, Optional

import jsonschema

from itly_sdk import Plugin, Event, ValidationResponse, PluginLoadOptions


class SchemaValidatorPlugin(Plugin):
    def __init__(self, schemas: Dict[str, str]):
        self._schemas: Dict[str, str] = schemas
        self._validators: Dict[str, jsonschema.Draft7Validator] = {}

    def id(self) -> str:
        return 'schema-validator'

    def load(self, options: PluginLoadOptions) -> None:
        for schema_key, raw_schema in self._schemas.items():
            schema = json.loads(raw_schema)
            jsonschema.Draft7Validator.check_schema(schema)
            self._validators[schema_key] = jsonschema.Draft7Validator(schema)

    def validate(self, event: Event) -> Optional[ValidationResponse]:
        schema_key = event.name
        # Check that we have a schema for this event
        if schema_key not in self._schemas:
            raise ValueError(f"Event '{event.name}' not found in tracking plan.")

        event_properties = event.properties.to_json() if event.properties is not None else {}
        try:
            self._validators[schema_key].validate(instance=event_properties)
        except jsonschema.ValidationError as ex:
            return self._create_invalid_response(
                message=f"Passed in {event.name} properties did not validate against your tracking plan. {ex}"
            )
        except Exception as ex:
            return self._create_invalid_response(
                message=f"Passed in {event.name} properties did not validate against your tracking plan."
                        f"An unknown error occurred during validation. {ex}"
            )

        return None
