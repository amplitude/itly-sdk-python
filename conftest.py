import sys

import pytest
from pytest_httpserver import HTTPServer
from pytest_httpserver.httpserver import RequestMatcher
from pytest_httpserver.pytest_plugin import Plugin, PluginHTTPServer
from werkzeug.wrappers import Request

sys.path.extend([
    './packages/plugin-amplitude',
    './packages/plugin-iteratively',
    './packages/plugin-mixpanel',
    './packages/plugin-schema-validator',
    './packages/plugin-segment',
    './packages/sdk',
])


class _RequestMatcher(RequestMatcher):
    def __init__(self, *args, collected_data=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._collected_data = collected_data

    def match_data(self, request: Request) -> bool:
        self._collected_data.append(request.data)
        return super().match_data(request)


class _PluginHTTPServer(PluginHTTPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collected_data = []

    def create_matcher(self, *args, **kwargs) -> RequestMatcher:
        return _RequestMatcher(collected_data=self.collected_data, *args, **kwargs)

    def clear(self):
        self.collected_data = []


@pytest.fixture
def httpserver():
    if Plugin.SERVER:
        Plugin.SERVER.clear()
        yield Plugin.SERVER
        return

    host = HTTPServer.DEFAULT_LISTEN_HOST
    port = HTTPServer.DEFAULT_LISTEN_PORT

    server = _PluginHTTPServer(host=host, port=port)
    server.start()
    yield server
