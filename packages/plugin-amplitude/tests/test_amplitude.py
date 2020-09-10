import time
from typing import List

from itly.plugin_amplitude import AmplitudePlugin, AmplitudeOptions
from itly.plugin_amplitude._amplitude_client import Request
from itly.sdk import PluginLoadOptions, Environment, Properties, Event, Logger


def test_amplitude():
    requests = []
    options = AmplitudeOptions(
        flush_queue_size=3,
        flush_interval_ms=1000,
    )
    p = AmplitudePlugin('My-Key', options)
    p._send_request = lambda request: requests.append(request)

    assert p.id() == 'amplitude'
    try:
        p.load(PluginLoadOptions(environment=Environment.DEVELOPMENT, logger=Logger.NONE))

        p.identify("user-1", Properties(item1='value1', item2=2))
        time.sleep(0.1)
        _clean_requests(requests)
        assert requests == []

        p.track("user-2", Event('event-1', Properties(item1='value1', item2=1)))
        time.sleep(0.1)
        _clean_requests(requests)
        assert requests == [
            Request('https://api.amplitude.com/identify', False, {
                'identification': '[{"user_id": "user-1", "user_properties": {"item1": "value1", "item2": 2}}]', 'api_key': 'My-Key'
            }),
        ]

        p.track("user-2", Event('event-2', Properties(item1='value2', item2=2)))
        time.sleep(0.1)
        _clean_requests(requests)
        assert requests == [
            Request('https://api.amplitude.com/identify', False, {
                'identification': '[{"user_id": "user-1", "user_properties": {"item1": "value1", "item2": 2}}]', 'api_key': 'My-Key'
            }),
        ]

        p.flush()
        time.sleep(0.1)
        _clean_requests(requests)
        assert requests == [
            Request('https://api.amplitude.com/identify', False, {
                'identification': '[{"user_id": "user-1", "user_properties": {"item1": "value1", "item2": 2}}]', 'api_key': 'My-Key'
            }),
            Request('https://api.amplitude.com/2/httpapi', True, {
                'events': [
                    {'user_id': 'user-2', 'event_type': 'event-1', 'event_properties': {'item1': 'value1', 'item2': 1}},
                    {'user_id': 'user-2', 'event_type': 'event-2', 'event_properties': {'item1': 'value2', 'item2': 2}}], 'api_key': 'My-Key'
            }),
        ]

        p.flush()
        p.flush()

        time.sleep(0.1)
        _clean_requests(requests)
        assert requests == [
            Request('https://api.amplitude.com/identify', False, {
                'identification': '[{"user_id": "user-1", "user_properties": {"item1": "value1", "item2": 2}}]', 'api_key': 'My-Key'
            }),
            Request('https://api.amplitude.com/2/httpapi', True, {
                'events': [
                    {'user_id': 'user-2', 'event_type': 'event-1', 'event_properties': {'item1': 'value1', 'item2': 1}},
                    {'user_id': 'user-2', 'event_type': 'event-2', 'event_properties': {'item1': 'value2', 'item2': 2}}
                ],
                'api_key': 'My-Key'}),
        ]

        p.track("user-2", Event('event-3', Properties(item1='value3', item2=3)))

        time.sleep(1.1)
        _clean_requests(requests)
        assert requests == [
            Request('https://api.amplitude.com/identify', False, {
                'identification': '[{"user_id": "user-1", "user_properties": {"item1": "value1", "item2": 2}}]', 'api_key': 'My-Key'
            }),
            Request('https://api.amplitude.com/2/httpapi', True, {
                'events': [
                    {'user_id': 'user-2', 'event_type': 'event-1', 'event_properties': {'item1': 'value1', 'item2': 1}},
                    {'user_id': 'user-2', 'event_type': 'event-2', 'event_properties': {'item1': 'value2', 'item2': 2}}
                ],
                'api_key': 'My-Key'}),
            Request('https://api.amplitude.com/2/httpapi', True, {
                'events': [
                    {'user_id': 'user-2', 'event_type': 'event-3', 'event_properties': {'item1': 'value3', 'item2': 3}}
                ],
                'api_key': 'My-Key'}),
        ]

        p.track("user-2", Event('event-4', Properties(item1='value4', item2=4)))
        p.track("user-1", Event('event-5', Properties(item1='value5', item2=5)))
    finally:
        p.shutdown()

        time.sleep(0.1)
        _clean_requests(requests)
        assert requests == [
            Request('https://api.amplitude.com/identify', False, {
                'identification': '[{"user_id": "user-1", "user_properties": {"item1": "value1", "item2": 2}}]', 'api_key': 'My-Key'}),
            Request('https://api.amplitude.com/2/httpapi', True, {
                'events': [
                    {'user_id': 'user-2', 'event_type': 'event-1', 'event_properties': {'item1': 'value1', 'item2': 1}},
                    {'user_id': 'user-2', 'event_type': 'event-2', 'event_properties': {'item1': 'value2', 'item2': 2}}
                ],
                'api_key': 'My-Key'}),
            Request('https://api.amplitude.com/2/httpapi', True, {
                'events': [
                    {'user_id': 'user-2', 'event_type': 'event-3', 'event_properties': {'item1': 'value3', 'item2': 3}}
                ],
                'api_key': 'My-Key'}),
            Request('https://api.amplitude.com/2/httpapi', True, {
                'events': [
                    {'user_id': 'user-2', 'event_type': 'event-4', 'event_properties': {'item1': 'value4', 'item2': 4}},
                    {'user_id': 'user-1', 'event_type': 'event-5', 'event_properties': {'item1': 'value5', 'item2': 5}}
                ],
                'api_key': 'My-Key'}),
        ]


def _clean_requests(requests: List[Request]) -> None:
    for request in requests:
        if 'events' in request.data:
            for event in request.data['events']:
                if 'time' in event:
                    del event['time']
