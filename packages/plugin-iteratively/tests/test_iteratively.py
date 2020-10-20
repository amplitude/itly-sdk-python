import json
import re
import time
from copy import deepcopy
from datetime import timedelta
from typing import List, Any

from pytest_httpserver import HTTPServer

from itly_plugin_iteratively import IterativelyPlugin, IterativelyOptions, IterativelyRetryOptions
from itly_sdk import PluginLoadOptions, Environment, Properties, Event, Logger, ValidationResponse

# Test Fixtures
user_id = "test-user-id"
PLUGIN_OPTIONS_DEV_NO_LOGGER = PluginLoadOptions(
    environment=Environment.DEVELOPMENT,
    logger=Logger.NONE
)

# Invalid identify call
post_identify_1_args = [
    user_id,
    Properties(item1='value1', item2=2),
    [
        ValidationResponse(valid=True, plugin_id='custom', message=''),
        ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
    ]
]
post_identify_1_expected_request = {
    'type': 'identify',
    'properties': {'item1': 'value1', 'item2': 2},
    'valid': False,
    'validation': {'details': 'invalid!!!'}
}

# Valid Identify Call
post_identify_2_args = [
    user_id,
    Properties(item1='value3', item2=4),
    []
]
post_identify_2_expected_request = {
    'type': 'identify',
    'properties': {'item1': 'value3', 'item2': 4},
    'valid': True,
    'validation': {'details': ''}
}

# Valid Group Call Info
post_group_args = [
    "user-2", "group-2", Properties(item1='value2', item2=2), []
]
post_group_expected_request = {
    'type': 'group',
    'properties': {'item1': 'value2', 'item2': 2},
    'valid': True,
    'validation': {'details': ''}
}

# Valid Group Call Info
post_page_args = [
    "user-2",
    "category-2",
    "page-3",
    Properties(item1='value3', item2=3),
    [
        ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
        ValidationResponse(valid=True, plugin_id='custom', message=''),
    ]
]
post_page_expected_request = {
    'type': 'page',
    'properties': {'item1': 'value3', 'item2': 3},
    'valid': False,
    'validation': {'details': 'invalid!!!'}
}

# Valid Track Call Info
post_track_1_args = [
    "user-2",
    Event('event-1', Properties(item1='value1', item2=1)),
    [
        ValidationResponse(valid=False, plugin_id='custom', message='not valid!!!'),
        ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
    ]
]
post_track_1_expected_request = {
    'type': 'track',
    'properties': {'item1': 'value1', 'item2': 1},
    'valid': False,
    'validation': {'details': 'not valid!!!'},
    'eventName': 'event-1'
}

# Track Call Info
post_track_2_args = [
    user_id,
    Event(
        'event-5',
        Properties(item1='value5', item2=5),
        id_='id-5',
        version='version-5'
    ),
    []
]

post_track_2_expected_request = {
    'type': 'track',
    'properties': {'item1': 'value5', 'item2': 5},
    'valid': True,
    'validation': {'details': ''},
    'eventName': 'event-5',
    'eventId': 'id-5',
    'eventSchemaVersion': 'version-5'
}


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


def configure_plugin_and_server(httpserver: HTTPServer, options: IterativelyOptions) -> IterativelyPlugin:
    httpserver.expect_request(re.compile('/track')).respond_with_data()
    return IterativelyPlugin('Test-Api-Key', httpserver.url_for('/track'), options)


def strip_property_values(req: Any):
    # Removes values to test omit_values
    for key in req['properties']:
        req['properties'][key] = None
    req['validation']['details'] = ''


def test_flush_at_queue_size(httpserver: HTTPServer):
    p = configure_plugin_and_server(httpserver, IterativelyOptions(
        flush_queue_size=3,
        flush_interval=timedelta(seconds=1),
    ))

    try:
        p.load(PLUGIN_OPTIONS_DEV_NO_LOGGER)

        p.post_identify(*post_identify_1_args)
        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        # Assert no requests (not flushed @ 1)
        assert requests == []

        p.post_identify(*post_identify_2_args)
        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        # Assert no requests (not flushed @ 2)
        assert requests == []

        p.post_track(*post_track_1_args)
        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        # Assert requests (flushed @ 3)
        assert requests == [{'objects': [
            post_identify_1_expected_request,
            post_identify_2_expected_request,
            post_track_1_expected_request
        ]}]
    finally:
        p.shutdown()
        httpserver.stop()


def test_flush_at_interval(httpserver: HTTPServer):
    p = configure_plugin_and_server(httpserver, IterativelyOptions(
        flush_queue_size=3,
        flush_interval=timedelta(seconds=1),
    ))

    try:
        p.load(PLUGIN_OPTIONS_DEV_NO_LOGGER)

        p.post_page(*post_page_args)
        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == []

        time.sleep(1.0)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {'objects': [
                post_page_expected_request
            ]},
        ]
    finally:
        p.shutdown()
        httpserver.stop()


