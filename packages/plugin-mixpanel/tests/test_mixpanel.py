import time
import unittest
from datetime import datetime, timedelta

from itly.plugin_mixpanel import MixpanelPlugin, MixpanelOptions
from itly.plugin_mixpanel._mixpanel_consumer import Request
from itly.sdk import PluginOptions, Environment, Properties, Event


class TestMixpanel(unittest.TestCase):
    def test_mixpanel(self):
        requests = []
        options = MixpanelOptions(
            flush_queue_size=3,
            flush_interval_ms=1000,
        )
        p = MixpanelPlugin('My-Key', options)
        p._send_request = lambda request: requests.append(request)

        assert p.id() == 'mixpanel'
        try:
            p.load(PluginOptions(environment=Environment.DEVELOPMENT))

            now = datetime(year=2020, month=8, day=27, hour=16, minute=41, second=25)

            p.identify("user-1", Properties(item1='value1', item2=2), timestamp=now)

            time.sleep(0.1)
            assert requests == []
            p.alias("user-1", "prev-user-1")

            time.sleep(0.1)
            assert requests == [
                Request('people', '[{"$token":"My-Key","$time":1598532085,"$distinct_id":"user-1","$set":{"item1":"value1","item2":2}}]'),
            ]

            p.track("user-2", Event('event-1', Properties(item1='value1', item2=1)), timestamp=now)
            time.sleep(0.1)
            assert requests == [
                Request('people', '[{"$token":"My-Key","$time":1598532085,"$distinct_id":"user-1","$set":{"item1":"value1","item2":2}}]'),
                Request('alias', '[{"event":"$create_alias","properties":{"distinct_id":"user-1","alias":"prev-user-1","token":"My-Key"}}]'),
            ]

            p.track("user-2", Event('event-2', Properties(item1='value2', item2=2)), timestamp=now + timedelta(seconds=3))
            time.sleep(0.1)
            assert requests == [
                Request('people', '[{"$token":"My-Key","$time":1598532085,"$distinct_id":"user-1","$set":{"item1":"value1","item2":2}}]'),
                Request('alias', '[{"event":"$create_alias","properties":{"distinct_id":"user-1","alias":"prev-user-1","token":"My-Key"}}]'),
            ]

            p.flush()
            time.sleep(0.1)
            assert requests == [
                Request('people', '[{"$token":"My-Key","$time":1598532085,"$distinct_id":"user-1","$set":{"item1":"value1","item2":2}}]'),
                Request('alias', '[{"event":"$create_alias","properties":{"distinct_id":"user-1","alias":"prev-user-1","token":"My-Key"}}]'),
                Request('events', '[{"event":"event-1","properties":{"token":"My-Key","distinct_id":"user-2","time":1598532085,"mp_lib":"python","$lib_version":"4.6.0","item1":"value1","item2":1}},{"event":"event-2","properties":{"token":"My-Key","distinct_id":"user-2","time":1598532088,"mp_lib":"python","$lib_version":"4.6.0","item1":"value2","item2":2}}]'),
            ]

            p.flush()
            p.flush()

            time.sleep(0.1)
            assert requests == [
                Request('people', '[{"$token":"My-Key","$time":1598532085,"$distinct_id":"user-1","$set":{"item1":"value1","item2":2}}]'),
                Request('alias', '[{"event":"$create_alias","properties":{"distinct_id":"user-1","alias":"prev-user-1","token":"My-Key"}}]'),
                Request('events', '[{"event":"event-1","properties":{"token":"My-Key","distinct_id":"user-2","time":1598532085,"mp_lib":"python","$lib_version":"4.6.0","item1":"value1","item2":1}},{"event":"event-2","properties":{"token":"My-Key","distinct_id":"user-2","time":1598532088,"mp_lib":"python","$lib_version":"4.6.0","item1":"value2","item2":2}}]'),
            ]

            p.track("user-2", Event('event-3', Properties(item1='value3', item2=3)), timestamp=now + timedelta(seconds=7))

            time.sleep(1.1)
            assert requests == [
                Request('people', '[{"$token":"My-Key","$time":1598532085,"$distinct_id":"user-1","$set":{"item1":"value1","item2":2}}]'),
                Request('alias', '[{"event":"$create_alias","properties":{"distinct_id":"user-1","alias":"prev-user-1","token":"My-Key"}}]'),
                Request('events', '[{"event":"event-1","properties":{"token":"My-Key","distinct_id":"user-2","time":1598532085,"mp_lib":"python","$lib_version":"4.6.0","item1":"value1","item2":1}},{"event":"event-2","properties":{"token":"My-Key","distinct_id":"user-2","time":1598532088,"mp_lib":"python","$lib_version":"4.6.0","item1":"value2","item2":2}}]'),
                Request('events', '[{"event":"event-3","properties":{"token":"My-Key","distinct_id":"user-2","time":1598532092,"mp_lib":"python","$lib_version":"4.6.0","item1":"value3","item2":3}}]'),
            ]

            p.track("user-2", Event('event-4', Properties(item1='value4', item2=4)), timestamp=now + timedelta(seconds=10))
            p.track("user-1", Event('event-5', Properties(item1='value5', item2=5)), timestamp=now + timedelta(seconds=12))
        finally:
            p.shutdown()

            time.sleep(0.1)
            assert requests == [
                Request('people', '[{"$token":"My-Key","$time":1598532085,"$distinct_id":"user-1","$set":{"item1":"value1","item2":2}}]'),
                Request('alias', '[{"event":"$create_alias","properties":{"distinct_id":"user-1","alias":"prev-user-1","token":"My-Key"}}]'),
                Request('events', '[{"event":"event-1","properties":{"token":"My-Key","distinct_id":"user-2","time":1598532085,"mp_lib":"python","$lib_version":"4.6.0","item1":"value1","item2":1}},{"event":"event-2","properties":{"token":"My-Key","distinct_id":"user-2","time":1598532088,"mp_lib":"python","$lib_version":"4.6.0","item1":"value2","item2":2}}]'),
                Request('events', '[{"event":"event-3","properties":{"token":"My-Key","distinct_id":"user-2","time":1598532092,"mp_lib":"python","$lib_version":"4.6.0","item1":"value3","item2":3}}]'),
                Request('events', '[{"event":"event-4","properties":{"token":"My-Key","distinct_id":"user-2","time":1598532095,"mp_lib":"python","$lib_version":"4.6.0","item1":"value4","item2":4}},{"event":"event-5","properties":{"token":"My-Key","distinct_id":"user-1","time":1598532097,"mp_lib":"python","$lib_version":"4.6.0","item1":"value5","item2":5}}]'),
            ]
