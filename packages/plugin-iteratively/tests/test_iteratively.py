import time
import unittest
from typing import List

from itly.plugin_iteratively import IterativelyPlugin, IterativelyOptions
from itly.plugin_iteratively._iteratively_client import Request
from itly.sdk import PluginLoadOptions, Environment, Properties, Event, Logger, ValidationResponse


class TestIteratively(unittest.TestCase):
    def test_iteratively(self):
        requests = []
        options = IterativelyOptions(
            url='',
            omit_values=False,
            flush_queue_size=3,
            flush_interval_ms=1000,
        )
        p = IterativelyPlugin('My-Key', options)
        p._send_request = lambda request: requests.append(request)

        self.assertEqual(p.id(), 'iteratively')
        try:
            p.load(PluginLoadOptions(environment=Environment.DEVELOPMENT, logger=Logger.NONE))

            p.post_identify("user-1", Properties(item1='value1', item2=2),
                            [
                                ValidationResponse(valid=True, plugin_id='custom', message=''),
                                ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
                            ])

            time.sleep(0.1)
            self._clean_requests(requests)
            self.assertEqual(requests, [])
            p.post_identify("user-2", Properties(item1='value3', item2=4), [])

            time.sleep(0.1)
            self._clean_requests(requests)
            self.assertEqual(requests, [])

            p.post_track("user-2", Event('event-1', Properties(item1='value1', item2=1)),
                         [
                             ValidationResponse(valid=False, plugin_id='custom', message='not valid!!!'),
                             ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
                         ])

            time.sleep(0.1)
            self._clean_requests(requests)
            self.assertEqual(requests, [
                Request(data={'objects': [
                    {'type': 'identify', 'properties': {'item1': 'value1', 'item2': 2}, 'valid': False, 'validation': {'details': 'invalid!!!'}},
                    {'type': 'identify', 'properties': {'item1': 'value3', 'item2': 4}, 'valid': True, 'validation': {'details': ''}},
                    {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'not valid!!!'}, 'eventName': 'event-1'}
                ]}),
            ])

            p.post_group("user-2", "group-2", Properties(item1='value2', item2=2), [])

            time.sleep(0.1)
            self._clean_requests(requests)
            self.assertEqual(requests, [
                Request(data={'objects': [
                    {'type': 'identify', 'properties': {'item1': 'value1', 'item2': 2}, 'valid': False, 'validation': {'details': 'invalid!!!'}},
                    {'type': 'identify', 'properties': {'item1': 'value3', 'item2': 4}, 'valid': True, 'validation': {'details': ''}},
                    {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'not valid!!!'}, 'eventName': 'event-1'}
                ]}),
            ])

            p.flush()

            time.sleep(0.1)
            self._clean_requests(requests)
            self.assertEqual(requests, [
                Request(data={'objects': [
                    {'type': 'identify', 'properties': {'item1': 'value1', 'item2': 2}, 'valid': False, 'validation': {'details': 'invalid!!!'}},
                    {'type': 'identify', 'properties': {'item1': 'value3', 'item2': 4}, 'valid': True, 'validation': {'details': ''}},
                    {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'not valid!!!'}, 'eventName': 'event-1'}
                ]}),
                Request(data={'objects': [
                    {'type': 'group', 'properties': {'item1': 'value2', 'item2': 2}, 'valid': True, 'validation': {'details': ''}}
                ]}),
            ])

            p.flush()
            p.flush()

            time.sleep(0.1)
            self._clean_requests(requests)
            self.assertEqual(requests, [
                Request(data={'objects': [
                    {'type': 'identify', 'properties': {'item1': 'value1', 'item2': 2}, 'valid': False, 'validation': {'details': 'invalid!!!'}},
                    {'type': 'identify', 'properties': {'item1': 'value3', 'item2': 4}, 'valid': True, 'validation': {'details': ''}},
                    {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'not valid!!!'}, 'eventName': 'event-1'}
                ]}),
                Request(data={'objects': [
                    {'type': 'group', 'properties': {'item1': 'value2', 'item2': 2}, 'valid': True, 'validation': {'details': ''}}
                ]}),
            ])

            p.post_page("user-2", "category-2", "page-3", Properties(item1='value3', item2=3),
                        [
                            ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
                            ValidationResponse(valid=True, plugin_id='custom', message=''),
                        ])

            time.sleep(1.1)
            self._clean_requests(requests)
            self.assertEqual(requests, [
                Request(data={'objects': [
                    {'type': 'identify', 'properties': {'item1': 'value1', 'item2': 2}, 'valid': False, 'validation': {'details': 'invalid!!!'}},
                    {'type': 'identify', 'properties': {'item1': 'value3', 'item2': 4}, 'valid': True, 'validation': {'details': ''}},
                    {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'not valid!!!'}, 'eventName': 'event-1'}
                ]}),
                Request(data={'objects': [
                    {'type': 'group', 'properties': {'item1': 'value2', 'item2': 2}, 'valid': True, 'validation': {'details': ''}}
                ]}),
                Request(data={'objects': [
                    {'type': 'page', 'properties': {'item1': 'value3', 'item2': 3}, 'valid': False, 'validation': {'details': 'invalid!!!'}}
                ]}),
            ])

            p.post_track("user-1", Event('event-5', Properties(item1='value5', item2=5), event_id='id-5', version='version-5'), [])
        finally:
            p.shutdown()

            time.sleep(0.1)
            self._clean_requests(requests)
            self.assertEqual(requests, [
                Request(data={'objects': [
                    {'type': 'identify', 'properties': {'item1': 'value1', 'item2': 2}, 'valid': False, 'validation': {'details': 'invalid!!!'}},
                    {'type': 'identify', 'properties': {'item1': 'value3', 'item2': 4}, 'valid': True, 'validation': {'details': ''}},
                    {'type': 'track', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': False, 'validation': {'details': 'not valid!!!'}, 'eventName': 'event-1'}
                ]}),
                Request(data={'objects': [
                    {'type': 'group', 'properties': {'item1': 'value2', 'item2': 2}, 'valid': True, 'validation': {'details': ''}}
                ]}),
                Request(data={'objects': [
                    {'type': 'page', 'properties': {'item1': 'value3', 'item2': 3}, 'valid': False, 'validation': {'details': 'invalid!!!'}}
                ]}),
                Request(data={'objects': [
                    {'type': 'track', 'properties': {'item1': 'value5', 'item2': 5}, 'valid': True, 'validation': {'details': ''}, 'eventName': 'event-5', 'eventId': 'id-5',
                     'eventSchemaVersion': 'version-5'}
                ]}),
            ])

    def test_iteratively_omit_values(self):
        requests = []
        options = IterativelyOptions(
            url='',
            omit_values=True,
            flush_queue_size=3,
            flush_interval_ms=1000,
        )
        p = IterativelyPlugin('My-Key', options)
        p._send_request = lambda request: requests.append(request)

        self.assertEqual(p.id(), 'iteratively')
        try:
            p.load(PluginLoadOptions(environment=Environment.DEVELOPMENT, logger=Logger.NONE))

            p.post_identify("user-1", Properties(item1='value1', item2=2), [])

            time.sleep(0.1)
            self._clean_requests(requests)
            self.assertEqual(requests, [])
            p.post_identify("user-2", Properties(item1='value3', item2=4),
                            [
                                ValidationResponse(valid=True, plugin_id='custom', message=''),
                                ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
                            ])

            time.sleep(0.1)
            self._clean_requests(requests)
            self.assertEqual(requests, [])

            p.post_track("user-2", Event('event-1', Properties(item1='value1', item2=1)), [])

            time.sleep(0.1)
            self._clean_requests(requests)
            self.assertEqual(requests, [
                Request(data={'objects': [
                    {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}},
                    {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}},
                    {'type': 'track', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}, 'eventName': 'event-1'}
                ]}),
            ])

            p.post_group("user-2", "group-2", Properties(item1='value2', item2=2),
                         [
                             ValidationResponse(valid=False, plugin_id='custom', message='not valid!!!'),
                             ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
                         ])

            time.sleep(0.1)
            self._clean_requests(requests)
            self.assertEqual(requests, [
                Request(data={'objects': [
                    {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}},
                    {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}},
                    {'type': 'track', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}, 'eventName': 'event-1'}
                ]}),
            ])

            p.flush()

            time.sleep(0.1)
            self._clean_requests(requests)
            self.assertEqual(requests, [
                Request(data={'objects': [
                    {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}},
                    {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}},
                    {'type': 'track', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}, 'eventName': 'event-1'}
                ]}),
                Request(data={'objects': [
                    {'type': 'group', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}}
                ]}),
            ])

            p.flush()
            p.flush()

            time.sleep(0.1)
            self._clean_requests(requests)
            self.assertEqual(requests, [
                Request(data={'objects': [
                    {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}},
                    {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}},
                    {'type': 'track', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}, 'eventName': 'event-1'}
                ]}),
                Request(data={'objects': [
                    {'type': 'group', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}}
                ]}),
            ])

            p.post_page("user-2", "category-2", "page-3", Properties(item1='value3', item2=3), [])

            time.sleep(1.1)
            self._clean_requests(requests)
            self.assertEqual(requests, [
                Request(data={'objects': [
                    {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}},
                    {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}},
                    {'type': 'track', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}, 'eventName': 'event-1'}
                ]}),
                Request(data={'objects': [
                    {'type': 'group', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}}
                ]}),
                Request(data={'objects': [
                    {'type': 'page', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}}
                ]}),
            ])

            p.post_track("user-1", Event('event-5', Properties(item1='value5', item2=5), event_id='id-5', version='version-5'),
                         [
                             ValidationResponse(valid=True, plugin_id='custom', message=''),
                             ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
                         ])
        finally:
            p.shutdown()

            time.sleep(0.1)
            self._clean_requests(requests)
            self.assertEqual(requests, [
                Request(data={'objects': [
                    {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}},
                    {'type': 'identify', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}},
                    {'type': 'track', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}, 'eventName': 'event-1'}
                ]}),
                Request(data={'objects': [
                    {'type': 'group', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}}
                ]}),
                Request(data={'objects': [
                    {'type': 'page', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}}
                ]}),
                Request(data={'objects': [
                    {'type': 'track', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''}, 'eventName': 'event-5', 'eventId': 'id-5',
                     'eventSchemaVersion': 'version-5'}
                ]}),
            ])

    def test_iteratively_disabled(self):
        requests = []
        options = IterativelyOptions(
            url='',
            disabled=True,
            flush_queue_size=3,
            flush_interval_ms=1000,
        )
        p = IterativelyPlugin('My-Key', options)
        p._send_request = lambda request: requests.append(request)

        self.assertEqual(p.id(), 'iteratively')
        try:
            p.load(PluginLoadOptions(environment=Environment.DEVELOPMENT, logger=Logger.NONE))

            p.post_identify("user-1", Properties(item1='value1', item2=2), [])

            time.sleep(0.1)
            self.assertEqual(requests, [])
            p.post_identify("user-2", Properties(item1='value3', item2=4), [])

            time.sleep(0.1)
            self.assertEqual(requests, [])

            p.post_track("user-2", Event('event-1', Properties(item1='value1', item2=1)),
                         [
                             ValidationResponse(valid=True, plugin_id='custom', message=''),
                             ValidationResponse(valid=False, plugin_id='custom', message='invalid!!!'),
                         ])

            time.sleep(0.1)
            self.assertEqual(requests, [])

            p.post_group("user-2", "group-2", Properties(item1='value2', item2=2), [])

            time.sleep(0.1)
            self.assertEqual(requests, [])

            p.flush()

            time.sleep(0.1)
            self.assertEqual(requests, [])

            p.flush()
            p.flush()

            time.sleep(0.1)
            self.assertEqual(requests, [])

            p.post_page("user-2", "category-2", "page-3", Properties(item1='value3', item2=3), [])

            time.sleep(1.1)
            self.assertEqual(requests, [])

            p.post_track("user-1", Event('event-5', Properties(item1='value5', item2=5), event_id='id-5', version='version-5'), [])
        finally:
            p.shutdown()

            time.sleep(0.1)
            self.assertEqual(requests, [])

    @staticmethod
    def _clean_requests(requests: List[Request]) -> None:
        for request in requests:
            for event in request.data['objects']:
                if 'dateSent' in event:
                    del event['dateSent']
