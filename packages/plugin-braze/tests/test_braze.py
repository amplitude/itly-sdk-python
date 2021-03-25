import json
import re
import time
from datetime import timedelta
from typing import List, Any

from pytest_httpserver import HTTPServer

from itly_plugin_braze import BrazePlugin, BrazeOptions
from itly_sdk import PluginLoadOptions, Environment, Properties, Event, Logger

time_short = 0.1
timedelta_max = timedelta(seconds=999)
identify_properties = Properties(item1='identify', item2=2)
event_1 = Event('event-1', Properties(item1='value1', item2=1))
event_2 = Event('event-2', Properties(item1='value2', item2=2))
plugin_load_options = PluginLoadOptions(environment=Environment.DEVELOPMENT, logger=Logger.NONE)


def test_Id_BrazePlugin_IsBraze():
    p = BrazePlugin('My-Key', BrazeOptions(base_url=''))
    assert p.id() == 'braze'


def test_Identify_Immediate_Queued(httpserver: HTTPServer):
    httpserver.expect_request(re.compile('/users/track')).respond_with_data()
    p = BrazePlugin('My-Key',
                    BrazeOptions(base_url=httpserver.url_for(''), flush_queue_size=100, flush_interval=timedelta_max))
    p.load(plugin_load_options)
    p.identify("user-1", identify_properties)
    p.identify("user-2", identify_properties)
    p.identify("user-3", identify_properties)
    time.sleep(time_short)
    requests = _get_cleaned_requests(httpserver)
    assert requests == []
    p.shutdown()


def test_Track_Immediate_Queued(httpserver: HTTPServer):
    httpserver.expect_request(re.compile('/users/track')).respond_with_data()
    p = BrazePlugin('My-Key',
                    BrazeOptions(base_url=httpserver.url_for(''), flush_queue_size=100, flush_interval=timedelta_max))
    p.load(plugin_load_options)
    p.track("user-1", event_1)
    p.track("user-1", event_2)
    p.track("user-2", event_1)
    time.sleep(time_short)
    requests = _get_cleaned_requests(httpserver)
    assert requests == []
    p.shutdown()


def test_TrackAndIdentify_Immediate_Queued(httpserver: HTTPServer):
    httpserver.expect_request(re.compile('/users/track')).respond_with_data()
    p = BrazePlugin('My-Key',
                    BrazeOptions(base_url=httpserver.url_for(''), flush_queue_size=100, flush_interval=timedelta_max))
    p.load(plugin_load_options)
    p.track("user-1", event_1)
    p.identify("user-3", identify_properties)
    p.track("user-2", event_1)
    time.sleep(time_short)
    requests = _get_cleaned_requests(httpserver)
    assert requests == []
    p.shutdown()


def test_Identify_ExceedQueueSize_Flushed(httpserver: HTTPServer):
    httpserver.expect_request(re.compile('/users/track')).respond_with_data()
    p = BrazePlugin('My-Key',
                    BrazeOptions(base_url=httpserver.url_for(''), flush_queue_size=2, flush_interval=timedelta_max))
    p.load(plugin_load_options)
    p.identify("user-1", identify_properties)
    p.identify("user-2", identify_properties)
    time.sleep(time_short)
    requests = _get_cleaned_requests(httpserver)
    assert requests == [
        {
            'attributes': [
                {'external_id': 'user-1', 'item1': 'identify', 'item2': 2},
                {'external_id': 'user-2', 'item1': 'identify', 'item2': 2},
            ],
        },
    ]
    p.shutdown()


