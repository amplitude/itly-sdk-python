import json
import re
import time
from datetime import timedelta
from typing import List, Any
import urllib.parse

from pytest_httpserver import HTTPServer

from itly_plugin_braze import BrazePlugin, BrazeOptions
from itly_sdk import PluginLoadOptions, Environment, Properties, Event, Logger


def test_braze(httpserver: HTTPServer):
    httpserver.expect_request(re.compile('/users/track')).respond_with_data()

    options = BrazeOptions(
        base_url=httpserver.url_for(''),
        flush_queue_size=3,
        flush_interval=timedelta(seconds=1),
    )
    p = BrazePlugin('My-Key', options)

    assert p.id() == 'braze'
    try:
        p.load(PluginLoadOptions(environment=Environment.DEVELOPMENT, logger=Logger.NONE))

        p.identify("user-1", Properties(item1='value1', item2=2))
        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == []

        p.track("user-2", Event('event-1', Properties(item1='value1', item2=1)))
        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == []

        p.track("user-2", Event('event-2', Properties(item1='value2', item2=2)))
        time.sleep(0.8)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {
                'attributes': [{'external_id': 'user-1', 'item1': 'value1', 'item2': 2}],
                'events': [
                    {'external_id': 'user-2', 'item1': 'value1', 'item2': 1, 'name': 'event-1', },
                    {'external_id': 'user-2', 'item1': 'value2', 'item2': 2, 'name': 'event-2', },
                ],
            }
        ]

        p.flush()
        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {
                'attributes': [{'external_id': 'user-1', 'item1': 'value1', 'item2': 2}],
                'events': [
                    {'external_id': 'user-2', 'item1': 'value1', 'item2': 1, 'name': 'event-1', },
                    {'external_id': 'user-2', 'item1': 'value2', 'item2': 2, 'name': 'event-2', },
                ],
            }
        ]

        p.flush()
        p.flush()

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {
                'attributes': [{'external_id': 'user-1', 'item1': 'value1', 'item2': 2}],
                'events': [
                    {'external_id': 'user-2', 'item1': 'value1', 'item2': 1, 'name': 'event-1', },
                    {'external_id': 'user-2', 'item1': 'value2', 'item2': 2, 'name': 'event-2', },
                ],
            }
        ]

        p.track("user-2", Event('event-3', Properties(item1='value3', item2=3)))

        time.sleep(1.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {
                'attributes': [{'external_id': 'user-1', 'item1': 'value1', 'item2': 2}],
                'events': [
                    {'external_id': 'user-2', 'item1': 'value1', 'item2': 1, 'name': 'event-1', },
                    {'external_id': 'user-2', 'item1': 'value2', 'item2': 2, 'name': 'event-2', },
                ],
            },
            {
                'events': [
                    {'external_id': 'user-2', 'item1': 'value3', 'item2': 3, 'name': 'event-3', }
                ],
            }
        ]
        p.track("user-2", Event('event-4', Properties(item1='value4', item2=[4])))
        p.track("user-1", Event('event-5', Properties(item1='value5', item2={'key':5})))
    finally:
        p.shutdown()

        time.sleep(0.1)
        httpserver.stop()
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {
                'attributes': [{'external_id': 'user-1', 'item1': 'value1', 'item2': 2}],
                'events': [
                    {'external_id': 'user-2', 'item1': 'value1', 'item2': 1, 'name': 'event-1', },
                    {'external_id': 'user-2', 'item1': 'value2', 'item2': 2, 'name': 'event-2', },
                ],
            },
            {
                'events': [
                    {'external_id': 'user-2', 'item1': 'value3', 'item2': 3, 'name': 'event-3', }
                ],
            },
            {
                'events': [
                    {'external_id': 'user-2', 'item1': 'value4', 'item2': '[4]', 'name': 'event-4', },
                    {'external_id': 'user-1', 'item1': 'value5', 'item2': '{"key": 5}', 'name': 'event-5', },
                ],
            }
        ]


def _get_cleaned_requests(httpserver: Any) -> List[Any]:
    requests = []
    for data in httpserver.collected_data:
        requests.append(json.loads(data))

    for request in requests:
        if 'events' in request:
            for event in request['events']:
                del event['time']

    return requests
