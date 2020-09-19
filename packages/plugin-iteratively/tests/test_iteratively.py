import json
import re
import time
from datetime import timedelta
from typing import List, Any

from pytest_httpserver import HTTPServer

from itly.plugin_iteratively import IterativelyPlugin, IterativelyOptions, IterativelyRetryOptions
from itly.sdk import PluginLoadOptions, Environment, Properties, Event, Logger, ValidationResponse


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


def test_iteratively(httpserver: HTTPServer):
    httpserver.expect_request(re.compile('/track')).respond_with_data()

    options = IterativelyOptions(
        url=httpserver.url_for('/track'),
        omit_values=False,
        flush_queue_size=3,
        flush_interval=timedelta(seconds=1),
    )
    p = IterativelyPlugin('My-Key', options)

    assert p.id() == 'iteratively'
    try:
        p.load(PluginLoadOptions(environment=Environment.DEVELOPMENT, logger=Logger.NONE))

        p.post_identify("user-1", Properties(item1='value1', item2=2),
                        [
                            ValidationResponse(valid=True, plugin_id='custom', message=''),
                            ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
                        ])

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == []
        p.post_identify("user-2", Properties(item1='value3', item2=4), [])

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == []

        p.post_track("user-2", Event('event-1', Properties(item1='value1', item2=1)),
                     [
                         ValidationResponse(valid=False, plugin_id='custom', message='not valid!!!'),
                         ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
                     ])

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {'objects': [
                {'type': 'identify', 'properties': {'item1': 'value1', 'item2': 2}, 'valid': False, 'validation': {'details': 'invalid!!!'}},
                {'type': 'identify', 'properties': {'item1': 'value3', 'item2': 4}, 'valid': True, 'validation': {'details': ''}},
                {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'not valid!!!'}, 'eventName': 'event-1'}
            ]},
        ]

        p.post_group("user-2", "group-2", Properties(item1='value2', item2=2), [])

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {'objects': [
                {'type': 'identify', 'properties': {'item1': 'value1', 'item2': 2}, 'valid': False, 'validation': {'details': 'invalid!!!'}},
                {'type': 'identify', 'properties': {'item1': 'value3', 'item2': 4}, 'valid': True, 'validation': {'details': ''}},
                {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'not valid!!!'}, 'eventName': 'event-1'}
            ]},
        ]

        p.flush()

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {'objects': [
                {'type': 'identify', 'properties': {'item1': 'value1', 'item2': 2}, 'valid': False, 'validation': {'details': 'invalid!!!'}},
                {'type': 'identify', 'properties': {'item1': 'value3', 'item2': 4}, 'valid': True, 'validation': {'details': ''}},
                {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'not valid!!!'}, 'eventName': 'event-1'}
            ]},
            {'objects': [
                {'type': 'group', 'properties': {'item1': 'value2', 'item2': 2}, 'valid': True, 'validation': {'details': ''}}
            ]},
        ]

        p.flush()
        p.flush()

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {'objects': [
                {'type': 'identify', 'properties': {'item1': 'value1', 'item2': 2}, 'valid': False, 'validation': {'details': 'invalid!!!'}},
                {'type': 'identify', 'properties': {'item1': 'value3', 'item2': 4}, 'valid': True, 'validation': {'details': ''}},
                {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'not valid!!!'}, 'eventName': 'event-1'}
            ]},
            {'objects': [
                {'type': 'group', 'properties': {'item1': 'value2', 'item2': 2}, 'valid': True, 'validation': {'details': ''}}
            ]},
        ]

        p.post_page("user-2", "category-2", "page-3", Properties(item1='value3', item2=3),
                    [
                        ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
                        ValidationResponse(valid=True, plugin_id='custom', message=''),
                    ])

        time.sleep(1.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {'objects': [
                {'type': 'identify', 'properties': {'item1': 'value1', 'item2': 2}, 'valid': False, 'validation': {'details': 'invalid!!!'}},
                {'type': 'identify', 'properties': {'item1': 'value3', 'item2': 4}, 'valid': True, 'validation': {'details': ''}},
                {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'not valid!!!'}, 'eventName': 'event-1'}
            ]},
            {'objects': [
                {'type': 'group', 'properties': {'item1': 'value2', 'item2': 2}, 'valid': True, 'validation': {'details': ''}}
            ]},
            {'objects': [
                {'type': 'page', 'properties': {'item1': 'value3', 'item2': 3}, 'valid': False, 'validation': {'details': 'invalid!!!'}}
            ]},
        ]

        p.post_track("user-1", Event('event-5', Properties(item1='value5', item2=5), id_='id-5', version='version-5'), [])
    finally:
        p.shutdown()

        time.sleep(0.1)
        httpserver.stop()
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {'objects': [
                {'type': 'identify', 'properties': {'item1': 'value1', 'item2': 2}, 'valid': False, 'validation': {'details': 'invalid!!!'}},
                {'type': 'identify', 'properties': {'item1': 'value3', 'item2': 4}, 'valid': True, 'validation': {'details': ''}},
                {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'not valid!!!'}, 'eventName': 'event-1'}
            ]},
            {'objects': [
                {'type': 'group', 'properties': {'item1': 'value2', 'item2': 2}, 'valid': True, 'validation': {'details': ''}}
            ]},
            {'objects': [
                {'type': 'page', 'properties': {'item1': 'value3', 'item2': 3}, 'valid': False, 'validation': {'details': 'invalid!!!'}}
            ]},
            {'objects': [
                {'type': 'track', 'properties': {'item1': 'value5', 'item2': 5}, 'valid': True, 'validation': {'details': ''}, 'eventName': 'event-5', 'eventId': 'id-5',
                 'eventSchemaVersion': 'version-5'}
            ]},
        ]