def test_Track_ExceedQueueSize_Flushed(httpserver: HTTPServer):
    httpserver.expect_request(re.compile('/users/track')).respond_with_data()
    p = BrazePlugin('My-Key',
                    BrazeOptions(base_url=httpserver.url_for(''), flush_queue_size=2, flush_interval=timedelta_max))
    p.load(plugin_load_options)
    p.track("user-1", event_1)
    p.track("user-2", event_2)
    time.sleep(time_short)
    requests = _get_cleaned_requests(httpserver)
    assert requests == [
        {
            'events': [
                {'external_id': 'user-1', 'name': 'event-1', 'properties': {'item1': 'value1', 'item2': 1}},
                {'external_id': 'user-2', 'name': 'event-2', 'properties': {'item1': 'value2', 'item2': 2}},
            ],
        },
    ]
    p.shutdown()


def test_TrackAndIdentify_ExceedQueueSize_Flushed(httpserver: HTTPServer):
    httpserver.expect_request(re.compile('/users/track')).respond_with_data()
    p = BrazePlugin('My-Key',
                    BrazeOptions(base_url=httpserver.url_for(''), flush_queue_size=3, flush_interval=timedelta_max))
    p.load(plugin_load_options)
    p.track("user-1", event_1)
    p.identify("user-1", identify_properties)
    p.track("user-2", event_2)
    time.sleep(time_short)
    requests = _get_cleaned_requests(httpserver)
    assert requests == [
        {
            'attributes': [
                {'external_id': 'user-1', 'item1': 'identify', 'item2': 2},
            ],
            'events': [
                {'external_id': 'user-1', 'name': 'event-1', 'properties': {'item1': 'value1', 'item2': 1}},
                {'external_id': 'user-2', 'name': 'event-2', 'properties': {'item1': 'value2', 'item2': 2}},
            ],
        },
    ]
    p.shutdown()


def test_Identify_ExceedFlushInterval_Flushed(httpserver: HTTPServer):
    httpserver.expect_request(re.compile('/users/track')).respond_with_data()
    flush_interval = timedelta(milliseconds=300)
    p = BrazePlugin('My-Key',
                    BrazeOptions(base_url=httpserver.url_for(''), flush_queue_size=100, flush_interval=flush_interval))
    p.load(plugin_load_options)
    p.identify("user-1", identify_properties)
    p.identify("user-2", identify_properties)
    time.sleep(flush_interval.total_seconds() + time_short)
    requests = _get_cleaned_requests(httpserver)
    assert requests == [
        {
            'attributes': [
                {'external_id': 'user-1', 'item1': 'identify', 'item2': 2},
                {'external_id': 'user-2', 'item1': 'identify', 'item2': 2},
            ],
        },
    ]
    p.shutdown()


def test_Track_ExceedFlushInterval_Flushed(httpserver: HTTPServer):
    httpserver.expect_request(re.compile('/users/track')).respond_with_data()
    flush_interval = timedelta(milliseconds=300)
    p = BrazePlugin('My-Key',
                    BrazeOptions(base_url=httpserver.url_for(''), flush_queue_size=100, flush_interval=flush_interval))
    p.load(plugin_load_options)
    p.track("user-1", event_1)
    p.track("user-2", event_2)
    time.sleep(flush_interval.total_seconds() + time_short)
    requests = _get_cleaned_requests(httpserver)
    assert requests == [
        {
            'events': [
                {'external_id': 'user-1', 'name': 'event-1', 'properties': {'item1': 'value1', 'item2': 1}},
                {'external_id': 'user-2', 'name': 'event-2', 'properties': {'item1': 'value2', 'item2': 2}},
            ],
        },
    ]
    p.shutdown()


def test_TrackAndIdentify_ExceedFlushInterval_Flushed(httpserver: HTTPServer):
    httpserver.expect_request(re.compile('/users/track')).respond_with_data()
    flush_interval = timedelta(milliseconds=300)
    p = BrazePlugin('My-Key',
                    BrazeOptions(base_url=httpserver.url_for(''), flush_queue_size=100, flush_interval=flush_interval))
    p.load(plugin_load_options)
    p.track("user-1", event_1)
    p.identify("user-1", identify_properties)
    p.track("user-2", event_2)
    time.sleep(flush_interval.total_seconds() + time_short)
    requests = _get_cleaned_requests(httpserver)
    assert requests == [
        {
            'attributes': [
                {'external_id': 'user-1', 'item1': 'identify', 'item2': 2},
            ],
            'events': [
                {'external_id': 'user-1', 'name': 'event-1', 'properties': {'item1': 'value1', 'item2': 1}},
                {'external_id': 'user-2', 'name': 'event-2', 'properties': {'item1': 'value2', 'item2': 2}},
            ],
        },
    ]
    p.shutdown()


