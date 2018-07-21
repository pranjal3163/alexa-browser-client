from unittest.mock import patch

from alexa_browser_client.refreshtoken.constants import (
    SESSION_KEY_REFRESH_TOKEN
)
from channels.test.base import ChannelTestCaseMixin
from channels.test import WSClient
import pytest


class ChannelTestCase(ChannelTestCaseMixin):
    def _pre_setup(self):
        pass

    def _post_teardown(self):
        pass


@pytest.fixture(autouse=True)
def mock_alexa_client_connect():
    """Prevent handshake with alexa"""
    stub = patch(
        'avs_client.avs_client.client.AlexaVoiceServiceClient.connect'
    )
    stub.start()
    yield stub
    stub.stop()


@pytest.fixture
def mock_channel_backend(autouse=True):
    """Hacky way to expose ChannelTestCase to pytest fixture."""
    instance = ChannelTestCase()
    instance._pre_setup()
    yield instance
    instance._post_teardown()


@pytest.fixture
def ws_client():
    return WSClient()


@pytest.fixture
def ws_client_refresh_token():
    ws_client = WSClient()
    ws_client.session.create()
    ws_client.session[SESSION_KEY_REFRESH_TOKEN] = 'my-refresh-token'
    ws_client.session.save()
    return ws_client
