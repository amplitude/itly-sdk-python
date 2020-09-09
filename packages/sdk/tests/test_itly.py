import enum
import unittest
from typing import List, Optional, Tuple

from itly.sdk import Itly, Options, Environment, Event, Properties, Logger, Plugin, PluginLoadOptions, ValidationResponse, ValidationOptions


class CustomLogger(Logger):
    def __init__(self) -> None:
        self.log_lines: List[str] = []

    def debug(self, message: str) -> None:
        self.log_lines.append(message)

    def info(self, message: str) -> None:
        self.log_lines.append(message)

    def warn(self, message: str) -> None:
        self.log_lines.append(message)

    def error(self, message: str) -> None:
        self.log_lines.append(message)


class CustomPlugin(Plugin):
    def id(self) -> str:
        return 'custom'

    def load(self, options: PluginLoadOptions) -> None:
        pass

    def alias(self, user_id: str, previous_id: str) -> None:
        pass

    def identify(self, user_id: str, properties: Optional[Properties]) -> None:
        pass

    def group(self, user_id: str, group_id: str, properties: Optional[Properties]) -> None:
        pass

    def page(self, user_id: str, category: Optional[str], name: Optional[str], properties: Optional[Properties]) -> None:
        pass

    def track(self, user_id: str, event: Event) -> None:
        pass

    def flush(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    # Validation methods

    def validate(self, event: Event) -> ValidationResponse:
        if event.properties is not None and 'invalid' in event.properties:
            return self._create_invalid_response('invalid event!!!')
        return self._create_valid_response()

    def on_validation_error(self, validation: ValidationResponse, event: Event) -> None:
        pass


class TestEnum(enum.Enum):
    Enum1 = "Enum1"
    Enum2 = "Enum2"


class TestOptionalEnum(enum.Enum):
    Value1 = "Value 1"
    Value2 = "Value 2"


class TestItly(unittest.TestCase):
    def test_load_default_options_succeeds(self) -> None:
        itly = Itly()
        itly.load(Options())

    def test_double_load_throws_exception(self) -> None:
        itly = Itly()
        itly.load(Options())
        with self.assertRaises(Exception) as ctx:
            itly.load(Options())

        self.assertEqual(str(ctx.exception), 'Itly is already initialized. itly.load() should only be called once.')

    def test_alias_before_load_throws_error(self) -> None:
        itly = Itly()
        with self.assertRaises(Exception) as ctx:
            itly.alias('user-id', 'previous-user-id')

        self.assertEqual(str(ctx.exception), 'Itly is not yet initialized. Have you called `itly.load()` on app start?')

    def test_group_before_load_throws_error(self) -> None:
        itly = Itly()
        with self.assertRaises(Exception) as ctx:
            itly.group('user-id', 'group-id')

        self.assertEqual(str(ctx.exception), 'Itly is not yet initialized. Have you called `itly.load()` on app start?')

    def test_identify_before_load_throws_error(self) -> None:
        itly = Itly()
        with self.assertRaises(Exception) as ctx:
            itly.identify('user-id')

        self.assertEqual(str(ctx.exception), 'Itly is not yet initialized. Have you called `itly.load()` on app start?')

    def test_page_before_load_throws_error(self) -> None:
        itly = Itly()
        with self.assertRaises(Exception) as ctx:
            itly.page('user-id', 'category', 'name')

        self.assertEqual(str(ctx.exception), 'Itly is not yet initialized. Have you called `itly.load()` on app start?')

    def test_track_before_load_throws_error(self) -> None:
        itly = Itly()
        with self.assertRaises(Exception) as ctx:
            itly.track('user-id', Event("event"))

        self.assertEqual(str(ctx.exception), 'Itly is not yet initialized. Have you called `itly.load()` on app start?')

    def test_flush_before_load_throws_error(self) -> None:
        itly = Itly()
        with self.assertRaises(Exception) as ctx:
            itly.flush()

        self.assertEqual(str(ctx.exception), 'Itly is not yet initialized. Have you called `itly.load()` on app start?')

    def test_shutdown_before_load_throws_error(self) -> None:
        itly = Itly()
        with self.assertRaises(Exception) as ctx:
            itly.shutdown()

        self.assertEqual(str(ctx.exception), 'Itly is not yet initialized. Have you called `itly.load()` on app start?')

    def test_double_shutdown_throws_exception(self) -> None:
        itly = Itly()
        itly.load(Options())
        itly.shutdown()
        with self.assertRaises(Exception) as ctx:
            itly.shutdown()

        self.assertEqual(str(ctx.exception), 'Itly is shutdown. No more requests are possible.')

    def test_track_after_shutdown_throws_error(self) -> None:
        itly = Itly()
        itly.load(Options())
        itly.shutdown()
        with self.assertRaises(Exception) as ctx:
            itly.track('user-id', Event("event"))

        self.assertEqual(str(ctx.exception), 'Itly is shutdown. No more requests are possible.')

    def test_identify_without_properties_succeeds(self) -> None:
        itly = Itly()
        logger = CustomLogger()
        itly.load(Options(logger=logger, plugins=[CustomPlugin()]))
        itly.identify('user-id')

        log_text = '\n'.join(logger.log_lines)
        self.assertEqual(log_text, """[itly-core] load()
[plugin-custom] load()
[plugin-custom] validate(event=context, properties=None)
[itly-core] identify(user_id=user-id, properties=None)
[plugin-custom] validate(event=identify, properties=None)
[plugin-custom] identify(user_id=user-id, properties=None)""")

    def test_identify_with_properties_succeeds(self) -> None:
        itly = Itly()
        logger = CustomLogger()
        itly.load(Options(logger=logger, plugins=[CustomPlugin()]))
        itly.identify('user-id', Properties(
            required_number=42.0,
        ))

        log_text = '\n'.join(logger.log_lines)
        self.assertEqual(log_text, """[itly-core] load()
[plugin-custom] load()
[plugin-custom] validate(event=context, properties=None)
[itly-core] identify(user_id=user-id, properties={"required_number": 42.0})
[plugin-custom] validate(event=identify, properties={"required_number": 42.0})
[plugin-custom] identify(user_id=user-id, properties={"required_number": 42.0})""")

    def test_group_without_properties_succeeds(self) -> None:
        itly = Itly()
        logger = CustomLogger()
        itly.load(Options(logger=logger, plugins=[CustomPlugin()]))
        itly.group('user-id', 'group-id')

        log_text = '\n'.join(logger.log_lines)
        self.assertEqual(log_text, """[itly-core] load()
[plugin-custom] load()
[plugin-custom] validate(event=context, properties=None)
[itly-core] group(user_id=user-id, group_id=group-id, properties=None)
[plugin-custom] validate(event=group, properties=None)
[plugin-custom] group(user_id=user-id, group_id=group-id, properties=None)""")

    def test_group_with_properties_succeeds(self) -> None:
        itly = Itly()
        logger = CustomLogger()
        itly.load(Options(logger=logger, plugins=[CustomPlugin()]))
        itly.group('user-id', 'group-id', Properties(
            required_boolean=True,
        ))

        log_text = '\n'.join(logger.log_lines)
        self.assertEqual(log_text, """[itly-core] load()
[plugin-custom] load()
[plugin-custom] validate(event=context, properties=None)
[itly-core] group(user_id=user-id, group_id=group-id, properties={"required_boolean": true})
[plugin-custom] validate(event=group, properties={"required_boolean": true})
[plugin-custom] group(user_id=user-id, group_id=group-id, properties={"required_boolean": true})""")

    def test_events_succeeds(self) -> None:
        user_id = 'test-user-id'

        itly = Itly()
        logger = CustomLogger()
        itly.load(Options(
            environment=Environment.PRODUCTION,
            context=Properties(
                requiredString='A required string',
                optionalEnum=TestOptionalEnum.Value1,
            ),
            plugins=[CustomPlugin()],
            logger=logger,
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

        log_text = '\n'.join(logger.log_lines)
        self.assertEqual(log_text, '''[itly-core] load()
[plugin-custom] load()
[plugin-custom] validate(event=context, properties={"requiredString": "A required string", "optionalEnum": "Value 1"})
[itly-core] identify(user_id=user-id, properties={"user_prop": 1})
[plugin-custom] validate(event=identify, properties={"user_prop": 1})
[plugin-custom] identify(user_id=user-id, properties={"user_prop": 1})
[itly-core] alias(user_id=test-user-id, previous_id=user-id)
[plugin-custom] alias(user_id=test-user-id, previous_id=user-id)
[itly-core] group(user_id=test-user-id, group_id=a-group-id, properties={"group_prop": "test value"})
[plugin-custom] validate(event=group, properties={"group_prop": "test value"})
[plugin-custom] group(user_id=test-user-id, group_id=a-group-id, properties={"group_prop": "test value"})
[itly-core] page(user_id=test-user-id, category=page category, name=page name, properties={"page_prop": "a page property"})
[plugin-custom] validate(event=page, properties={"page_prop": "a page property"})
[plugin-custom] page(user_id=test-user-id, category=page category, name=page name, properties={"page_prop": "a page property"})
[itly-core] track(user_id=test-user-id, event=Event No Properties, properties={"requiredString": "A required string", "optionalEnum": "Value 1"})
[plugin-custom] validate(event=Event No Properties, properties=None)
[plugin-custom] track(user_id=test-user-id, event=Event No Properties, properties={"requiredString": "A required string", "optionalEnum": "Value 1"})
[itly-core] track(user_id=test-user-id, event=Event With All Properties, properties={"requiredString": "A required string", "optionalEnum": "Value 1", "required_string": "A required string", "required_number": 2.0, "required_integer": 42, "required_enum": "Enum1", "required_boolean": false, "required_const": "some-const-value", "required_array": ["required", "array"], "optional_string": "I'm optional!"})
[plugin-custom] validate(event=Event With All Properties, properties={"required_string": "A required string", "required_number": 2.0, "required_integer": 42, "required_enum": "Enum1", "required_boolean": false, "required_const": "some-const-value", "required_array": ["required", "array"], "optional_string": "I'm optional!"})
[plugin-custom] track(user_id=test-user-id, event=Event With All Properties, properties={"requiredString": "A required string", "optionalEnum": "Value 1", "required_string": "A required string", "required_number": 2.0, "required_integer": 42, "required_enum": "Enum1", "required_boolean": false, "required_const": "some-const-value", "required_array": ["required", "array"], "optional_string": "I'm optional!"})
[itly-core] flush()
[plugin-custom] flush()
[itly-core] track(user_id=test-user-id, event=EventMaxIntForTest, properties={"requiredString": "A required string", "optionalEnum": "Value 1", "int_max_10": 20})
[plugin-custom] validate(event=EventMaxIntForTest, properties={"int_max_10": 20})
[plugin-custom] track(user_id=test-user-id, event=EventMaxIntForTest, properties={"requiredString": "A required string", "optionalEnum": "Value 1", "int_max_10": 20})
[itly-core] flush()
[plugin-custom] flush()
[itly-core] shutdown()
[plugin-custom] shutdown()''')

    def test_events_disabled(self) -> None:
        user_id = 'test-user-id'

        itly = Itly()
        logger = CustomLogger()
        itly.load(Options(
            environment=Environment.PRODUCTION,
            context=Properties(
                requiredString='A required string',
                optionalEnum=TestOptionalEnum.Value1,
            ),
            plugins=[CustomPlugin()],
            logger=logger,
            disabled=True,
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

        log_text = '\n'.join(logger.log_lines)
        self.assertEqual(log_text, '''[itly-core] disabled = True''')

    def test_development_failed_validation_on_validation_error(self) -> None:
        validation_results = [
            (None, "Validation Error: invalid event!!!", '''[itly-core] load()
[plugin-custom] load()
[plugin-custom] validate(event=context, properties=None)
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] on_validation_error(event=event, validation='invalid event!!!')'''),
            (ValidationOptions(disabled=False, track_invalid=False, error_on_invalid=False), None, '''[itly-core] load()
[plugin-custom] load()
[plugin-custom] validate(event=context, properties=None)
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] on_validation_error(event=event, validation='invalid event!!!')'''),
            (ValidationOptions(disabled=False, track_invalid=False, error_on_invalid=True), "Validation Error: invalid event!!!", '''[itly-core] load()
[plugin-custom] load()
[plugin-custom] validate(event=context, properties=None)
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] on_validation_error(event=event, validation='invalid event!!!')'''),
            (ValidationOptions(disabled=False, track_invalid=True, error_on_invalid=False), None, '''[itly-core] load()
[plugin-custom] load()
[plugin-custom] validate(event=context, properties=None)
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] on_validation_error(event=event, validation='invalid event!!!')
[plugin-custom] track(user_id=user-id, event=event, properties={"invalid": true})'''),
            (ValidationOptions(disabled=False, track_invalid=True, error_on_invalid=True), "Validation Error: invalid event!!!", '''[itly-core] load()
[plugin-custom] load()
[plugin-custom] validate(event=context, properties=None)
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] on_validation_error(event=event, validation='invalid event!!!')'''),
            (ValidationOptions(disabled=True, track_invalid=True, error_on_invalid=True), None, '''[itly-core] load()
[plugin-custom] load()
[plugin-custom] validate(event=context, properties=None)
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] track(user_id=user-id, event=event, properties={"invalid": true})'''),
        ]
        self._check_validation_results(Environment.DEVELOPMENT, validation_results)

    def test_production_failed_validation_on_validation_error(self) -> None:
        validation_results = [
            (None, None, '''[itly-core] load()
[plugin-custom] load()
[plugin-custom] validate(event=context, properties=None)
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] on_validation_error(event=event, validation='invalid event!!!')'''),
            (ValidationOptions(disabled=False, track_invalid=False, error_on_invalid=False), None, '''[itly-core] load()
[plugin-custom] load()
[plugin-custom] validate(event=context, properties=None)
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] on_validation_error(event=event, validation='invalid event!!!')'''),
            (ValidationOptions(disabled=False, track_invalid=False, error_on_invalid=True), "Validation Error: invalid event!!!", '''[itly-core] load()
[plugin-custom] load()
[plugin-custom] validate(event=context, properties=None)
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] on_validation_error(event=event, validation='invalid event!!!')'''),
            (ValidationOptions(disabled=False, track_invalid=True, error_on_invalid=False), None, '''[itly-core] load()
[plugin-custom] load()
[plugin-custom] validate(event=context, properties=None)
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] on_validation_error(event=event, validation='invalid event!!!')
[plugin-custom] track(user_id=user-id, event=event, properties={"invalid": true})'''),
            (ValidationOptions(disabled=False, track_invalid=True, error_on_invalid=True), "Validation Error: invalid event!!!", '''[itly-core] load()
[plugin-custom] load()
[plugin-custom] validate(event=context, properties=None)
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] on_validation_error(event=event, validation='invalid event!!!')'''),
            (ValidationOptions(disabled=True, track_invalid=True, error_on_invalid=True), None, '''[itly-core] load()
[plugin-custom] load()
[plugin-custom] validate(event=context, properties=None)
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] track(user_id=user-id, event=event, properties={"invalid": true})'''),
        ]
        self._check_validation_results(Environment.PRODUCTION, validation_results)

    def _check_validation_results(self, environment: Environment, validation_results: List[Tuple[ValidationOptions, Optional[str], str]]) -> None:
        for validation_options, error_text, expected_log in validation_results:
            itly = Itly()
            logger = CustomLogger()
            itly.load(Options(
                environment=environment,
                logger=logger,
                plugins=[CustomPlugin()],
                validation=validation_options),
            )
            if error_text is not None:
                with self.assertRaises(Exception) as ctx:
                    itly.track('user-id', Event("event", Properties(invalid=True)))
                self.assertEqual(error_text, str(ctx.exception))
            else:
                itly.track('user-id', Event("event", Properties(invalid=True)))
            log_text = '\n'.join(logger.log_lines)
            self.assertEqual(expected_log, log_text)
