import time

from itly.plugin_segment import SegmentPlugin, SegmentOptions
from itly.plugin_segment._segment_client import Request
from itly.sdk import PluginLoadOptions, Environment, Properties, Event, Logger


def test_segment():
    requests = []
    options = SegmentOptions(
        flush_queue_size=3,
        flush_interval_ms=1000,
    )
    p = SegmentPlugin('My-Key', options)
    p._send_request = lambda request: requests.append(request)

    assert p.id() == 'segment'
    try:
        p.load(PluginLoadOptions(environment=Environment.DEVELOPMENT, logger=Logger.NONE))

        p.identify("user-1", Properties(item1='value1', item2=2))

        time.sleep(0.1)
        assert requests == []
        p.alias("user-1", "prev-user-1")

        time.sleep(0.1)
        assert requests == []

        p.track("user-2", Event('event-1', Properties(item1='value1', item2=1)))
        time.sleep(0.1)

        _clean_requests(requests)
        assert requests == [
            Request(data=[
                {'integrations': {}, 'anonymousId': None, 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}}, 'type': 'identify',
                 'userId': 'user-1', 'traits': {'item1': 'value1', 'item2': 2}},
                {'integrations': {}, 'previousId': 'prev-user-1', 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}},
                 'userId': 'user-1', 'type': 'alias', 'anonymousId': None},
                {'integrations': {}, 'anonymousId': None, 'properties': {'item1': 'value1', 'item2': 1}, 
                 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}}, 'userId': 'user-2', 'type': 'track', 'event': 'event-1'}
            ]),
        ]

        p.group("user-2", "group-2", Properties(item1='value2', item2=2))
        time.sleep(0.1)

        _clean_requests(requests)
        assert requests == [
            Request(data=[
                {'integrations': {}, 'anonymousId': None, 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}}, 'type': 'identify',
                 'userId': 'user-1', 'traits': {'item1': 'value1', 'item2': 2}},
                {'integrations': {}, 'previousId': 'prev-user-1', 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}},
                 'userId': 'user-1', 'type': 'alias', 'anonymousId': None},
                {'integrations': {}, 'anonymousId': None, 'properties': {'item1': 'value1', 'item2': 1}, 
                 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}}, 'userId': 'user-2', 'type': 'track', 'event': 'event-1'}
            ]),
        ]

        p.flush()
        time.sleep(0.1)

        _clean_requests(requests)
        assert requests == [
            Request(data=[
                {'integrations': {}, 'anonymousId': None, 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}}, 'type': 'identify',
                 'userId': 'user-1', 'traits': {'item1': 'value1', 'item2': 2}},
                {'integrations': {}, 'previousId': 'prev-user-1', 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}},
                 'userId': 'user-1', 'type': 'alias', 'anonymousId': None},
                {'integrations': {}, 'anonymousId': None, 'properties': {'item1': 'value1', 'item2': 1}, 
                 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}}, 'userId': 'user-2', 'type': 'track', 'event': 'event-1'}
            ]),
            Request(data=[
                {'integrations': {}, 'anonymousId': None, 'groupId': 'group-2', 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}},
                 'userId': 'user-2', 'traits': {'item1': 'value2', 'item2': 2}, 'type': 'group'}
            ]),
        ]

        p.flush()
        p.flush()

        time.sleep(0.1)
        _clean_requests(requests)
        assert requests == [
            Request(data=[
                {'integrations': {}, 'anonymousId': None, 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}}, 'type': 'identify',
                 'userId': 'user-1', 'traits': {'item1': 'value1', 'item2': 2}},
                {'integrations': {}, 'previousId': 'prev-user-1', 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}},
                 'userId': 'user-1', 'type': 'alias', 'anonymousId': None},
                {'integrations': {}, 'anonymousId': None, 'properties': {'item1': 'value1', 'item2': 1}, 
                 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}}, 'userId': 'user-2', 'type': 'track', 'event': 'event-1'}
            ]),
            Request(data=[
                {'integrations': {}, 'anonymousId': None, 'groupId': 'group-2', 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}},
                 'userId': 'user-2', 'traits': {'item1': 'value2', 'item2': 2}, 'type': 'group'}
            ]),
        ]

        p.page("user-2", "category-2", "page-3", Properties(item1='value3', item2=3))

        time.sleep(1.1)
        _clean_requests(requests)
        assert requests == [
            Request(data=[
                {'integrations': {}, 'anonymousId': None, 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}}, 'type': 'identify',
                 'userId': 'user-1', 'traits': {'item1': 'value1', 'item2': 2}},
                {'integrations': {}, 'previousId': 'prev-user-1', 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}},
                 'userId': 'user-1', 'type': 'alias', 'anonymousId': None},
                {'integrations': {}, 'anonymousId': None, 'properties': {'item1': 'value1', 'item2': 1}, 
                 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}}, 'userId': 'user-2', 'type': 'track', 'event': 'event-1'}
            ]),
            Request(data=[
                {'integrations': {}, 'anonymousId': None, 'groupId': 'group-2', 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}},
                 'userId': 'user-2', 'traits': {'item1': 'value2', 'item2': 2}, 'type': 'group'}
            ]),
            Request(data=[{'integrations': {}, 'anonymousId': None, 'properties': {'item1': 'value3', 'item2': 3}, 'category': 'category-2',
                           'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}}, 'userId': 'user-2', 'type': 'page', 'name': 'page-3'}
                          ]),
        ]

        p.track("user-2", Event('event-4', Properties(item1='value4', item2=4)))
        p.track("user-1", Event('event-5', Properties(item1='value5', item2=5)))
    finally:
        p.shutdown()

        time.sleep(0.1)
        _clean_requests(requests)
        assert requests == [
            Request(data=[
                {'integrations': {}, 'anonymousId': None, 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}}, 'type': 'identify',
                 'userId': 'user-1', 'traits': {'item1': 'value1', 'item2': 2}},
                {'integrations': {}, 'previousId': 'prev-user-1', 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}},
                 'userId': 'user-1', 'type': 'alias', 'anonymousId': None},
                {'integrations': {}, 'anonymousId': None, 'properties': {'item1': 'value1', 'item2': 1}, 
                 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}}, 'userId': 'user-2', 'type': 'track', 'event': 'event-1'}
            ]),
            Request(data=[
                {'integrations': {}, 'anonymousId': None, 'groupId': 'group-2', 'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}},
                 'userId': 'user-2', 'traits': {'item1': 'value2', 'item2': 2}, 'type': 'group'}]),
            Request(data=[{'integrations': {}, 'anonymousId': None, 'properties': {'item1': 'value3', 'item2': 3}, 'category': 'category-2',
                           'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}}, 'userId': 'user-2', 'type': 'page', 'name': 'page-3'}
                          ]),
            Request(data=[{'integrations': {}, 'anonymousId': None, 'properties': {'item1': 'value4', 'item2': 4}, 
                           'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}}, 'userId': 'user-2', 'type': 'track', 'event': 'event-4'},
                          {'integrations': {}, 'anonymousId': None, 'properties': {'item1': 'value5', 'item2': 5}, 
                           'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}}, 'userId': 'user-1', 'type': 'track', 'event': 'event-5'}
                          ]),
        ]


def _clean_requests(requests):
    for request in requests:
        for item in request.data:
            if 'messageId' in item:
                del item['messageId']
            if 'timestamp' in item:
                del item['timestamp']