def test_iteratively_omit_values(httpserver: HTTPServer):
    httpserver.expect_request(re.compile('/track')).respond_with_data()

    options = IterativelyOptions(
        url=httpserver.url_for('/track'),
        omit_values=True,
        flush_queue_size=3,
        flush_interval=timedelta(seconds=1),
    )
    p = IterativelyPlugin('My-Key', options)

    assert p.id() == 'iteratively'
    try:
        p.load(PluginLoadOptions(environment=Environment.DEVELOPMENT, logger=Logger.NONE))

        p.post_identify("user-1", Properties(item1='value1', item2=2), [])

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == []
        p.post_identify("user-2", Properties(item1='value3', item2=4),
                        [
                            ValidationResponse(valid=True, plugin_id='custom', message=''),
                            ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
                        ])

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == []

        p.post_track("user-2", Event('event-1', Properties(item1='value1', item2=1)), [])

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {'objects': [
                {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}},
                {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}},
                {'type': 'track', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}, 'eventName': 'event-1'}
            ]},
        ]

        p.post_group("user-2", "group-2", Properties(item1='value2', item2=2),
                     [
                         ValidationResponse(valid=False, plugin_id='custom', message='not valid!!!'),
                         ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
                     ])

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {'objects': [
                {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}},
                {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}},
                {'type': 'track', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}, 'eventName': 'event-1'}
            ]},
        ]

        p.flush()

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {'objects': [
                {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}},
                {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}},
                {'type': 'track', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}, 'eventName': 'event-1'}
            ]},
            {'objects': [
                {'type': 'group', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}}
            ]},
        ]

        p.flush()
        p.flush()

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {'objects': [
                {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}},
                {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}},
                {'type': 'track', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}, 'eventName': 'event-1'}
            ]},
            {'objects': [
                {'type': 'group', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}}
            ]},
        ]

        p.post_page("user-2", "category-2", "page-3", Properties(item1='value3', item2=3), [])

        time.sleep(1.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {'objects': [
                {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}},
                {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}},
                {'type': 'track', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}, 'eventName': 'event-1'}
            ]},
            {'objects': [
                {'type': 'group', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}}
            ]},
            {'objects': [
                {'type': 'page', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}}
            ]},
        ]

        p.post_track("user-1", Event('event-5', Properties(item1='value5', item2=5), id_='id-5', version='version-5'),
                     [
                         ValidationResponse(valid=True, plugin_id='custom', message=''),
                         ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
                     ])
    finally:
        p.shutdown()

        time.sleep(0.1)
        httpserver.stop()
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {'objects': [
                {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}},
                {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}},
                {'type': 'track', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}, 'eventName': 'event-1'}
            ]},
            {'objects': [
                {'type': 'group', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}}
            ]},
            {'objects': [
                {'type': 'page', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}}
            ]},
            {'objects': [
                {'type': 'track', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}, 'eventName': 'event-5', 'eventId': 'id-5',
                 'eventSchemaVersion': 'version-5'}
            ]},
        ]


