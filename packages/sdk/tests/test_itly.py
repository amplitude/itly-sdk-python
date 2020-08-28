import enum
import unittest
from datetime import datetime
from typing import List, Optional

from itly.sdk import itly, Options, Environment, Event, Properties, Logger, Plugin, PluginOptions, ValidationResponse


class CustomLogger(Logger):
    def __init__(self, log_lines):
        # type: (List[str]) -> None
        self.log_lines = log_lines

    def debug(self, message):
        # type: (str) -> None
        self.log_lines.append(message)

    def info(self, message):
        # type: (str) -> None
        self.log_lines.append(message)

    def warn(self, message):
        # type: (str) -> None
        self.log_lines.append(message)

    def error(self, message):
        # type: (str) -> None
        self.log_lines.append(message)


class CustomPlugin(Plugin):
    def id(self):
        return 'custom'

    def load(self, options):
        # type: (PluginOptions) -> None
        pass

    def alias(self, user_id, previous_id, timestamp=None):
        # type: (str, str, Optional[datetime]) -> None
        pass

    def identify(self, user_id, properties, timestamp=None):
        # type: (str, Optional[Properties], Optional[datetime]) -> None
        pass

    def group(self, user_id, group_id, properties, timestamp=None):
        # type: (str, str, Optional[Properties], Optional[datetime]) -> None
        pass

    def page(self, user_id, category, name, properties, timestamp=None):
        # type: (str, Optional[str], Optional[str], Optional[Properties], Optional[datetime]) -> None
        pass

    def track(self, user_id, event, timestamp=None):
        # type: (str, Event, Optional[datetime]) -> None
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

    def on_validation_error(self, validation, event, timestamp=None):
        # type: (ValidationResponse, Event, Optional[datetime]) -> None
        pass


class TestEnum(enum.Enum):
    Enum1 = "Enum1"
    Enum2 = "Enum2"


class TestOptionalEnum(enum.Enum):
    Value1 = "Value 1"
    Value2 = "Value 2"


class TestItly(unittest.TestCase):
    def test_should_load_and_track_events_to_a_custom_destination_no_validation(self):
        # type: () -> None
        user_id = 'test-user-id'

        log_lines = []  # type: List[str]

        itly.load(Options(
            environment=Environment.PRODUCTION,
            context=Properties(
                requiredString='A required string',
                optionalEnum=TestOptionalEnum.Value1,
            ),
            plugins=[CustomPlugin()],
            logger=CustomLogger(log_lines),
        ))

        itly.identify('user-id', Properties(user_prop=1))
        itly.alias(user_id, 'user-id')
        itly.group(user_id, 'a-group-id', Properties(group_prop='test value'))
        itly.page(user_id, 'page category', 'page name', Properties(page_prop='a page property'))
        itly.track(user_id, Event(name='Event No Properties'))
        itly.track(user_id, Event(name='Event With All Properties', properties=Properties(
            required_string='A required string',
            required_number=2.0,
            required_integer=42,
            required_enum=TestEnum.Enum1,
            required_boolean=False,
            required_const='some-const-value',
            required_array=['required', 'array'],
            optional_string="I'm optional!",
        )))
        itly.flush()
        itly.track(user_id, Event(name='EventMaxIntForTest', properties=Properties(
            int_max_10=20,
        )))
        itly.flush()
        itly.shutdown()

        custom_plugin = itly.get_plugin('custom')
        assert custom_plugin is not None and custom_plugin.id() == 'custom'

        log_text = '\n'.join(log_lines)
        assert log_text == '''[itly-plugin-custom] load()
[itly-plugin-custom] validate(event=context, properties={"requiredString": "A required string", "optionalEnum": "Value 1"})
[itly-plugin-custom] validate(event=identify, properties={"user_prop": 1})
[itly-plugin-custom] identify(user_id=user-id, properties={"user_prop": 1})
[itly-plugin-custom] alias(user_id=test-user-id, previous_id=user-id)
[itly-plugin-custom] validate(event=group, properties={"group_prop": "test value"})
[itly-plugin-custom] group(user_id=test-user-id, group_id=a-group-id, properties={"group_prop": "test value"})
[itly-plugin-custom] validate(event=page, properties={"page_prop": "a page property"})
[itly-plugin-custom] page(user_id=test-user-id, category=page category, name=page name, properties={"page_prop": "a page property"})
[itly-plugin-custom] validate(event=Event No Properties, properties=None)
[itly-plugin-custom] track(user_id=test-user-id, event=Event No Properties, properties={"requiredString": "A required string", "optionalEnum": "Value 1"})
[itly-plugin-custom] validate(event=Event With All Properties, properties={"required_string": "A required string", "required_number": 2.0, "required_integer": 42, "required_enum": "Enum1", "required_boolean": false, "required_const": "some-const-value", "required_array": ["required", "array"], "optional_string": "I'm optional!"})
[itly-plugin-custom] track(user_id=test-user-id, event=Event With All Properties, properties={"requiredString": "A required string", "optionalEnum": "Value 1", "required_string": "A required string", "required_number": 2.0, "required_integer": 42, "required_enum": "Enum1", "required_boolean": false, "required_const": "some-const-value", "required_array": ["required", "array"], "optional_string": "I'm optional!"})
[itly-plugin-custom] flush()
[itly-plugin-custom] validate(event=EventMaxIntForTest, properties={"int_max_10": 20})
[itly-plugin-custom] track(user_id=test-user-id, event=EventMaxIntForTest, properties={"requiredString": "A required string", "optionalEnum": "Value 1", "int_max_10": 20})
[itly-plugin-custom] flush()
[itly-plugin-custom] shutdown()'''
