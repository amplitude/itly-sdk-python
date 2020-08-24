import enum
import unittest
from typing import List

from itly.sdk import itly, Options, Environment, Event, Properties
from .custom_logger import CustomLogger
from .custom_plugin import CustomPlugin


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
        assert log_text == '''[itly-plugin-custom] load() environment='PRODUCTION'
[itly-plugin-custom] validate() event='context'
[itly-plugin-custom] validate() event='identify'
[itly-plugin-custom] identify() user_id='user-id' properties={"user_prop": 1}
[itly-plugin-custom] alias() user_id='test-user-id' previous_id='user-id'
[itly-plugin-custom] validate() event='group'
[itly-plugin-custom] group() user_id='test-user-id' group_id='a-group-id' properties={"group_prop": "test value"}
[itly-plugin-custom] validate() event='page'
[itly-plugin-custom] page() user_id='test-user-id' category='page category' name='page name' properties={"page_prop": "a page property"}
[itly-plugin-custom] validate() event='Event No Properties'
[itly-plugin-custom] track() user_id='test-user-id' event='Event No Properties' properties={"requiredString": "A required string", "optionalEnum": "Value 1"}
[itly-plugin-custom] validate() event='Event With All Properties'
[itly-plugin-custom] track() user_id='test-user-id' event='Event With All Properties' properties={"requiredString": "A required string", "optionalEnum": "Value 1", "required_string": "A required string", "required_number": 2.0, "required_integer": 42, "required_enum": "Enum1", "required_boolean": false, "required_const": "some-const-value", "required_array": ["required", "array"], "optional_string": "I'm optional!"}
[itly-plugin-custom] flush()
[itly-plugin-custom] validate() event='EventMaxIntForTest'
[itly-plugin-custom] track() user_id='test-user-id' event='EventMaxIntForTest' properties={"requiredString": "A required string", "optionalEnum": "Value 1", "int_max_10": 20}
[itly-plugin-custom] flush()
[itly-plugin-custom] shutdown()'''
