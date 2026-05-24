"""
Test suite for authentication routes (register, login, logout).

Covers:
- GET /register and GET /login page loads
- GET / redirects to login when not logged in
- POST /register validation and user creation
- POST /login validation and session management
- GET /logout session cleanup
- Database connection failure handling
"""

import pytest
from werkzeug.security import generate_password_hash
from unittest.mock import patch


class TestRegisterPage:
    """Tests for GET /register endpoint."""

    def test_get_register_returns_200(self, client):
        """GET /register should return 200 OK."""
        res = client.get('/register')
        assert res.status_code == 200
        assert b'Register' in res.data or b'register' in res.data

    def test_get_register_redirects_to_todos_if_logged_in(self, logged_in_client):
        """GET /register should redirect to /todos if user is already logged in."""
        res = logged_in_client.get('/register')
        assert res.status_code == 302
        assert res.headers['Location'].endswith('/todos')


class TestLoginPage:
    """Tests for GET /login endpoint."""

    def test_get_login_returns_200(self, client):
        """GET /login should return 200 OK."""
        res = client.get('/login')
        assert res.status_code == 200
        assert b'Login' in res.data or b'login' in res.data

    def test_get_login_redirects_to_todos_if_logged_in(self, logged_in_client):
        """GET /login should redirect to /todos if user is already logged in."""
        res = logged_in_client.get('/login')
        assert res.status_code == 302
        assert res.headers['Location'].endswith('/todos')


class TestIndexRoute:
    """Tests for GET / (index) endpoint."""

    def test_index_redirects_to_login_when_not_logged_in(self, client):
        """GET / should redirect to /login when user is not logged in."""
        res = client.get('/')
        assert res.status_code == 302
        assert res.headers['Location'].endswith('/login')

    def test_index_redirects_to_todos_when_logged_in(self, logged_in_client):
        """GET / should redirect to /todos when user is logged in."""
        res = logged_in_client.get('/')
        assert res.status_code == 302
        assert res.headers['Location'].endswith('/todos')


class TestRegisterValidation:
    """Tests for POST /register validation."""

    def test_register_username_too_short(self, client, patched_get_db_connection):
        """POST /register with username < 3 chars should show error."""
        res = client.post('/register', data={
            'username': 'ab',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        assert res.status_code == 200
        assert b'Username must be at least 3 characters' in res.data

    def test_register_invalid_email(self, client, patched_get_db_connection):
        """POST /register with invalid email should show error."""
        res = client.post('/register', data={
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        assert res.status_code == 200
        assert b'valid email' in res.data

    def test_register_password_too_short(self, client, patched_get_db_connection):
        """POST /register with password < 6 chars should show error."""
        res = client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'short',
            'confirm_password': 'short'
        })
        assert res.status_code == 200
        assert b'Password must be at least 6 characters' in res.data

    def test_register_passwords_do_not_match(self, client, patched_get_db_connection):
        """POST /register with mismatched passwords should show error."""
        res = client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password456'
        })
        assert res.status_code == 200
        assert b'Passwords do not match' in res.data


