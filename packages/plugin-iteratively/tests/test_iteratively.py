import time
import unittest
from datetime import datetime, timedelta

from itly.plugin_iteratively import IterativelyPlugin, IterativelyOptions
from itly.plugin_iteratively._iteratively_client import Request
from itly.sdk import PluginOptions, Environment, Properties, Event, ValidationResponse, Logger


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
            p.load(PluginOptions(environment=Environment.DEVELOPMENT, logger=Logger.NONE))

            now = datetime(year=2020, month=8, day=27, hour=16, minute=41, second=25)

            p.identify("user-1", Properties(item1='value1', item2=2), timestamp=now)

            time.sleep(0.1)
            self.assertEqual(requests, [])
            p.identify("user-2", Properties(item1='value3', item2=4), timestamp=now + timedelta(milliseconds=500))

            time.sleep(0.1)
            self.assertEqual(requests, [])

            p.track("user-2", Event('event-1', Properties(item1='value1', item2=1)), timestamp=now + timedelta(milliseconds=800))

            time.sleep(0.1)
            self.assertEqual(requests, [
                Request(data={'objects': [{'type': 'identify', 'dateSent': '2020-08-27T16:41:25.000Z', 'properties': {'item1': 'value1', 'item2': 2}, 'valid': True, 'validation': {'details': ''}},
                                          {'type': 'identify', 'dateSent': '2020-08-27T16:41:25.500Z', 'properties': {'item1': 'value3', 'item2': 4}, 'valid': True,
                                           'validation': {'details': ''}},
                                          {'type': 'track', 'dateSent': '2020-08-27T16:41:25.800Z', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': True, 'validation': {'details': ''},
                                           'eventName': 'event-1'}]}),
            ])

            p.group("user-2", "group-2", Properties(item1='value2', item2=2), timestamp=now + timedelta(seconds=3))

            time.sleep(0.1)
            self.assertEqual(requests, [
                Request(data={'objects': [{'type': 'identify', 'dateSent': '2020-08-27T16:41:25.000Z', 'properties': {'item1': 'value1', 'item2': 2}, 'valid': True, 'validation': {'details': ''}},
                                          {'type': 'identify', 'dateSent': '2020-08-27T16:41:25.500Z', 'properties': {'item1': 'value3', 'item2': 4}, 'valid': True,
                                           'validation': {'details': ''}},
                                          {'type': 'track', 'dateSent': '2020-08-27T16:41:25.800Z', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': True, 'validation': {'details': ''},
                                           'eventName': 'event-1'}]}),
            ])

            p.flush()

            time.sleep(0.1)
            self.assertEqual(requests, [
                Request(data={'objects': [{'type': 'identify', 'dateSent': '2020-08-27T16:41:25.000Z', 'properties': {'item1': 'value1', 'item2': 2}, 'valid': True, 'validation': {'details': ''}},
                                          {'type': 'identify', 'dateSent': '2020-08-27T16:41:25.500Z', 'properties': {'item1': 'value3', 'item2': 4}, 'valid': True,
                                           'validation': {'details': ''}},
                                          {'type': 'track', 'dateSent': '2020-08-27T16:41:25.800Z', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': True, 'validation': {'details': ''},
                                           'eventName': 'event-1'}]}),
                Request(data={'objects': [{'type': 'group', 'dateSent': '2020-08-27T16:41:28.000Z', 'properties': {'item1': 'value2', 'item2': 2}, 'valid': True, 'validation': {'details': ''}}]}),
            ])

            p.flush()
            p.flush()

            time.sleep(0.1)
            self.assertEqual(requests, [
                Request(data={'objects': [{'type': 'identify', 'dateSent': '2020-08-27T16:41:25.000Z', 'properties': {'item1': 'value1', 'item2': 2}, 'valid': True, 'validation': {'details': ''}},
                                          {'type': 'identify', 'dateSent': '2020-08-27T16:41:25.500Z', 'properties': {'item1': 'value3', 'item2': 4}, 'valid': True,
                                           'validation': {'details': ''}},
                                          {'type': 'track', 'dateSent': '2020-08-27T16:41:25.800Z', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': True, 'validation': {'details': ''},
                                           'eventName': 'event-1'}]}),
                Request(data={'objects': [{'type': 'group', 'dateSent': '2020-08-27T16:41:28.000Z', 'properties': {'item1': 'value2', 'item2': 2}, 'valid': True, 'validation': {'details': ''}}]}),
            ])

            p.page("user-2", "category-2", "page-3", Properties(item1='value3', item2=3), timestamp=now + timedelta(seconds=7))

            time.sleep(1.1)
            self.assertEqual(requests, [
                Request(data={'objects': [{'type': 'identify', 'dateSent': '2020-08-27T16:41:25.000Z', 'properties': {'item1': 'value1', 'item2': 2}, 'valid': True, 'validation': {'details': ''}},
                                          {'type': 'identify', 'dateSent': '2020-08-27T16:41:25.500Z', 'properties': {'item1': 'value3', 'item2': 4}, 'valid': True,
                                           'validation': {'details': ''}},
                                          {'type': 'track', 'dateSent': '2020-08-27T16:41:25.800Z', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': True, 'validation': {'details': ''},
                                           'eventName': 'event-1'}]}),
                Request(data={'objects': [{'type': 'group', 'dateSent': '2020-08-27T16:41:28.000Z', 'properties': {'item1': 'value2', 'item2': 2}, 'valid': True, 'validation': {'details': ''}}]}),
                Request(data={'objects': [{'type': 'page', 'dateSent': '2020-08-27T16:41:32.000Z', 'properties': {'item1': 'value3', 'item2': 3}, 'valid': True, 'validation': {'details': ''}}]}),
            ])

            p.on_validation_error(ValidationResponse(valid=False, plugin_id='custom', message='is empty'), Event('event-4', Properties(item1='value4', item2=4)), timestamp=now + timedelta(seconds=10))
            p.track("user-1", Event('event-5', Properties(item1='value5', item2=5), event_id='id-5', version='version-5'), timestamp=now + timedelta(seconds=12))
        finally:
            p.shutdown()

            time.sleep(0.1)
            self.assertEqual(requests, [
                Request(data={'objects': [{'type': 'identify', 'dateSent': '2020-08-27T16:41:25.000Z', 'properties': {'item1': 'value1', 'item2': 2}, 'valid': True, 'validation': {'details': ''}},
                                          {'type': 'identify', 'dateSent': '2020-08-27T16:41:25.500Z', 'properties': {'item1': 'value3', 'item2': 4}, 'valid': True,
                                           'validation': {'details': ''}},
                                          {'type': 'track', 'dateSent': '2020-08-27T16:41:25.800Z', 'properties': {'item1': 'value1', 'item2': 1}, 'valid': True, 'validation': {'details': ''},
                                           'eventName': 'event-1'}]}),
                Request(data={'objects': [{'type': 'group', 'dateSent': '2020-08-27T16:41:28.000Z', 'properties': {'item1': 'value2', 'item2': 2}, 'valid': True, 'validation': {'details': ''}}]}),
                Request(data={'objects': [{'type': 'page', 'dateSent': '2020-08-27T16:41:32.000Z', 'properties': {'item1': 'value3', 'item2': 3}, 'valid': True, 'validation': {'details': ''}}]}),
                Request(data={'objects': [
                    {'type': 'track', 'dateSent': '2020-08-27T16:41:35.000Z', 'properties': {'item1': 'value4', 'item2': 4}, 'valid': False, 'validation': {'details': 'is empty'},
                     'eventName': 'event-4'},
                    {'type': 'track', 'dateSent': '2020-08-27T16:41:37.000Z', 'properties': {'item1': 'value5', 'item2': 5}, 'valid': True, 'validation': {'details': ''}, 'eventName': 'event-5',
                     'eventId': 'id-5', 'eventSchemaVersion': 'version-5'}]}),
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
            p.load(PluginOptions(environment=Environment.DEVELOPMENT, logger=Logger.NONE))

            now = datetime(year=2020, month=8, day=27, hour=16, minute=41, second=25)

            p.identify("user-1", Properties(item1='value1', item2=2), timestamp=now)

            time.sleep(0.1)
            self.assertEqual(requests, [])
            p.identify("user-2", Properties(item1='value3', item2=4), timestamp=now + timedelta(milliseconds=500))

            time.sleep(0.1)
            self.assertEqual(requests, [])

            p.track("user-2", Event('event-1', Properties(item1='value1', item2=1)), timestamp=now + timedelta(milliseconds=800))

            time.sleep(0.1)
            self.assertEqual(requests, [
                Request(data={'objects': [{'type': 'identify', 'dateSent': '2020-08-27T16:41:25.000Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}},
                                          {'type': 'identify', 'dateSent': '2020-08-27T16:41:25.500Z', 'properties': {'item1': None, 'item2': None}, 'valid': True,
                                           'validation': {'details': ''}},
                                          {'type': 'track', 'dateSent': '2020-08-27T16:41:25.800Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''},
                                           'eventName': 'event-1'}]}),
            ])

            p.group("user-2", "group-2", Properties(item1='value2', item2=2), timestamp=now + timedelta(seconds=3))

            time.sleep(0.1)
            self.assertEqual(requests, [
                Request(data={'objects': [{'type': 'identify', 'dateSent': '2020-08-27T16:41:25.000Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}},
                                          {'type': 'identify', 'dateSent': '2020-08-27T16:41:25.500Z', 'properties': {'item1': None, 'item2': None}, 'valid': True,
                                           'validation': {'details': ''}},
                                          {'type': 'track', 'dateSent': '2020-08-27T16:41:25.800Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''},
                                           'eventName': 'event-1'}]}),
            ])

            p.flush()

            time.sleep(0.1)
            self.assertEqual(requests, [
                Request(data={'objects': [{'type': 'identify', 'dateSent': '2020-08-27T16:41:25.000Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}},
                                          {'type': 'identify', 'dateSent': '2020-08-27T16:41:25.500Z', 'properties': {'item1': None, 'item2': None}, 'valid': True,
                                           'validation': {'details': ''}},
                                          {'type': 'track', 'dateSent': '2020-08-27T16:41:25.800Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''},
                                           'eventName': 'event-1'}]}),
                Request(data={'objects': [{'type': 'group', 'dateSent': '2020-08-27T16:41:28.000Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}}]}),
            ])

            p.flush()
            p.flush()

            time.sleep(0.1)
            self.assertEqual(requests, [
                Request(data={'objects': [{'type': 'identify', 'dateSent': '2020-08-27T16:41:25.000Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}},
                                          {'type': 'identify', 'dateSent': '2020-08-27T16:41:25.500Z', 'properties': {'item1': None, 'item2': None}, 'valid': True,
                                           'validation': {'details': ''}},
                                          {'type': 'track', 'dateSent': '2020-08-27T16:41:25.800Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''},
                                           'eventName': 'event-1'}]}),
                Request(data={'objects': [{'type': 'group', 'dateSent': '2020-08-27T16:41:28.000Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}}]}),
            ])

            p.page("user-2", "category-2", "page-3", Properties(item1='value3', item2=3), timestamp=now + timedelta(seconds=7))

            time.sleep(1.1)
            self.assertEqual(requests, [
                Request(data={'objects': [{'type': 'identify', 'dateSent': '2020-08-27T16:41:25.000Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}},
                                          {'type': 'identify', 'dateSent': '2020-08-27T16:41:25.500Z', 'properties': {'item1': None, 'item2': None}, 'valid': True,
                                           'validation': {'details': ''}},
                                          {'type': 'track', 'dateSent': '2020-08-27T16:41:25.800Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''},
                                           'eventName': 'event-1'}]}),
                Request(data={'objects': [{'type': 'group', 'dateSent': '2020-08-27T16:41:28.000Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}}]}),
                Request(data={'objects': [{'type': 'page', 'dateSent': '2020-08-27T16:41:32.000Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}}]}),
            ])

            p.on_validation_error(ValidationResponse(valid=False, plugin_id='custom', message='is empty'), Event('event-4', Properties(item1='value4', item2=4)), timestamp=now + timedelta(seconds=10))
            p.track("user-1", Event('event-5', Properties(item1='value5', item2=5), event_id='id-5', version='version-5'), timestamp=now + timedelta(seconds=12))
        finally:
            p.shutdown()

            time.sleep(0.1)
            self.assertEqual(requests, [
                Request(data={'objects': [{'type': 'identify', 'dateSent': '2020-08-27T16:41:25.000Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}},
                                          {'type': 'identify', 'dateSent': '2020-08-27T16:41:25.500Z', 'properties': {'item1': None, 'item2': None}, 'valid': True,
                                           'validation': {'details': ''}},
                                          {'type': 'track', 'dateSent': '2020-08-27T16:41:25.800Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''},
                                           'eventName': 'event-1'}]}),
                Request(data={'objects': [{'type': 'group', 'dateSent': '2020-08-27T16:41:28.000Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}}]}),
                Request(data={'objects': [{'type': 'page', 'dateSent': '2020-08-27T16:41:32.000Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}}]}),
                Request(data={'objects': [
                    {'type': 'track', 'dateSent': '2020-08-27T16:41:35.000Z', 'properties': {'item1': None, 'item2': None}, 'valid': False, 'validation': {'details': ''},
                     'eventName': 'event-4'},
                    {'type': 'track', 'dateSent': '2020-08-27T16:41:37.000Z', 'properties': {'item1': None, 'item2': None}, 'valid': True, 'validation': {'details': ''}, 'eventName': 'event-5',
                     'eventId': 'id-5', 'eventSchemaVersion': 'version-5'}]}),
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
            p.load(PluginOptions(environment=Environment.DEVELOPMENT, logger=Logger.NONE))

            now = datetime(year=2020, month=8, day=27, hour=16, minute=41, second=25)

            p.identify("user-1", Properties(item1='value1', item2=2), timestamp=now)

            time.sleep(0.1)
            self.assertEqual(requests, [])
            p.identify("user-2", Properties(item1='value3', item2=4), timestamp=now + timedelta(milliseconds=500))

            time.sleep(0.1)
            self.assertEqual(requests, [])

            p.track("user-2", Event('event-1', Properties(item1='value1', item2=1)), timestamp=now + timedelta(milliseconds=800))

            time.sleep(0.1)
            self.assertEqual(requests, [])

            p.group("user-2", "group-2", Properties(item1='value2', item2=2), timestamp=now + timedelta(seconds=3))

            time.sleep(0.1)
            self.assertEqual(requests, [])

            p.flush()

            time.sleep(0.1)
            self.assertEqual(requests, [])

            p.flush()
            p.flush()

            time.sleep(0.1)
            self.assertEqual(requests, [])

            p.page("user-2", "category-2", "page-3", Properties(item1='value3', item2=3), timestamp=now + timedelta(seconds=7))

            time.sleep(1.1)
            self.assertEqual(requests, [])

            p.on_validation_error(ValidationResponse(valid=False, plugin_id='custom', message='is empty'), Event('event-4', Properties(item1='value4', item2=4)), timestamp=now + timedelta(seconds=10))
            p.track("user-1", Event('event-5', Properties(item1='value5', item2=5), event_id='id-5', version='version-5'), timestamp=now + timedelta(seconds=12))
        finally:
            p.shutdown()

            time.sleep(0.1)
            self.assertEqual(requests, [])
