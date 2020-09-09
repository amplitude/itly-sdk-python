import enum
import unittest
from typing import Optional, List

from itly.plugin_schema_validator import SchemaValidatorPlugin
from itly.sdk import PluginLoadOptions, Environment, Properties, Event, Logger

DEFAULT_SCHEMAS = {
    'context': '{"$id":"https://iterative.ly/company/77b37977-cb3a-42eb-bce3-09f5f7c3adb7/context","$schema":"http://json-schema.org/draft-07/schema#","title":"Context","description":"","type":"object","properties":{"requiredString":{"description":"description for context requiredString","type":"string"},"optionalEnum":{"description":"description for context optionalEnum","enum":["Value 1","Value 2"]}},"additionalProperties":false,"required":["requiredString"]}',  # nopep8
    'group': '{"$id":"https://iterative.ly/company/77b37977-cb3a-42eb-bce3-09f5f7c3adb7/group","$schema":"http://json-schema.org/draft-07/schema#","title":"Group","description":"","type":"object","properties":{"requiredBoolean":{"description":"Description for group requiredBoolean","type":"boolean"},"optionalString":{"description":"Description for group optionalString","type":"string"}},"additionalProperties":false,"required":["requiredBoolean"]}',  # nopep8
    'identify': '{"$id":"https://iterative.ly/company/77b37977-cb3a-42eb-bce3-09f5f7c3adb7/identify","$schema":"http://json-schema.org/draft-07/schema#","title":"Identify","description":"","type":"object","properties":{"optionalArray":{"description":"Description for identify optionalArray","type":"array","uniqueItems":false,"items":{"type":"string"}},"requiredNumber":{"description":"Description for identify requiredNumber","type":"number"}},"additionalProperties":false,"required":["requiredNumber"]}',  # nopep8
    'Event With Optional Properties': '{"$id":"https://iterative.ly/company/77b37977-cb3a-42eb-bce3-09f5f7c3adb7/event/00b99136-9d1a-48d8-89d5-25f165ff3ae0/version/1.0.0","$schema":"http://json-schema.org/draft-07/schema#","title":"Event With Optional Properties","description":"Event w optional properties description","type":"object","properties":{"optionalNumber":{"description":"","type":"number"},"optionalArrayString":{"description":"","type":"array","items":{"type":"string"}},"optionalArrayNumber":{"description":"","type":"array","items":{"type":"number"}},"optionalString":{"description":"Optional String property description","type":"string"},"optionalBoolean":{"description":"","type":"boolean"}},"additionalProperties":false,"required":[]}',  # nopep8
    'Event No Properties': '{"$id":"https://iterative.ly/company/77b37977-cb3a-42eb-bce3-09f5f7c3adb7/event/26af925a-be3a-40e5-947d-33da66a5352f/version/1.0.0","$schema":"http://json-schema.org/draft-07/schema#","title":"Event No Properties","description":"Event w no properties description","type":"object","properties":{},"additionalProperties":false,"required":[]}',  # nopep8
    'Event With Optional Array Types': '{"$id":"https://iterative.ly/company/77b37977-cb3a-42eb-bce3-09f5f7c3adb7/event/2755da0e-a507-4b18-8f17-86d1d5c499ab/version/1.0.0","$schema":"http://json-schema.org/draft-07/schema#","title":"Event With Optional Array Types","description":"Description for event with optional array types","type":"object","properties":{"optionalStringArray":{"description":"Description for optional string array","type":"array","items":{"type":"string"}},"optionalJSONArray":{"description":"Description for optional object array","type":"array","items":{"type":"object"}},"optionalBooleanArray":{"description":"Description for optional boolean array","type":"array","items":{"type":"boolean"}},"optionalNumberArray":{"description":"Description for optional number array","type":"array","items":{"type":"number"}}},"additionalProperties":false,"required":[]}',  # nopep8
    'Event With All Properties': '{"$id":"https://iterative.ly/company/77b37977-cb3a-42eb-bce3-09f5f7c3adb7/event/311ba144-8532-4474-a9bd-8b430625e29a/version/1.0.0","$schema":"http://json-schema.org/draft-07/schema#","title":"Event With All Properties","description":"Event w all properties description","type":"object","properties":{"requiredConst":{"description":"Event 2 Property - Const","const":"some-const-value"},"requiredInteger":{"description":"Event 2 Property - Integer    *     * Examples:    * 5, 4, 3","type":"integer"},"optionalString":{"description":"Event 2 Property - Optional String    *     * Examples:    * Some string, or another","type":"string"},"requiredNumber":{"description":"Event 2 Property - Number","type":"number"},"requiredString":{"description":"Event 2 Property - String","type":"string"},"requiredArray":{"description":"Event 2 Property - Array","type":"array","minItems":0,"items":{"type":"string"}},"requiredEnum":{"description":"Event 2 Property - Enum","enum":["Enum1","Enum2"]},"requiredBoolean":{"description":"Event 2 Property - Boolean","type":"boolean"}},"additionalProperties":false,"required":["requiredConst","requiredInteger","requiredNumber","requiredString","requiredArray","requiredEnum","requiredBoolean"]}',  # nopep8
    'Event With Const Types': '{"$id":"https://iterative.ly/company/77b37977-cb3a-42eb-bce3-09f5f7c3adb7/event/321b8f02-1bb3-4b33-8c21-8c55401d62da/version/1.0.0","$schema":"http://json-schema.org/draft-07/schema#","title":"Event With Const Types","description":"Description for event with const types","type":"object","properties":{"Integer Const":{"description":"Description for integer const","const":10},"Boolean Const":{"description":"Description for boolean const type","const":true},"String Int Const":{"description":"Description for string int const","const":0},"Number Const":{"description":"Description for number const","const":2.2},"String Const WIth Quotes":{"description":"Description for Int With Quotes","const":"\\"String \\"Const With\\" Quotes\\""},"String Const":{"description":"Description for string const","const":"String-Constant"}},"additionalProperties":false,"required":["Integer Const","Boolean Const","String Int Const","Number Const","String Const WIth Quotes","String Const"]}',  # nopep8
    'Event With Array Types': '{"$id":"https://iterative.ly/company/77b37977-cb3a-42eb-bce3-09f5f7c3adb7/event/5ded19cd-6015-441b-a2be-f954425be1fe/version/1.0.0","$schema":"http://json-schema.org/draft-07/schema#","title":"Event With Array Types","description":"Description for event with Array Types","type":"object","properties":{"requiredBooleanArray":{"description":"description for required boolean array","type":"array","items":{"type":"boolean"}},"requiredStringArray":{"description":"description for required string array","type":"array","items":{"type":"string"}},"requiredObjectArray":{"description":"Description for required object array","type":"array","items":{"type":"object"}},"requiredNumberArray":{"description":"Description for required number array","type":"array","items":{"type":"number"}}},"additionalProperties":false,"required":["requiredBooleanArray","requiredStringArray","requiredObjectArray","requiredNumberArray"]}',  # nopep8
    'EventMaxIntForTest': '{"$id":"https://iterative.ly/company/77b37977-cb3a-42eb-bce3-09f5f7c3adb7/event/aa0f08ac-8928-4569-a524-c1699e7da6f4/version/1.0.0","$schema":"http://json-schema.org/draft-07/schema#","title":"EventMaxIntForTest","description":"Event to test schema validation","type":"object","properties":{"intMax10":{"description":"property to test schema validation","type":"integer","maximum":10}},"additionalProperties":false,"required":["intMax10"]}',  # nopep8
    'Event with Object and Object Array': '{"$id":"https://iterative.ly/company/77b37977-cb3a-42eb-bce3-09f5f7c3adb7/event/aea72ecc-5a10-4bd7-99a6-81a464aabaed/version/1.0.0","$schema":"http://json-schema.org/draft-07/schema#","title":"Event Object Types","description":"Event with Object and Object Array","type":"object","properties":{"requiredObject":{"description":"Property Object Type","type":"object"},"requiredObjectArray":{"description":"Property Object Array Type","type":"array","items":{"type":"object"}}},"additionalProperties":false,"required":["requiredObject","requiredObjectArray"]}',  # nopep8
    'Event With Enum Types': '{"$id":"https://iterative.ly/company/77b37977-cb3a-42eb-bce3-09f5f7c3adb7/event/b4fc8366-b05d-40d3-b698-79795701624b/version/1.0.0","$schema":"http://json-schema.org/draft-07/schema#","title":"Event With Enum Types","description":"Description for event with enum types","type":"object","properties":{"required enum":{"description":"Description for optional enum","enum":["required enum 1","required enum 2"]},"optional enum":{"description":"Description for required enum","enum":["optional enum 1","optional enum 2"]}},"additionalProperties":false,"required":["required enum"]}',  # nopep8
    'event withDifferent_CasingTypes': '{"$id":"https://iterative.ly/company/77b37977-cb3a-42eb-bce3-09f5f7c3adb7/event/fcb3d82d-208f-4bc2-b8e1-843683d9b595/version/1.0.0","$schema":"http://json-schema.org/draft-07/schema#","title":"event withDifferent_CasingTypes","description":"Description for case with space","type":"object","properties":{"EnumPascalCase":{"description":"DescirptionForEnumPascalCase","enum":["EnumPascalCase"]},"property with space":{"description":"Description for case with space","type":"string"},"enum with space":{"description":"Description for enum with space","enum":["enum with space"]},"enum_snake_case":{"description":"description_for_enum_snake_case","enum":["enum_snake_case"]},"propertyWithCamelCase":{"description":"descriptionForCamelCase","type":"string"},"PropertyWithPascalCase":{"description":"DescriptionForPascalCase","type":"string"},"property_with_snake_case":{"description":"Description_for_snake_case","type":"string"},"enumCamelCase":{"description":"descriptionForEnumCamelCase","enum":["enumCamelCase"]}},"additionalProperties":false,"required":["EnumPascalCase","property with space","enum with space","enum_snake_case","propertyWithCamelCase","PropertyWithPascalCase","property_with_snake_case","enumCamelCase"]}'  # nopep8
}


