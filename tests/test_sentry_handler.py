import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import Request, HTTPException
from starlette.datastructures import MutableHeaders

from interfaces.database import DatabaseI
from interfaces.vector_database import VectorDatabaseI
from interfaces.sentry_handler import SentryHandler
# Assuming the file name of the provided code is "your_file.py"

@pytest.fixture
def database_interface():
    return MagicMock(spec=DatabaseI)

@pytest.fixture
def vector_database_interface():
    return MagicMock(spec=VectorDatabaseI)

@pytest.fixture
def sentry_handler(database_interface, vector_database_interface):
    return SentryHandler(database_interface, vector_database_interface, "test_app_id", "test_app_pem")

@pytest.fixture
def mock_request():
    request = AsyncMock(spec=Request)
    headers = MutableHeaders()
    headers.update({
        "Sentry-Hook-Signature": "test-signature",
        "Sentry-Hook-Resource": "test-resource"
    })
    request.headers = headers
    return request

def test_sentry_handler_init(database_interface, vector_database_interface):
    handler = SentryHandler(database_interface, vector_database_interface, "test_app_id", "test_app_pem")
    assert handler.db == database_interface
    assert handler.vector_db == vector_database_interface
    assert handler.app_id == "test_app_id"
    assert handler.app_pem == "test_app_pem"

@patch("your_file.json.loads", return_value={"data": {"error": {"project": 123}}})
async def test_handle_request_error_path(mock_json_loads, sentry_handler, mock_request):
    mock_request.body = AsyncMock(return_value=b'{"data": {}}')
    sentry_handler.db.fetch_repo_info_with_alert_service_id = MagicMock(return_value=MagicMock(data=[{
        "sentry_client_secret": "test-secret",
        "github_repository": "test-repo",
        "github_base_branch": "test-branch"
    }]))
    
    with pytest.raises(HTTPException) as e:
        await sentry_handler.handle_request(mock_request, MagicMock())
    assert e.value.status_code == 401

@patch("your_file.json.loads", return_value={"data": {"issue": {"project": {"id": 456}}}})
async def test_handle_request_issue_path(mock_json_loads, sentry_handler, mock_request):
    mock_request.body = AsyncMock(return_value=b'{"data": {}}')
    sentry_handler.db.fetch_repo_info_with_alert_service_id = MagicMock(return_value=MagicMock(data=[{
        "sentry_client_secret": "test-secret",
        "github_repository": "test-repo",
        "github_base_branch": "test-branch"
    }]))
    
    with pytest.raises(HTTPException) as e:
        await sentry_handler.handle_request(mock_request, MagicMock())
    assert e.value.status_code == 401

@patch("your_file.json.loads", return_value={"data": {}, "action": "created"})
async def test_handle_request_created_path(mock_json_loads, sentry_handler, mock_request):
    mock_request.body = AsyncMock(return_value=b'{"data": {}}')
    sentry_handler.db.fetch_repo_info_with_alert_service_id = MagicMock(return_value=MagicMock(data=[{
        "sentry_client_secret": "test-secret",
        "github_repository": "test-repo",
        "github_base_branch": "test-branch"
    }]))
    sentry_handler.vector_db.search = MagicMock(return_value=[])
    
    result = await sentry_handler.handle_request(mock_request, MagicMock())
    assert result == {"status": "received"}

# Extend the tests further to handle:
# - Different signatures (valid/invalid)
# - Different payload structures
# - The branching and issue creation logic in GithubService
# - Testing agent pool logic and thread execution

# With the provided and extended tests, you should achieve high code coverage for the SentryHandler's handle_request method.
