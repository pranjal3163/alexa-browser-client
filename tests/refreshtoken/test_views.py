from unittest.mock import call, patch

from avs_client.refreshtoken.helpers import AmazonOauth2RequestManager
import pytest

from django.urls import reverse

from alexa_browser_client.refreshtoken.constants import (
    SESSION_KEY_REFRESH_TOKEN
)


@patch.object(AmazonOauth2RequestManager, 'get_authorization_request_url')
def test_authorization_request_redirect_view(
    mock_get_authorization_request_url, settings, client
):
    mock_get_authorization_request_url.return_value = 'https://redirect.com'

    response = client.get(reverse('refreshtoken'))

    assert response.status_code == 302
    assert response.url == 'https://redirect.com'

    assert mock_get_authorization_request_url.call_count == 1
    assert mock_get_authorization_request_url.call_args == call(
        device_type_id=settings.ALEXA_BROWSER_CLIENT_AVS_DEVICE_TYPE_ID,
        callback_url='http://testserver/refreshtoken/callback/'
    )


@patch.object(AmazonOauth2RequestManager, 'get_authorizarization_grant_params')
def test_authorization_grant_view(
    mock_get_authorizarization_grant_params, client, requests_mocker
):
    requests_mocker.post(
        AmazonOauth2RequestManager.authorization_grant_url,
        json={'refresh_token': 'my-refresh-token'}
    )
    mock_get_authorizarization_grant_params.return_value = {'code': 'my-code'}

    response = client.get(
        reverse('refreshtoken-callback'),
        {'code': 'my-code'}
    )

    assert response.status_code == 302

    assert mock_get_authorizarization_grant_params.call_count == 1
    assert mock_get_authorizarization_grant_params.call_args == call(
        code='my-code',
        callback_url='http://testserver/refreshtoken/callback/'
    )

    assert client.session[SESSION_KEY_REFRESH_TOKEN] == 'my-refresh-token'


@patch.object(AmazonOauth2RequestManager, 'get_authorizarization_grant_params')
def test_authorization_grant_view_bad_code(
    mock_get_authorizarization_grant_params, client, requests_mocker
):
    requests_mocker.post(
        AmazonOauth2RequestManager.authorization_grant_url,
        json={'error': 'incorrect code'},  # example. real error is different
        status_code=400,
    )
    mock_get_authorizarization_grant_params.return_value = {'code': 'my-code'}

    response = client.get(
        reverse('refreshtoken-callback'),
        {'code': 'my-bad-code'}
    )

    assert response.status_code == 400
    assert response.json() == {'error': 'incorrect code'}


@pytest.mark.parametrize('data', ({'hello': 'hi'}, {}))
def test_authorization_grant_view_missing_code(client, requests_mocker, data):

    response = client.get(reverse('refreshtoken-callback'), data)

    assert response.status_code == 400
    assert response.json() == {'code': ['This field is required.']}