def test_TrackAndIdentify_ExplicitFlush_Flushed(httpserver: HTTPServer):
    httpserver.expect_request(re.compile('/users/track')).respond_with_data()
    p = BrazePlugin('My-Key',
                    BrazeOptions(base_url=httpserver.url_for(''), flush_queue_size=100, flush_interval=timedelta_max))
    p.load(plugin_load_options)
    p.track("user-1", event_1)
    p.identify("user-1", identify_properties)
    p.track("user-2", event_2)
    p.flush()
    time.sleep(time_short)
    requests = _get_cleaned_requests(httpserver)
    assert requests == [
        {
            'attributes': [
                {'external_id': 'user-1', 'item1': 'identify', 'item2': 2},
            ],
            'events': [
                {'external_id': 'user-1', 'name': 'event-1', 'properties': {'item1': 'value1', 'item2': 1}},
                {'external_id': 'user-2', 'name': 'event-2', 'properties': {'item1': 'value2', 'item2': 2}},
            ],
        },
    ]
    p.shutdown()


def test_TrackAndIdentify_Shutdown_Flushed(httpserver: HTTPServer):
    httpserver.expect_request(re.compile('/users/track')).respond_with_data()
    p = BrazePlugin('My-Key',
                    BrazeOptions(base_url=httpserver.url_for(''), flush_queue_size=100, flush_interval=timedelta_max))
    p.load(plugin_load_options)
    p.track("user-1", event_1)
    p.identify("user-1", identify_properties)
    p.track("user-2", event_2)
    time.sleep(time_short)
    p.shutdown()
    requests = _get_cleaned_requests(httpserver)
    assert requests == [
        {
            'attributes': [
                {'external_id': 'user-1', 'item1': 'identify', 'item2': 2},
            ],
            'events': [
                {'external_id': 'user-1', 'name': 'event-1', 'properties': {'item1': 'value1', 'item2': 1}},
                {'external_id': 'user-2', 'name': 'event-2', 'properties': {'item1': 'value2', 'item2': 2}},
            ],
        },
    ]


def test_TrackAndIdentify_ObjectAndArrayProperties_Stringified(httpserver: HTTPServer):
    httpserver.expect_request(re.compile('/users/track')).respond_with_data()
    p = BrazePlugin('My-Key',
                    BrazeOptions(base_url=httpserver.url_for(''), flush_queue_size=100, flush_interval=timedelta_max))
    p.load(plugin_load_options)
    p.identify("user-1", Properties(item1=[11, 'value2'], item2={"a": True, "b": 17}))
    p.track("user-2", Event('event-1', Properties(item1=['value1', 'value2'], item2={"a": 1, "b": "test"})))
    p.flush()
    requests = _get_cleaned_requests(httpserver)
    assert requests == [
        {
            'attributes': [
                {'external_id': 'user-1', 'item1': '[11, "value2"]', 'item2': '{"a": true, "b": 17}'},
            ],
            'events': [
                {
                    'external_id': 'user-2', 'name': 'event-1',
                    'properties': {'item1': '["value1", "value2"]', 'item2': '{"a": 1, "b": "test"}'},
                },
            ],
        },
    ]
    p.shutdown()


def _get_cleaned_requests(httpserver: Any) -> List[Any]:
    requests = []
    for data in httpserver.collected_data:
        requests.append(json.loads(data))

    for request in requests:
        if 'events' in request:
            for event in request['events']:
                del event['time']

    return requests