class Context(Event):
    class OptionalEnum(enum.Enum):
        VALUE_1 = 'Value 1'
        VALUE_2 = 'Value 2'

    def __init__(self, required_string: str, optional_enum: "Context.OptionalEnum" = None) -> None:
        properties = {
            "requiredString": required_string
        }
        if optional_enum is not None:
            properties['optionalEnum'] = optional_enum
        super().__init__(
            "context",
            Properties(**properties),
        )


class Group(Event):
    def __init__(self, required_boolean: bool, optional_string: Optional[str] = None) -> None:
        properties = {
            "requiredBoolean": required_boolean
        }
        if optional_string is not None:
            properties['optionalString'] = optional_string
        super().__init__(
            "group",
            Properties(**properties),
        )


class Identify(Event):
    def __init__(self, required_number: float, optional_array: Optional[List[str]] = None) -> None:
        properties = {
            "requiredNumber": required_number
        }
        if optional_array is not None:
            properties['optionalArray'] = optional_array
        super().__init__(
            "identify",
            Properties(**properties),
        )


class EventWithAllProperties(Event):
    class RequiredEnum(enum.Enum):
        ENUM_1 = "Enum1"
        ENUM_2 = "Enum2"

    def __init__(self, required_array: List[str], required_boolean: bool, required_enum: "EventWithAllProperties.RequiredEnum",
                 required_integer: int, required_number: float, required_string: str, optional_string: Optional[str] = None) -> None:
        properties = {
            "requiredArray": required_array,
            "requiredBoolean": required_boolean,
            "requiredConst": "some-const-value",
            "requiredEnum": required_enum,
            "requiredInteger": required_integer,
            "requiredNumber": required_number,
            "requiredString": required_string
        }
        if optional_string is not None:
            properties['optionalString'] = optional_string
        super().__init__(
            "Event With All Properties",
            Properties(**properties),
        )