def test_flush_on_flush(httpserver: HTTPServer):
    p = configure_plugin_and_server(httpserver, IterativelyOptions(
        flush_queue_size=3,
        flush_interval=timedelta(seconds=1),
    ))

    try:
        p.load(PLUGIN_OPTIONS_DEV_NO_LOGGER)

        p.post_group(*post_group_args)
        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        # Assert no requests (not flushed)
        assert requests == []

        p.flush()
        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        # Assert requests were flushed
        assert requests == [{'objects': [
            post_group_expected_request,
        ]}]

        # Assert additional flushes do nothing
        p.flush()
        p.flush()
        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        # Assert requests were flushed
        assert requests == [{'objects': [
            post_group_expected_request,
        ]}]
    finally:
        p.shutdown()
        httpserver.stop()


def test_flush_on_shutdown(httpserver: HTTPServer):
    p = configure_plugin_and_server(httpserver, IterativelyOptions(
        flush_queue_size=3,
        flush_interval=timedelta(seconds=1),
    ))

    assert p.id() == 'iteratively'
    try:
        p.load(PLUGIN_OPTIONS_DEV_NO_LOGGER)
        p.post_track(*post_track_2_args)

    finally:
        p.shutdown()

        time.sleep(0.1)
        httpserver.stop()
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {'objects': [
                post_track_2_expected_request
            ]},
        ]


def test_iteratively_omit_values(httpserver: HTTPServer):
    p = configure_plugin_and_server(httpserver, IterativelyOptions(
        omit_values=True,
        flush_queue_size=10
    ))

    try:
        p.load(PLUGIN_OPTIONS_DEV_NO_LOGGER)

        p.post_identify(*post_identify_1_args)
        p.post_identify(*post_identify_2_args)
        p.post_track(*post_track_1_args)
        p.post_group(*post_group_args)
        p.post_page(*post_page_args)
        p.post_track(*post_track_2_args)
    finally:
        p.shutdown()

        time.sleep(0.1)
        httpserver.stop()
        requests = _get_cleaned_requests(httpserver)
        expected_requests = deepcopy([
            post_identify_1_expected_request,
            post_identify_2_expected_request,
            post_track_1_expected_request,
            post_group_expected_request,
            post_page_expected_request,
            post_track_2_expected_request
        ])

        for req in expected_requests:
            strip_property_values(req)

        assert requests == [{'objects': expected_requests}]


def test_iteratively_disabled(httpserver: HTTPServer):
    p = configure_plugin_and_server(httpserver, IterativelyOptions(
        disabled=True,
        flush_queue_size=3,
        flush_interval=timedelta(seconds=1),
    ))

    try:
        p.load(PLUGIN_OPTIONS_DEV_NO_LOGGER)

        p.post_identify(*post_identify_1_args)
        p.post_identify(*post_identify_2_args)
        p.post_track(*post_track_1_args)
        p.post_group(*post_group_args)
        p.flush()

        p.post_page(*post_page_args)

        p.flush()
        p.flush()

        p.post_track(*post_track_2_args)
    finally:
        p.shutdown()

        time.sleep(0.1)
        httpserver.stop()
        requests = _get_cleaned_requests(httpserver)
        assert requests == []


def test_iteratively_retry(httpserver: HTTPServer):
    logger = CustomLogger()
    p = IterativelyPlugin('My-Key', httpserver.url_for('/track'), IterativelyOptions(
        flush_queue_size=3,
        flush_interval=timedelta(seconds=1),
        retry_options=IterativelyRetryOptions(
            max_retries=3,
            delay_initial=timedelta(seconds=0.1),
            delay_maximum=timedelta(seconds=0.5)
        ),
    ))
    expected_request = {'objects': [post_track_1_expected_request]}

    try:
        p.load(PluginLoadOptions(environment=Environment.DEVELOPMENT, logger=logger))

        httpserver.expect_oneshot_request(re.compile('/track')).respond_with_data(status=429)
        httpserver.expect_oneshot_request(re.compile('/track')).respond_with_data(status=501)
        httpserver.expect_oneshot_request(re.compile('/track')).respond_with_data()
        p.post_track(*post_track_1_args)
        p.flush()
        time.sleep(2)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            expected_request,
            expected_request,
            expected_request
        ]
        assert logger.log_lines == []

        httpserver.expect_oneshot_request(re.compile('/track')).respond_with_data(status=429)
        httpserver.expect_oneshot_request(re.compile('/track')).respond_with_data(status=501)
        httpserver.expect_oneshot_request(re.compile('/track')).respond_with_data(status=504)
        httpserver.expect_oneshot_request(re.compile('/track')).respond_with_data()
        p.post_track(*post_track_1_args)
        p.flush()
        time.sleep(2)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            expected_request,
            expected_request,
            expected_request,
            expected_request,
            expected_request,
            expected_request,
        ]
        assert logger.log_lines == ['Error. Failed to upload events. Maximum attempts exceeded.']
    finally:
        p.shutdown()
        httpserver.stop()


def _get_cleaned_requests(httpserver: Any) -> List[Any]:
    requests = [json.loads(data) for data in httpserver.collected_data]
    for request in requests:
        for event in request['objects']:
            del event['dateSent']
    return requests
