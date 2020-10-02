import base64
import json
import time
from typing import Any, List

from pytest_httpserver import HTTPServer

from itly_plugin_snowplow import SnowplowPlugin, SnowplowOptions
from itly_sdk import PluginLoadOptions, Environment, Properties, Event, Logger


def test_snowplow(httpserver: HTTPServer):
    httpserver.expect_request('/v1/batch').respond_with_data()

    endpoint = httpserver.url_for("").replace("http://", "")
    p = SnowplowPlugin("ly.iterative.test", SnowplowOptions(endpoint))

    assert p.id() == 'snowplow'
    p.load(PluginLoadOptions(environment=Environment.DEVELOPMENT, logger=Logger.NONE))

    p.page("user-1", "category-1", "page-1", Properties(item1='value0', item2=0))
    p.track("user-2", Event('event-1', Properties(item1='value1', item2=1), id_="event-1", version="0.0.1"))
    p.flush()
    p.page("user-2", "category-2", "page-3", Properties(item1='value3', item2=3))
    p.track("user-2", Event('event-4', Properties(item1='value4', item2=4), id_="event-4", version="0.0.4"))
    p.track("user-1", Event('event-5', Properties(item1='value5', item2=5), id_="event-5", version="0.0.5"))

    p.flush()
    p.shutdown()
    time.sleep(0.1)
    httpserver.stop()

    requests = _get_cleaned_requests(httpserver)
    assert requests == [
        [
            {
                'properties': {
                    'data': {
                        'data': {'name': 'page-1'},
                        'schema': 'iglu:com.snowplowanalytics.snowplow/screen_view/jsonschema/1-0-0'},
                    'schema': 'iglu:com.snowplowanalytics.snowplow/unstruct_event/jsonschema/1-0-0'
                },
                'uid': 'user-1'
            },
            {
                'properties': {
                    'data': {
                        'data': {'item1': 'value1', 'item2': 1},
                        'schema': 'iglu:ly.iterative.test/event-1/jsonschema/0-0-1'
                    },
                    'schema': 'iglu:com.snowplowanalytics.snowplow/unstruct_event/jsonschema/1-0-0'
                },
                'uid': 'user-2'
            }
        ],
        [
            {
                'properties': {
                    'data': {
                        'data': {'name': 'page-3'},
                        'schema': 'iglu:com.snowplowanalytics.snowplow/screen_view/jsonschema/1-0-0'
                    },
                    'schema': 'iglu:com.snowplowanalytics.snowplow/unstruct_event/jsonschema/1-0-0'
                },
                'uid': 'user-2'
            },
            {
                'properties': {
                    'data': {
                        'data': {'item1': 'value4', 'item2': 4},
                        'schema': 'iglu:ly.iterative.test/event-4/jsonschema/0-0-4'
                    },
                    'schema': 'iglu:com.snowplowanalytics.snowplow/unstruct_event/jsonschema/1-0-0'
                },
                'uid': 'user-2'
            },
            {
                'properties': {
                        'data': {
                             'data': {'item1': 'value5', 'item2': 5},
                             'schema': 'iglu:ly.iterative.test/event-5/jsonschema/0-0-5'
                        },
                        'schema': 'iglu:com.snowplowanalytics.snowplow/unstruct_event/jsonschema/1-0-0'
                },
                'uid': 'user-1'
            }
        ]
    ]


def _get_cleaned_requests(httpserver: Any) -> List[Any]:
    batches = [json.loads(data) for data in httpserver.collected_data]
    return [_clean_batch(batch) for batch in batches]


def _clean_batch(batch: Any) -> Any:
    return [{"uid": r["uid"], "properties": json.loads(base64.decodebytes(r["ue_px"].encode("ascii")))} for r in batch['data']]