class EventWithConstTypes(Event):
    def __init__(self) -> None:
        properties = {
            "Boolean Const": True,
            "Integer Const": 10,
            "Number Const": 2.2,
            "String Const": "String-Constant",
            "String Const WIth Quotes": "\"String \"Const With\" Quotes\"",
            "String Int Const": 0
        }
        super().__init__(
            "Event With Const Types",
            Properties(**properties),
        )


class EventMaxIntForTest(Event):
    def __init__(self, int_max_10: int) -> None:
        properties = {
            "intMax10": int_max_10
        }
        super().__init__(
            "EventMaxIntForTest",
            Properties(**properties),
        )


class TestSchemaValidatorPlugin(unittest.TestCase):
    def test_validate_context_with_properties_valid(self):
        plugin = SchemaValidatorPlugin(DEFAULT_SCHEMAS)
        plugin.load(PluginLoadOptions(environment=Environment.PRODUCTION, logger=Logger.NONE))
        validation = plugin.validate(Context(
            required_string="Required context string",
            optional_enum=Context.OptionalEnum.VALUE_1
        ))
        self.assertTrue(validation.valid)

    def test_validate_group_with_properties_valid(self):
        plugin = SchemaValidatorPlugin(DEFAULT_SCHEMAS)
        plugin.load(PluginLoadOptions(environment=Environment.PRODUCTION, logger=Logger.NONE))
        validation = plugin.validate(Group(
            required_boolean=False,
            optional_string="I'm optional!"
        ))
        self.assertTrue(validation.valid)

    def test_validate_identify_with_properties_valid(self):
        plugin = SchemaValidatorPlugin(DEFAULT_SCHEMAS)
        plugin.load(PluginLoadOptions(environment=Environment.PRODUCTION, logger=Logger.NONE))
        validation = plugin.validate(Identify(
            required_number=2.0,
            optional_array=['optional']
        ))
        self.assertTrue(validation.valid)

    def test_validate_event_with_all_properties_valid(self):
        plugin = SchemaValidatorPlugin(DEFAULT_SCHEMAS)
        plugin.load(PluginLoadOptions(environment=Environment.PRODUCTION, logger=Logger.NONE))
        validation = plugin.validate(EventWithAllProperties(
            required_array=['required', 'string'],
            required_boolean=True,
            required_enum=EventWithAllProperties.RequiredEnum.ENUM_1,
            required_integer=42,
            required_number=2.0,
            required_string="don't forget this. it's required.",
        ))
        self.assertTrue(validation.valid)

    def test_validate_event_with_const_types_valid(self):
        plugin = SchemaValidatorPlugin(DEFAULT_SCHEMAS)
        plugin.load(PluginLoadOptions(environment=Environment.PRODUCTION, logger=Logger.NONE))
        validation = plugin.validate(EventWithConstTypes())
        self.assertTrue(validation.valid)

    def test_validate_invalid_event_not_valid(self):
        plugin = SchemaValidatorPlugin(DEFAULT_SCHEMAS)
        plugin.load(PluginLoadOptions(environment=Environment.PRODUCTION, logger=Logger.NONE))
        validation = plugin.validate(EventMaxIntForTest(int_max_10=20))
        self.assertFalse(validation.valid)
        self.assertEqual(validation.message, """Passed in EventMaxIntForTest properties did not validate against your tracking plan. 20 is greater than the maximum of 10

Failed validating 'maximum' in schema['properties']['intMax10']:
    {'description': 'property to test schema validation',
     'maximum': 10,
     'type': 'integer'}

On instance['intMax10']:
    20""")

    def test_validate_unknown_event_exception(self):
        plugin = SchemaValidatorPlugin(DEFAULT_SCHEMAS)
        plugin.load(PluginLoadOptions(environment=Environment.PRODUCTION, logger=Logger.NONE))
        with self.assertRaises(ValueError) as ctx:
            plugin.validate(Event('unknown'))
        self.assertEqual(str(ctx.exception), "Event 'unknown' not found in tracking plan.")
