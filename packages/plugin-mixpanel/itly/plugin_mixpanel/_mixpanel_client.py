from typing import Dict, Optional

from mixpanel import Mixpanel, json_dumps


class MixpanelClient(Mixpanel):
    def alias(self, alias_id, original, meta=None):
        # type: (str, str, Optional[Dict]) -> None
        event = {
            'event': '$create_alias',
            'properties': {
                'distinct_id': original,
                'alias': alias_id,
                'token': self._token,
            },
        }
        if meta:
            event.update(meta)
        self._consumer.send('alias', json_dumps(event, cls=self._serializer))