class TestRegisterSuccess:
    """Tests for successful registration."""

    def test_register_valid_data_redirects_to_login(self, client, patched_get_db_connection):
        """POST /register with valid data should redirect to /login."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        # Mock no existing user
        mock_cursor.fetchone.return_value = None
        
        res = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert res.status_code == 302
        assert res.headers['Location'].endswith('/login')
        
        # Verify the INSERT was called
        assert mock_cursor.execute.call_count >= 2  # First for check, second for insert
        mock_db_connection.commit.assert_called()


class TestRegisterDuplicates:
    """Tests for duplicate user handling during registration."""

    def test_register_duplicate_username(self, client, patched_get_db_connection):
        """POST /register with existing username should show error."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        # Mock existing user
        mock_cursor.fetchone.return_value = {'id': 1, 'username': 'testuser'}
        
        res = client.post('/register', data={
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert res.status_code == 200
        assert b'Username or email already exists' in res.data

    def test_register_duplicate_email(self, client, patched_get_db_connection):
        """POST /register with existing email should show error."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        # Mock existing user
        mock_cursor.fetchone.return_value = {'id': 1, 'email': 'test@example.com'}
        
        res = client.post('/register', data={
            'username': 'newuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert res.status_code == 200
        assert b'Username or email already exists' in res.data


class TestRegisterDatabaseFailure:
    """Tests for database failures during registration."""

    def test_register_connection_fails(self, client, patched_get_db_connection_none):
        """POST /register when DB connection fails should show error."""
        res = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert res.status_code == 200
        assert b'Database connection failed' in res.data


class TestLoginValidation:
    """Tests for POST /login validation."""

    def test_login_missing_email(self, client, patched_get_db_connection):
        """POST /login with missing email should show error."""
        res = client.post('/login', data={
            'email': '',
            'password': 'password123'
        })
        assert res.status_code == 200
        assert b'fill in all fields' in res.data or b'Please fill in all fields' in res.data

    def test_login_missing_password(self, client, patched_get_db_connection):
        """POST /login with missing password should show error."""
        res = client.post('/login', data={
            'email': 'test@example.com',
            'password': ''
        })
        assert res.status_code == 200
        assert b'fill in all fields' in res.data or b'Please fill in all fields' in res.data

    def test_login_missing_both_fields(self, client, patched_get_db_connection):
        """POST /login with both fields missing should show error."""
        res = client.post('/login', data={
            'email': '',
            'password': ''
        })
        assert res.status_code == 200
        assert b'fill in all fields' in res.data or b'Please fill in all fields' in res.data


class TestLoginSuccess:
    """Tests for successful login."""

    def test_login_valid_credentials(self, client, patched_get_db_connection):
        """POST /login with valid credentials should set session and redirect."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        # Mock user in database
        hashed_pw = generate_password_hash('password123')
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'password': hashed_pw
        }
        
        res = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        assert res.status_code == 302
        assert res.headers['Location'].endswith('/todos')
        
        # Verify session was set
        with client.session_transaction() as sess:
            assert sess['user_id'] == 1
            assert sess['username'] == 'testuser'

    def test_login_shows_success_message(self, client, patched_get_db_connection):
        """POST /login with valid credentials should show welcome message."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        hashed_pw = generate_password_hash('password123')
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'password': hashed_pw
        }
        
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        # Follow redirect and check for message
        res = client.get('/todos')
        assert res.status_code == 200
        assert b'Welcome back' in res.data or b'testuser' in res.data


class TestLoginFailure:
    """Tests for failed login attempts."""

    def test_login_user_not_found(self, client, patched_get_db_connection):
        """POST /login with non-existent email should show error."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        # Mock no user found
        mock_cursor.fetchone.return_value = None
        
        res = client.post('/login', data={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        })
        
        assert res.status_code == 200
        assert b'Invalid email or password' in res.data

    def test_login_wrong_password(self, client, patched_get_db_connection):
        """POST /login with wrong password should show error."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        # Mock user with correct hash
        correct_hash = generate_password_hash('correct_password')
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'password': correct_hash
        }
        
        res = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'wrong_password'
        })
        
        assert res.status_code == 200
        assert b'Invalid email or password' in res.data
        
        # Verify session was not set
        with client.session_transaction() as sess:
            assert 'user_id' not in sess


class TestLoginDatabaseFailure:
    """Tests for database failures during login."""

    def test_login_connection_fails(self, client, patched_get_db_connection_none):
        """POST /login when DB connection fails should show error."""
        res = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        assert res.status_code == 200
        assert b'Database connection failed' in res.data


class TestLogout:
    """Tests for GET /logout endpoint."""

    def test_logout_clears_session(self, logged_in_client):
        """GET /logout should clear the session."""
        # Verify session is set before logout
        with logged_in_client.session_transaction() as sess:
            assert sess['user_id'] == 1
            assert sess['username'] == 'testuser'
        
        # Logout
        res = logged_in_client.get('/logout')
        
        assert res.status_code == 302
        assert res.headers['Location'].endswith('/login')
        
        # Verify session is cleared
        with logged_in_client.session_transaction() as sess:
            assert 'user_id' not in sess
            assert 'username' not in sess

    def test_logout_redirects_to_login(self, logged_in_client):
        """GET /logout should redirect to /login."""
        res = logged_in_client.get('/logout')
        assert res.status_code == 302
        assert res.headers['Location'].endswith('/login')

    def test_logout_shows_message(self, logged_in_client):
        """GET /logout should show logged out message."""
        logged_in_client.get('/logout')
        res = logged_in_client.get('/login')
        assert b'logged out' in res.data.lower() or b'You have been logged out' in res.data
