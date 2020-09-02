import time
import unittest
from datetime import datetime, timedelta

from itly.plugin_amplitude import AmplitudePlugin, AmplitudeOptions
from itly.plugin_amplitude._amplitude_client import Request
from itly.sdk import PluginLoadOptions, Environment, Properties, Event, Logger


class TestAmplitude(unittest.TestCase):
    def test_amplitude(self):
        requests = []
        options = AmplitudeOptions(
            flush_queue_size=3,
            flush_interval_ms=1000,
        )
        p = AmplitudePlugin('My-Key', options)
        p._send_request = lambda request: requests.append(request)

        self.assertEqual(p.id(), 'amplitude')
        try:
            p.load(PluginLoadOptions(environment=Environment.DEVELOPMENT, logger=Logger.NONE))

            p.identify("user-1", Properties(item1='value1', item2=2))
            time.sleep(0.1)
            self.assertEqual(requests, [])

            now = datetime(year=2020, month=8, day=27, hour=16, minute=41, second=25)
            p.track("user-2", Event('event-1', Properties(item1='value1', item2=1)), timestamp=now)
            time.sleep(0.1)
            self.assertEqual(requests, [
                Request('https://api.amplitude.com/identify', False, {'identification': '[{"user_id": "user-1", "user_properties": {"item1": "value1", "item2": 2}}]', 'api_key': 'My-Key'}),
            ])

            p.track("user-2", Event('event-2', Properties(item1='value2', item2=2)), timestamp=now + timedelta(seconds=3))
            time.sleep(0.1)
            self.assertEqual(requests, [
                Request('https://api.amplitude.com/identify', False, {'identification': '[{"user_id": "user-1", "user_properties": {"item1": "value1", "item2": 2}}]', 'api_key': 'My-Key'}),
            ])

            p.flush()
            time.sleep(0.1)
            self.assertEqual(requests, [
                Request('https://api.amplitude.com/identify', False, {'identification': '[{"user_id": "user-1", "user_properties": {"item1": "value1", "item2": 2}}]', 'api_key': 'My-Key'}),
                Request('https://api.amplitude.com/2/httpapi', True, {'events': [{'user_id': 'user-2', 'event_type': 'event-1', 'time': 1598532085000, 'event_properties': {'item1': 'value1', 'item2': 1}}, {'user_id': 'user-2', 'event_type': 'event-2', 'time': 1598532088000, 'event_properties': {'item1': 'value2', 'item2': 2}}], 'api_key': 'My-Key'}),
            ])

            p.flush()
            p.flush()

            time.sleep(0.1)
            self.assertEqual(requests, [
                Request('https://api.amplitude.com/identify', False, {'identification': '[{"user_id": "user-1", "user_properties": {"item1": "value1", "item2": 2}}]', 'api_key': 'My-Key'}),
                Request('https://api.amplitude.com/2/httpapi', True, {'events': [{'user_id': 'user-2', 'event_type': 'event-1', 'time': 1598532085000, 'event_properties': {'item1': 'value1', 'item2': 1}}, {'user_id': 'user-2', 'event_type': 'event-2', 'time': 1598532088000, 'event_properties': {'item1': 'value2', 'item2': 2}}], 'api_key': 'My-Key'}),
            ])

            p.track("user-2", Event('event-3', Properties(item1='value3', item2=3)), timestamp=now + timedelta(seconds=7))

            time.sleep(1.1)
            self.assertEqual(requests, [
                Request('https://api.amplitude.com/identify', False, {'identification': '[{"user_id": "user-1", "user_properties": {"item1": "value1", "item2": 2}}]', 'api_key': 'My-Key'}),
                Request('https://api.amplitude.com/2/httpapi', True, {'events': [{'user_id': 'user-2', 'event_type': 'event-1', 'time': 1598532085000, 'event_properties': {'item1': 'value1', 'item2': 1}}, {'user_id': 'user-2', 'event_type': 'event-2', 'time': 1598532088000, 'event_properties': {'item1': 'value2', 'item2': 2}}], 'api_key': 'My-Key'}),
                Request('https://api.amplitude.com/2/httpapi', True, {'events': [{'user_id': 'user-2', 'event_type': 'event-3', 'time': 1598532092000, 'event_properties': {'item1': 'value3', 'item2': 3}}], 'api_key': 'My-Key'}),
            ])

            p.track("user-2", Event('event-4', Properties(item1='value4', item2=4)), timestamp=now + timedelta(seconds=10))
            p.track("user-1", Event('event-5', Properties(item1='value5', item2=5)), timestamp=now + timedelta(seconds=12))
        finally:
            p.shutdown()

            time.sleep(0.1)
            self.assertEqual(requests, [
                Request('https://api.amplitude.com/identify', False, {'identification': '[{"user_id": "user-1", "user_properties": {"item1": "value1", "item2": 2}}]', 'api_key': 'My-Key'}),
                Request('https://api.amplitude.com/2/httpapi', True, {'events': [{'user_id': 'user-2', 'event_type': 'event-1', 'time': 1598532085000, 'event_properties': {'item1': 'value1', 'item2': 1}}, {'user_id': 'user-2', 'event_type': 'event-2', 'time': 1598532088000, 'event_properties': {'item1': 'value2', 'item2': 2}}], 'api_key': 'My-Key'}),
                Request('https://api.amplitude.com/2/httpapi', True, {'events': [{'user_id': 'user-2', 'event_type': 'event-3', 'time': 1598532092000, 'event_properties': {'item1': 'value3', 'item2': 3}}], 'api_key': 'My-Key'}),
                Request('https://api.amplitude.com/2/httpapi', True, {'events': [{'user_id': 'user-2', 'event_type': 'event-4', 'time': 1598532095000, 'event_properties': {'item1': 'value4', 'item2': 4}}, {'user_id': 'user-1', 'event_type': 'event-5', 'time': 1598532097000, 'event_properties': {'item1': 'value5', 'item2': 5}}], 'api_key': 'My-Key'}),
            ])