def test_iteratively_disabled(httpserver: HTTPServer):
    httpserver.expect_request(re.compile('/track')).respond_with_data()

    options = IterativelyOptions(
        url=httpserver.url_for('/track'),
        disabled=True,
        flush_queue_size=3,
        flush_interval=timedelta(seconds=1),
    )
    p = IterativelyPlugin('My-Key', options)

    assert p.id() == 'iteratively'
    try:
        p.load(PluginLoadOptions(environment=Environment.DEVELOPMENT, logger=Logger.NONE))

        p.post_identify("user-1", Properties(item1='value1', item2=2), [])

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == []
        p.post_identify("user-2", Properties(item1='value3', item2=4), [])

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == []

        p.post_track("user-2", Event('event-1', Properties(item1='value1', item2=1)),
                     [
                         ValidationResponse(valid=True, plugin_id='custom', message=''),
                         ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
                     ])

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == []

        p.post_group("user-2", "group-2", Properties(item1='value2', item2=2), [])

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == []

        p.flush()

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == []

        p.flush()
        p.flush()

        time.sleep(0.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == []

        p.post_page("user-2", "category-2", "page-3", Properties(item1='value3', item2=3), [])

        time.sleep(1.1)
        requests = _get_cleaned_requests(httpserver)
        assert requests == []

        p.post_track("user-1", Event('event-5', Properties(item1='value5', item2=5), id_='id-5', version='version-5'), [])
    finally:
        p.shutdown()

        time.sleep(0.1)
        httpserver.stop()
        requests = _get_cleaned_requests(httpserver)
        assert requests == []


def test_iteratively_retry(httpserver: HTTPServer):
    options = IterativelyOptions(
        url=httpserver.url_for('/track'),
        flush_queue_size=3,
        flush_interval=timedelta(seconds=1),
        retry_options=IterativelyRetryOptions(max_retries=3, delay_initial=timedelta(seconds=0.1), delay_maximum=timedelta(seconds=0.5)),
    )
    logger = CustomLogger()
    p = IterativelyPlugin('My-Key', options)
    try:
        p.load(PluginLoadOptions(environment=Environment.DEVELOPMENT, logger=logger))

        httpserver.expect_oneshot_request(re.compile('/track')).respond_with_data(status=429)
        httpserver.expect_oneshot_request(re.compile('/track')).respond_with_data(status=501)
        httpserver.expect_oneshot_request(re.compile('/track')).respond_with_data()
        p.post_track("user-2", Event('event-1', Properties(item1='value1', item2=1)),
                     [
                         ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
                     ])
        p.flush()
        time.sleep(2)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {'objects': [
                {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'invalid!!!'}, 'eventName': 'event-1'}
            ]},
            {'objects': [
                {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'invalid!!!'}, 'eventName': 'event-1'}
            ]},
            {'objects': [
                {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'invalid!!!'}, 'eventName': 'event-1'}
            ]},
        ]
        assert logger.log_lines == []

        httpserver.expect_oneshot_request(re.compile('/track')).respond_with_data(status=429)
        httpserver.expect_oneshot_request(re.compile('/track')).respond_with_data(status=501)
        httpserver.expect_oneshot_request(re.compile('/track')).respond_with_data(status=504)
        httpserver.expect_oneshot_request(re.compile('/track')).respond_with_data()
        p.post_track("user-2", Event('event-1', Properties(item1='value1', item2=1)),
                     [
                         ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
                     ])
        p.flush()
        time.sleep(2)
        requests = _get_cleaned_requests(httpserver)
        assert requests == [
            {'objects': [
                {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'invalid!!!'}, 'eventName': 'event-1'}
            ]},
            {'objects': [
                {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'invalid!!!'}, 'eventName': 'event-1'}
            ]},
            {'objects': [
                {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'invalid!!!'}, 'eventName': 'event-1'}
            ]},
            {'objects': [
                {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'invalid!!!'}, 'eventName': 'event-1'}
            ]},
            {'objects': [
                {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'invalid!!!'}, 'eventName': 'event-1'}
            ]},
            {'objects': [
                {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'invalid!!!'}, 'eventName': 'event-1'}
            ]},
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
