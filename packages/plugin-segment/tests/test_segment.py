import json

from itly.plugin_segment import SegmentPlugin, SegmentOptions
from itly.sdk import PluginLoadOptions, Environment, Properties, Event, Logger


def test_segment(httpserver):
    httpserver.expect_request('/v1/batch').respond_with_data()

    options = SegmentOptions(
        host=httpserver.url_for(''),
    )

    p = SegmentPlugin('My-Key', options)

    assert p.id() == 'segment'
    p.load(PluginLoadOptions(environment=Environment.DEVELOPMENT, logger=Logger.NONE))

    p.identify("user-1", Properties(item1='value1', item2=2))
    p.alias("user-1", "prev-user-1")
    p.track("user-2", Event('event-1', Properties(item1='value1', item2=1)))
    p.group("user-2", "group-2", Properties(item1='value2', item2=2))
    p.flush()
    p.page("user-2", "category-2", "page-3", Properties(item1='value3', item2=3))
    p.track("user-2", Event('event-4', Properties(item1='value4', item2=4)))
    p.track("user-1", Event('event-5', Properties(item1='value5', item2=5)))

    p.flush()
    p.shutdown()

    batches = [json.loads(data)['batch'] for data in httpserver.collected_data]
    requests = [_clean_request(r) for batch in batches for r in batch]
    assert requests == [
        {'anonymousId': None,
         'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}},
         'integrations': {},
         'traits': {'item1': 'value1', 'item2': 2},
         'type': 'identify',
         'userId': 'user-1'},
        {'anonymousId': None,
         'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}},
         'integrations': {},
         'previousId': 'prev-user-1',
         'type': 'alias',
         'userId': 'user-1'},
        {'anonymousId': None,
         'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}},
         'event': 'event-1',
         'integrations': {},
         'properties': {'item1': 'value1', 'item2': 1},
         'type': 'track',
         'userId': 'user-2'},
        {'anonymousId': None,
         'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}},
         'groupId': 'group-2',
         'integrations': {},
         'traits': {'item1': 'value2', 'item2': 2},
         'type': 'group',
         'userId': 'user-2'},
        {'anonymousId': None,
         'category': 'category-2',
         'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}},
         'integrations': {},
         'name': 'page-3',
         'properties': {'item1': 'value3', 'item2': 3},
         'type': 'page',
         'userId': 'user-2'},
        {'anonymousId': None,
         'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}},
         'event': 'event-4',
         'integrations': {},
         'properties': {'item1': 'value4', 'item2': 4},
         'type': 'track',
         'userId': 'user-2'},
        {'anonymousId': None,
         'context': {'library': {'name': 'analytics-python', 'version': '1.2.9'}},
         'event': 'event-5',
         'integrations': {},
         'properties': {'item1': 'value5', 'item2': 5},
         'type': 'track',
         'userId': 'user-1'}
    ]


def _clean_request(request):
    del request['messageId']
    del request['timestamp']
    return request
