import json
import re
import time
from datetime import timedelta
from typing import List, Any
import urllib.parse

from pytest_httpserver import HTTPServer

from itly.plugin_amplitude import AmplitudePlugin, AmplitudeOptions
from itly.sdk import PluginLoadOptions, Environment, Properties, Event, Logger


def test_amplitude(httpserver: HTTPServer):
    httpserver.expect_request(re.compile('/(events|identify)')).respond_with_data()

    options = AmplitudeOptions(
        events_endpoint=httpserver.url_for('/events'),
        identification_endpoint=httpserver.url_for('/identify'),
        flush_queue_size=3,
        flush_interval=timedelta(seconds=1),
    )
    p = AmplitudePlugin('My-Key', options)

    assert p.id() == 'amplitude'
    try:
        p.load(PluginLoadOptions(environment=Environment.DEVELOPMENT, logger=Logger.NONE))

        p.identify("user-1", Properties(item1='value1', item2=2))
        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == []

        p.track("user-2", Event('event-1', Properties(item1='value1', item2=1)))
        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            [
                {"user_id": "user-1", "user_properties": {"item1": "value1", "item2": 2}}
            ],
        ]

        p.track("user-2", Event('event-2', Properties(item1='value2', item2=2)))
        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            [
                {"user_id": "user-1", "user_properties": {"item1": "value1", "item2": 2}}
            ],
        ]

        p.flush()
        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            [
                {"user_id": "user-1", "user_properties": {"item1": "value1", "item2": 2}},
            ],
            {
                'events': [
                    {'user_id': 'user-2', 'event_type': 'event-1', 'event_properties': {'item1': 'value1', 'item2': 1}},
                    {'user_id': 'user-2', 'event_type': 'event-2', 'event_properties': {'item1': 'value2', 'item2': 2}}], 'api_key': 'My-Key'
            },
        ]

        p.flush()
        p.flush()

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            [
                {"user_id": "user-1", "user_properties": {"item1": "value1", "item2": 2}}
            ],
            {
                'events': [
                    {'user_id': 'user-2', 'event_type': 'event-1', 'event_properties': {'item1': 'value1', 'item2': 1}},
                    {'user_id': 'user-2', 'event_type': 'event-2', 'event_properties': {'item1': 'value2', 'item2': 2}}
                ],
                'api_key': 'My-Key'},
        ]

        p.track("user-2", Event('event-3', Properties(item1='value3', item2=3)))

        time.sleep(1.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            [
                {"user_id": "user-1", "user_properties": {"item1": "value1", "item2": 2}}
            ],
            {
                'events': [
                    {'user_id': 'user-2', 'event_type': 'event-1', 'event_properties': {'item1': 'value1', 'item2': 1}},
                    {'user_id': 'user-2', 'event_type': 'event-2', 'event_properties': {'item1': 'value2', 'item2': 2}}
                ],
                'api_key': 'My-Key'},
            {
                'events': [
                    {'user_id': 'user-2', 'event_type': 'event-3', 'event_properties': {'item1': 'value3', 'item2': 3}}
                ],
                'api_key': 'My-Key'},
        ]

        p.track("user-2", Event('event-4', Properties(item1='value4', item2=4)))
        p.track("user-1", Event('event-5', Properties(item1='value5', item2=5)))
    finally:
        p.shutdown()

        time.sleep(0.1)
        httpserver.stop()
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            [
                {"user_id": "user-1", "user_properties": {"item1": "value1", "item2": 2}}
            ],
            {
                'events': [
                    {'user_id': 'user-2', 'event_type': 'event-1', 'event_properties': {'item1': 'value1', 'item2': 1}},
                    {'user_id': 'user-2', 'event_type': 'event-2', 'event_properties': {'item1': 'value2', 'item2': 2}}
                ],
                'api_key': 'My-Key'},
            {
                'events': [
                    {'user_id': 'user-2', 'event_type': 'event-3', 'event_properties': {'item1': 'value3', 'item2': 3}}
                ],
                'api_key': 'My-Key'},
            {
                'events': [
                    {'user_id': 'user-2', 'event_type': 'event-4', 'event_properties': {'item1': 'value4', 'item2': 4}},
                    {'user_id': 'user-1', 'event_type': 'event-5', 'event_properties': {'item1': 'value5', 'item2': 5}}
                ],
                'api_key': 'My-Key'},
        ]


identification_re = re.compile(br'^identification=([^&]+)&')


def _get_cleaned_requests(httpserver: Any) -> List[Any]:
    requests = []
    for data in httpserver.collected_data:
        match = identification_re.search(data)
        if match:
            data = urllib.parse.unquote_plus(match.group(1).decode('ascii'))
        requests.append(json.loads(data))

    for request in requests:
        if 'events' in request:
            for event in request['events']:
                del event['time']
    return requests
