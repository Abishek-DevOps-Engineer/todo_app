"""
Pytest configuration and shared fixtures for Taska todo app tests.

Provides:
- Flask test client with TESTING enabled
- Mocked MySQL database connection
- Logged-in session fixture
- Mock cursor fixture with configurable data
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


@pytest.fixture
def client():
    """
    Flask test client with TESTING mode enabled.
    Uses in-memory session management for tests.
    """
    app.config['TESTING'] = True
    app.config['SESSION_TYPE'] = 'filesystem'
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def mock_db_connection():
    """
    Mocked MySQL database connection.
    Returns a MagicMock object that simulates a mysql.connector connection.
    """
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_conn.commit.return_value = None
    mock_conn.close.return_value = None
    return mock_conn


@pytest.fixture
def mock_cursor():
    """
    Mocked database cursor that returns configurable data.
    Can be used to control what the database returns during tests.
    """
    mock_cur = MagicMock()
    mock_cur.execute.return_value = None
    mock_cur.fetchone.return_value = None
    mock_cur.fetchall.return_value = []
    mock_cur.close.return_value = None
    return mock_cur


@pytest.fixture
def logged_in_client(client):
    """
    Flask test client with a simulated logged-in session.
    Sets session['user_id'] = 1 and session['username'] = 'testuser'.
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser'
    return client


@pytest.fixture
def patched_get_db_connection(mock_db_connection, mock_cursor):
    """
    Patches app.get_db_connection to return the mock connection.
    The mock connection's cursor() method returns the mock cursor.
    """
    mock_db_connection.cursor.return_value = mock_cursor
    
    with patch('app.get_db_connection', return_value=mock_db_connection):
        yield mock_db_connection, mock_cursor


@pytest.fixture
def patched_get_db_connection_none():
    """
    Patches app.get_db_connection to return None (simulating connection failure).
    """
    with patch('app.get_db_connection', return_value=None):
        yield
