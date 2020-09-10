import enum
from typing import List, Optional, Tuple

import pytest

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

    def post_alias(self, user_id: str, previous_id: str) -> None:
        pass

    def identify(self, user_id: str, properties: Optional[Properties]) -> None:
        pass

    def post_identify(self, user_id: str, properties: Optional[Properties], validation_results: List[ValidationResponse]) -> None:
        pass

    def group(self, user_id: str, group_id: str, properties: Optional[Properties]) -> None:
        pass

    def post_group(self, user_id: str, group_id: str, properties: Optional[Properties], validation_results: List[ValidationResponse]) -> None:
        pass

    def page(self, user_id: str, category: Optional[str], name: Optional[str], properties: Optional[Properties]) -> None:
        pass

    def post_page(self, user_id: str, category: Optional[str], name: Optional[str], properties: Optional[Properties], validation_results: List[ValidationResponse]) -> None:
        pass

    def track(self, user_id: str, event: Event) -> None:
        pass

    def post_track(self, user_id: str, event: Event, validation_results: List[ValidationResponse]) -> None:
        pass

    def flush(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def validate(self, event: Event) -> ValidationResponse:
        if event.properties is not None and 'invalid' in event.properties:
            return self._create_invalid_response('invalid event!!!')
        return self._create_valid_response()


class RequiredEnum(enum.Enum):
    Enum1 = "Enum1"
    Enum2 = "Enum2"


class OptionalEnum(enum.Enum):
    Value1 = "Value 1"
    Value2 = "Value 2"


def test_load_default_options_succeeds() -> None:
    itly = Itly()
    itly.load(Options())


def test_double_load_throws_exception() -> None:
    itly = Itly()
    itly.load(Options())
    with pytest.raises(Exception) as ctx:
        itly.load(Options())

    assert str(ctx.value) == 'Itly is already initialized. itly.load() should only be called once.'


def test_alias_before_load_throws_error() -> None:
    itly = Itly()
    with pytest.raises(Exception) as ctx:
        itly.alias('user-id', 'previous-user-id')

    assert str(ctx.value) == 'Itly is not yet initialized. Have you called `itly.load()` on app start?'


def test_group_before_load_throws_error() -> None:
    itly = Itly()
    with pytest.raises(Exception) as ctx:
        itly.group('user-id', 'group-id')

    assert str(ctx.value) == 'Itly is not yet initialized. Have you called `itly.load()` on app start?'


def test_identify_before_load_throws_error() -> None:
    itly = Itly()
    with pytest.raises(Exception) as ctx:
        itly.identify('user-id')

    assert str(ctx.value) == 'Itly is not yet initialized. Have you called `itly.load()` on app start?'


def test_page_before_load_throws_error() -> None:
    itly = Itly()
    with pytest.raises(Exception) as ctx:
        itly.page('user-id', 'category', 'name')

    assert str(ctx.value) == 'Itly is not yet initialized. Have you called `itly.load()` on app start?'


def test_track_before_load_throws_error() -> None:
    itly = Itly()
    with pytest.raises(Exception) as ctx:
        itly.track('user-id', Event("event"))

    assert str(ctx.value) == 'Itly is not yet initialized. Have you called `itly.load()` on app start?'


def test_flush_before_load_throws_error() -> None:
    itly = Itly()
    with pytest.raises(Exception) as ctx:
        itly.flush()

    assert str(ctx.value) == 'Itly is not yet initialized. Have you called `itly.load()` on app start?'


def test_shutdown_before_load_throws_error() -> None:
    itly = Itly()
    with pytest.raises(Exception) as ctx:
        itly.shutdown()

    assert str(ctx.value) == 'Itly is not yet initialized. Have you called `itly.load()` on app start?'


def test_double_shutdown_throws_exception() -> None:
    itly = Itly()
    itly.load(Options())
    itly.shutdown()
    with pytest.raises(Exception) as ctx:
        itly.shutdown()

    assert str(ctx.value) == 'Itly is shutdown. No more requests are possible.'


def test_track_after_shutdown_throws_error() -> None:
    itly = Itly()
    itly.load(Options())
    itly.shutdown()
    with pytest.raises(Exception) as ctx:
        itly.track('user-id', Event("event"))

    assert str(ctx.value) == 'Itly is shutdown. No more requests are possible.'


def test_identify_without_properties_succeeds() -> None:
    itly = Itly()
    logger = CustomLogger()
    itly.load(Options(logger=logger, plugins=[CustomPlugin()], context=Properties(context_property=1)))
    itly.identify('user-id')

    log_text = '\n'.join(logger.log_lines)
    assert log_text, """[itly-core] load()
[plugin-custom] load()
[itly-core] identify(user_id=user-id, properties=None)
[plugin-custom] validate(event=identify, properties=None)
[plugin-custom] identify(user_id=user-id, properties=None)
[plugin-custom] post_identify(user_id=user-id, properties=None, validation_results=[])"""


def test_identify_with_properties_succeeds() -> None:
    itly = Itly()
    logger = CustomLogger()
    itly.load(Options(logger=logger, plugins=[CustomPlugin()], context=Properties(context_property=1)))
    itly.identify('user-id', Properties(
        required_number=42.0,
    ))

    log_text = '\n'.join(logger.log_lines)
    assert log_text == """[itly-core] load()
[plugin-custom] load()
[itly-core] identify(user_id=user-id, properties={"required_number": 42.0})
[plugin-custom] validate(event=identify, properties={"required_number": 42.0})
[plugin-custom] identify(user_id=user-id, properties={"required_number": 42.0})
[plugin-custom] post_identify(user_id=user-id, properties={"required_number": 42.0}, validation_results=[])"""


def test_group_without_properties_succeeds() -> None:
    itly = Itly()
    logger = CustomLogger()
    itly.load(Options(logger=logger, plugins=[CustomPlugin()], context=Properties(context_property=1)))
    itly.group('user-id', 'group-id')

    log_text = '\n'.join(logger.log_lines)
    assert log_text == """[itly-core] load()
[plugin-custom] load()
[itly-core] group(user_id=user-id, group_id=group-id, properties=None)
[plugin-custom] validate(event=group, properties=None)
[plugin-custom] group(user_id=user-id, group_id=group-id, properties=None)
[plugin-custom] post_group(user_id=user-id, group_id=group-id, properties=None, validation_results=[])"""


def test_group_with_properties_succeeds() -> None:
    itly = Itly()
    logger = CustomLogger()
    itly.load(Options(logger=logger, plugins=[CustomPlugin()], context=Properties(context_property=1)))
    itly.group('user-id', 'group-id', Properties(
        required_boolean=True,
    ))

    log_text = '\n'.join(logger.log_lines)
    assert log_text == """[itly-core] load()
[plugin-custom] load()
[itly-core] group(user_id=user-id, group_id=group-id, properties={"required_boolean": true})
[plugin-custom] validate(event=group, properties={"required_boolean": true})
[plugin-custom] group(user_id=user-id, group_id=group-id, properties={"required_boolean": true})
[plugin-custom] post_group(user_id=user-id, group_id=group-id, properties={"required_boolean": true}, validation_results=[])"""


def test_events_succeeds() -> None:
    user_id = 'test-user-id'

    itly = Itly()
    logger = CustomLogger()
    itly.load(Options(
        environment=Environment.PRODUCTION,
        context=Properties(
            requiredString='A required string',
            optionalEnum=OptionalEnum.Value1,
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
        required_enum=RequiredEnum.Enum1,
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
    assert log_text == '''[itly-core] load()
[plugin-custom] load()
[itly-core] identify(user_id=user-id, properties={"user_prop": 1})
[plugin-custom] validate(event=identify, properties={"user_prop": 1})
[plugin-custom] identify(user_id=user-id, properties={"user_prop": 1})
[plugin-custom] post_identify(user_id=user-id, properties={"user_prop": 1}, validation_results=[])
[itly-core] alias(user_id=test-user-id, previous_id=user-id)
[plugin-custom] alias(user_id=test-user-id, previous_id=user-id)
[plugin-custom] post_alias(user_id=test-user-id, previous_id=user-id)
[itly-core] group(user_id=test-user-id, group_id=a-group-id, properties={"group_prop": "test value"})
[plugin-custom] validate(event=group, properties={"group_prop": "test value"})
[plugin-custom] group(user_id=test-user-id, group_id=a-group-id, properties={"group_prop": "test value"})
[plugin-custom] post_group(user_id=test-user-id, group_id=a-group-id, properties={"group_prop": "test value"}, validation_results=[])
[itly-core] page(user_id=test-user-id, category=page category, name=page name, properties={"page_prop": "a page property"})
[plugin-custom] validate(event=page, properties={"page_prop": "a page property"})
[plugin-custom] page(user_id=test-user-id, category=page category, name=page name, properties={"page_prop": "a page property"})
[plugin-custom] post_page(user_id=test-user-id, category=page category, name=page name, properties={"page_prop": "a page property"}, validation_results=[])
[itly-core] track(user_id=test-user-id, event=Event No Properties, properties=None)
[plugin-custom] validate(event=context, properties={"requiredString": "A required string", "optionalEnum": "Value 1"})
[plugin-custom] validate(event=Event No Properties, properties=None)
[plugin-custom] track(user_id=test-user-id, event=Event No Properties, properties={"requiredString": "A required string", "optionalEnum": "Value 1"})
[plugin-custom] post_track(user_id=test-user-id, event=Event No Properties, properties={"requiredString": "A required string", "optionalEnum": "Value 1"}, validation_results=[])
[itly-core] track(user_id=test-user-id, event=Event With All Properties, properties={"required_string": "A required string", "required_number": 2.0, "required_integer": 42, "required_enum": "Enum1", "required_boolean": false, "required_const": "some-const-value", "required_array": ["required", "array"], "optional_string": "I'm optional!"})
[plugin-custom] validate(event=context, properties={"requiredString": "A required string", "optionalEnum": "Value 1"})
[plugin-custom] validate(event=Event With All Properties, properties={"required_string": "A required string", "required_number": 2.0, "required_integer": 42, "required_enum": "Enum1", "required_boolean": false, "required_const": "some-const-value", "required_array": ["required", "array"], "optional_string": "I'm optional!"})
[plugin-custom] track(user_id=test-user-id, event=Event With All Properties, properties={"requiredString": "A required string", "optionalEnum": "Value 1", "required_string": "A required string", "required_number": 2.0, "required_integer": 42, "required_enum": "Enum1", "required_boolean": false, "required_const": "some-const-value", "required_array": ["required", "array"], "optional_string": "I'm optional!"})
[plugin-custom] post_track(user_id=test-user-id, event=Event With All Properties, properties={"requiredString": "A required string", "optionalEnum": "Value 1", "required_string": "A required string", "required_number": 2.0, "required_integer": 42, "required_enum": "Enum1", "required_boolean": false, "required_const": "some-const-value", "required_array": ["required", "array"], "optional_string": "I'm optional!"}, validation_results=[])
[itly-core] flush()
[plugin-custom] flush()
[itly-core] track(user_id=test-user-id, event=EventMaxIntForTest, properties={"int_max_10": 20})
[plugin-custom] validate(event=context, properties={"requiredString": "A required string", "optionalEnum": "Value 1"})
[plugin-custom] validate(event=EventMaxIntForTest, properties={"int_max_10": 20})
[plugin-custom] track(user_id=test-user-id, event=EventMaxIntForTest, properties={"requiredString": "A required string", "optionalEnum": "Value 1", "int_max_10": 20})
[plugin-custom] post_track(user_id=test-user-id, event=EventMaxIntForTest, properties={"requiredString": "A required string", "optionalEnum": "Value 1", "int_max_10": 20}, validation_results=[])
[itly-core] flush()
[plugin-custom] flush()
[itly-core] shutdown()
[plugin-custom] shutdown()'''  # nopep8


def test_events_disabled() -> None:
    user_id = 'test-user-id'

    itly = Itly()
    logger = CustomLogger()
    itly.load(Options(
        environment=Environment.PRODUCTION,
        context=Properties(
            requiredString='A required string',
            optionalEnum=OptionalEnum.Value1,
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
        required_enum=RequiredEnum.Enum1,
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
    assert log_text == '''[itly-core] disabled = True'''


def test_development_failed_validation() -> None:
    validation_results = [
        (None, "invalid event!!!", '''[itly-core] load()
[plugin-custom] load()
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=context, properties=None)
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] post_track(user_id=user-id, event=event, properties={"invalid": true}, validation_results=[ValidationResponse(valid=False, plugin_id='custom', message='invalid event!!!')])'''),
        # nopep8
        (ValidationOptions(disabled=False, track_invalid=False, error_on_invalid=False), None, '''[itly-core] load()
[plugin-custom] load()
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=context, properties=None)
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] post_track(user_id=user-id, event=event, properties={"invalid": true}, validation_results=[ValidationResponse(valid=False, plugin_id='custom', message='invalid event!!!')])'''),
        # nopep8
        (ValidationOptions(disabled=False, track_invalid=False, error_on_invalid=True), "invalid event!!!", '''[itly-core] load()
[plugin-custom] load()
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=context, properties=None)
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] post_track(user_id=user-id, event=event, properties={"invalid": true}, validation_results=[ValidationResponse(valid=False, plugin_id='custom', message='invalid event!!!')])'''),
        # nopep8
        (ValidationOptions(disabled=False, track_invalid=True, error_on_invalid=False), None, '''[itly-core] load()
[plugin-custom] load()
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=context, properties=None)
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] post_track(user_id=user-id, event=event, properties={"invalid": true}, validation_results=[ValidationResponse(valid=False, plugin_id='custom', message='invalid event!!!')])'''),
        # nopep8
        (ValidationOptions(disabled=False, track_invalid=True, error_on_invalid=True), "invalid event!!!", '''[itly-core] load()
[plugin-custom] load()
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=context, properties=None)
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] post_track(user_id=user-id, event=event, properties={"invalid": true}, validation_results=[ValidationResponse(valid=False, plugin_id='custom', message='invalid event!!!')])'''),
        # nopep8
        (ValidationOptions(disabled=True, track_invalid=True, error_on_invalid=True), None, '''[itly-core] load()
[plugin-custom] load()
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] post_track(user_id=user-id, event=event, properties={"invalid": true}, validation_results=[])'''),
    ]
    _check_validation_results(Environment.DEVELOPMENT, validation_results)


def test_production_failed_validation() -> None:
    validation_results = [
        (None, None, '''[itly-core] load()
[plugin-custom] load()
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=context, properties=None)
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] post_track(user_id=user-id, event=event, properties={"invalid": true}, validation_results=[ValidationResponse(valid=False, plugin_id='custom', message='invalid event!!!')])'''),
        # nopep8
        (ValidationOptions(disabled=False, track_invalid=False, error_on_invalid=False), None, '''[itly-core] load()
[plugin-custom] load()
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=context, properties=None)
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] post_track(user_id=user-id, event=event, properties={"invalid": true}, validation_results=[ValidationResponse(valid=False, plugin_id='custom', message='invalid event!!!')])'''),
        # nopep8
        (ValidationOptions(disabled=False, track_invalid=False, error_on_invalid=True), "invalid event!!!", '''[itly-core] load()
[plugin-custom] load()
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=context, properties=None)
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] post_track(user_id=user-id, event=event, properties={"invalid": true}, validation_results=[ValidationResponse(valid=False, plugin_id='custom', message='invalid event!!!')])'''),
        # nopep8
        (ValidationOptions(disabled=False, track_invalid=True, error_on_invalid=False), None, '''[itly-core] load()
[plugin-custom] load()
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=context, properties=None)
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] post_track(user_id=user-id, event=event, properties={"invalid": true}, validation_results=[ValidationResponse(valid=False, plugin_id='custom', message='invalid event!!!')])'''),
        # nopep8
        (ValidationOptions(disabled=False, track_invalid=True, error_on_invalid=True), "invalid event!!!", '''[itly-core] load()
[plugin-custom] load()
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] validate(event=context, properties=None)
[plugin-custom] validate(event=event, properties={"invalid": true})
[plugin-custom] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] post_track(user_id=user-id, event=event, properties={"invalid": true}, validation_results=[ValidationResponse(valid=False, plugin_id='custom', message='invalid event!!!')])'''),
        # nopep8
        (ValidationOptions(disabled=True, track_invalid=True, error_on_invalid=True), None, '''[itly-core] load()
[plugin-custom] load()
[itly-core] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] track(user_id=user-id, event=event, properties={"invalid": true})
[plugin-custom] post_track(user_id=user-id, event=event, properties={"invalid": true}, validation_results=[])'''),
    ]
    _check_validation_results(Environment.PRODUCTION, validation_results)


def _check_validation_results(environment: Environment, validation_results: List[Tuple[ValidationOptions, Optional[str], str]]) -> None:
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
            with pytest.raises(Exception) as ctx:
                itly.track('user-id', Event("event", Properties(invalid=True)))
            assert str(ctx.value) == error_text
        else:
            itly.track('user-id', Event("event", Properties(invalid=True)))
        log_text = '\n'.join(logger.log_lines)
        assert expected_log == log_text
