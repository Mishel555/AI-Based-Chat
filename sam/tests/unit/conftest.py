import os
from pathlib import Path
from unittest import mock

import pytest
from pytest_mock import MockerFixture


def _configure_env():
    os.environ.update(
        {
            'POWERTOOLS_METRICS_NAMESPACE': 'metric_namespace',
            'POWERTOOLS_SERVICE_NAME': 'metric_name',
        }
    )


def pytest_configure():
    _configure_env()


_repository = None


def repository():
    global _repository
    if not _repository:
        from tests.unit.mocks.redis_repository import RedisRepositoryMock
        _repository = RedisRepositoryMock()
    return _repository


@pytest.fixture()
def redis_mock(mocker: MockerFixture, mock_env):
    mocker.patch('chatbot_cloud_util.auth_utils.get_redis_repository', return_value=repository())
    mocker.patch('chatbot_cloud_util.auth_utils.session_repository.get_redis_repository', return_value=repository())
    yield repository()
    repository().cleanup()


@pytest.fixture(scope='function')
def mock_env(mocker: MockerFixture) -> None:
    with mock.patch.dict(
            os.environ,
            clear=True,
            POWERTOOLS_METRICS_NAMESPACE='metric_namespace',
            POWERTOOLS_SERVICE_NAME='metric_name',
            REDIS_HOST='localhost',
            REDIS_PORT='6379',
            CLIENT_ID='test_client_id',
            AUTH0_URL='https://test.auth0.com',
            chatbot_request_prefix_tpl='{id}.json',
            chatbot_chat_history_prefix_tpl='{year}-{month}/{day}/{chat_id}/'
    ):
        yield os.environ


@pytest.fixture()
def base_dir() -> Path:
    return Path(__file__).parent.parent.parent.parent.resolve()


@pytest.fixture()
def mock_auth(mock_env: dict, mocker: MockerFixture):
    validate_access_token_mock = mocker.patch('chatbot_cloud_util.decorators._validate_access_token')
    yield validate_access_token_mock
    validate_access_token_mock.assert_called_once()
