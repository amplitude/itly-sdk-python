import base64
import json
import re
import time
import urllib.parse
from typing import Any, List

from pytest_httpserver import HTTPServer

from itly.plugin_mixpanel import MixpanelPlugin, MixpanelOptions
from itly.sdk import PluginLoadOptions, Environment, Properties, Event, Logger


def test_mixpanel(httpserver: HTTPServer):
    httpserver.expect_request(re.compile('/(track|engage)')).respond_with_json({'status': 1})

    options = MixpanelOptions(
        api_host=httpserver.url_for('').rstrip('/'),
    )
    p = MixpanelPlugin('My-Key', options)

    assert p.id() == 'mixpanel'
    p.load(PluginLoadOptions(environment=Environment.DEVELOPMENT, logger=Logger.NONE))
    p.identify("user-1", Properties(item1='value1', item2=2))
    p.alias("user-1", "prev-user-1")
    p.track("user-2", Event('event-1', Properties(item1='value1', item2=1)))
    p.track("user-2", Event('event-2', Properties(item1='value2', item2=2)))
    p.flush()
    p.track("user-2", Event('event-3', Properties(item1='value3', item2=3)))
    p.track("user-2", Event('event-4', Properties(item1='value4', item2=4)))
    p.track("user-1", Event('event-5', Properties(item1='value5', item2=5)))
    p.shutdown()

    time.sleep(0.1)
    requests = _get_cleaned_requests(httpserver)
    httpserver.stop()

    assert requests == [
        {'event': 'event-1',
         'properties': {'$lib_version': '4.6.0',
                        'distinct_id': 'user-2',
                        'item1': 'value1',
                        'item2': 1,
                        'mp_lib': 'python',
                        'token': 'My-Key'}},
        {'event': 'event-2',
         'properties': {'$lib_version': '4.6.0',
                        'distinct_id': 'user-2',
                        'item1': 'value2',
                        'item2': 2,
                        'mp_lib': 'python',
                        'token': 'My-Key'}},
        {'$distinct_id': 'user-1',
         '$set': {'item1': 'value1', 'item2': 2},
         '$token': 'My-Key'},
        {'event': 'event-3',
         'properties': {'$lib_version': '4.6.0',
                        'distinct_id': 'user-2',
                        'item1': 'value3',
                        'item2': 3,
                        'mp_lib': 'python',
                        'token': 'My-Key'}},
        {'event': 'event-4',
         'properties': {'$lib_version': '4.6.0',
                        'distinct_id': 'user-2',
                        'item1': 'value4',
                        'item2': 4,
                        'mp_lib': 'python',
                        'token': 'My-Key'}},
        {'event': 'event-5',
         'properties': {'$lib_version': '4.6.0',
                        'distinct_id': 'user-1',
                        'item1': 'value5',
                        'item2': 5,
                        'mp_lib': 'python',
                        'token': 'My-Key'}}
    ]


def _get_cleaned_requests(httpserver: Any) -> List[Any]:
    requests = []
    for item in httpserver.collected_data:
        data = re.search(b'data=([^&]+)&', item)
        batch = json.loads(base64.b64decode(urllib.parse.unquote(data.group(1).decode('ascii'))))
        requests += [_clean_request(r) for r in batch]
    return requests


def _clean_request(request: Any) -> Any:
    if '$time' in request:
        del request['$time']
    if 'properties' in request and 'time' in request['properties']:
        del request['properties']['time']
    return request
