# Taska Todo App - Test Suite Guide

## Overview

A comprehensive pytest test suite for the Taska Flask + MySQL todo application. The suite includes **40+ test cases** covering authentication, authorization, input validation, database operations, and error handling.

## Test Structure

```
tests/
├── __init__.py          # Package marker
├── conftest.py          # Pytest fixtures and configuration
├── test_auth.py         # Authentication & authorization tests (20+ tests)
└── test_todos.py        # Todo CRUD operations tests (20+ tests)
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pytest==8.1.1` - Testing framework
- `pytest-mock==3.14.0` - Mocking utilities

### 2. Configure Environment

Ensure you have a `.env` file in the root directory with the following (tests will mock the database, so these can be any values):

```env
SECRET_KEY=test-secret-key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DB=todo_app
```

## Running Tests

### Run All Tests

```bash
pytest
```

Output with verbose results:
```bash
pytest -v
```

### Run Specific Test File

```bash
# Auth tests only
pytest tests/test_auth.py -v

# Todo tests only
pytest tests/test_todos.py -v
```

### Run Specific Test Class

```bash
pytest tests/test_auth.py::TestLoginSuccess -v
```

### Run Specific Test Function

```bash
pytest tests/test_auth.py::test_login_valid_credentials -v
```

### Run with Coverage Report

```bash
pytest --cov=. --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`

## Test Coverage

### test_auth.py (20+ tests)

#### Registration Tests
- ✅ GET /register page loads (200)
- ✅ GET /register redirects if already logged in
- ✅ POST /register validates username length (min 3 chars)
- ✅ POST /register validates email format
- ✅ POST /register validates password length (min 6 chars)
- ✅ POST /register validates matching passwords
- ✅ POST /register rejects duplicate usernames
- ✅ POST /register rejects duplicate emails
- ✅ POST /register succeeds with valid data
- ✅ POST /register handles database connection failure

#### Login Tests
- ✅ GET /login page loads (200)
- ✅ GET /login redirects if already logged in
- ✅ POST /login validates email field required
- ✅ POST /login validates password field required
- ✅ POST /login succeeds with valid credentials
- ✅ POST /login sets session data
- ✅ POST /login shows welcome message
- ✅ POST /login rejects non-existent email
- ✅ POST /login rejects wrong password
- ✅ POST /login handles database connection failure

#### Logout Tests
- ✅ GET /logout clears session
- ✅ GET /logout redirects to /login
- ✅ GET /logout shows success message

#### Index/Home Route Tests
- ✅ GET / redirects to /login when not logged in
- ✅ GET / redirects to /todos when logged in

### test_todos.py (20+ tests)

#### Todo List Tests
- ✅ GET /todos redirects to /login when not authenticated
- ✅ GET /todos returns 200 when logged in
- ✅ GET /todos displays todo items
- ✅ GET /todos handles empty list
- ✅ GET /todos handles database connection failure

#### Add Todo Tests
- ✅ POST /todos/add redirects to /login when not authenticated
- ✅ POST /todos/add validates title is required
- ✅ POST /todos/add rejects empty/whitespace titles
- ✅ POST /todos/add succeeds with valid title
- ✅ POST /todos/add inserts into database
- ✅ POST /todos/add shows success message
- ✅ POST /todos/add works with minimal data
- ✅ POST /todos/add handles database connection failure

#### Toggle Todo Tests
- ✅ GET /todos/toggle/<id> redirects to /login when not authenticated
- ✅ GET /todos/toggle/<id> succeeds and redirects
- ✅ GET /todos/toggle/<id> calls database UPDATE
- ✅ GET /todos/toggle/<id> works with different IDs
- ✅ GET /todos/toggle/<id> handles database connection failure

#### Delete Todo Tests
- ✅ GET /todos/delete/<id> redirects to /login when not authenticated
- ✅ GET /todos/delete/<id> succeeds and redirects
- ✅ GET /todos/delete/<id> calls database DELETE
- ✅ GET /todos/delete/<id> shows success message
- ✅ GET /todos/delete/<id> works with different IDs
- ✅ GET /todos/delete/<id> handles database connection failure

## Key Testing Patterns

### 1. Mocked Database Connection

All tests use **mocked MySQL connections** - no real database required:

```python
def test_login_valid_credentials(client, patched_get_db_connection):
    mock_db_connection, mock_cursor = patched_get_db_connection
    mock_cursor.fetchone.return_value = {
        'id': 1,
        'username': 'testuser',
        'password': hashed_password
    }
    # Test code...
```

### 2. Simulated Login Sessions

Tests can simulate a logged-in user without database:

```python
def test_todos_with_logged_in_user(logged_in_client, patched_get_db_connection):
    # logged_in_client automatically sets session['user_id'] = 1
    res = logged_in_client.get('/todos')
    assert res.status_code == 200
```

### 3. Database Failure Simulation

Tests verify error handling when database is unavailable:

```python
def test_add_todo_connection_fails(logged_in_client, patched_get_db_connection_none):
    # patched_get_db_connection_none makes get_db_connection() return None
    res = logged_in_client.post('/todos/add', data={'title': 'Test'})
    assert b'Database connection failed' in logged_in_client.get('/todos').data
```

### 4. Flash Message Verification

Tests check Flask flash messages appear in rendered HTML:

```python
def test_login_shows_error(client, patched_get_db_connection):
    res = client.post('/login', data={'email': 'test@example.com', 'password': 'wrong'})
    assert b'Invalid email or password' in res.data
```

### 5. Redirect Verification

Tests verify proper redirects with status codes:

```python
def test_register_redirects_to_login(client, patched_get_db_connection):
    res = client.post('/register', data={...})
    assert res.status_code == 302
    assert res.headers['Location'].endswith('/login')
```

## Fixtures Reference (conftest.py)

### `client`
Flask test client with `TESTING = True`.
```python
def test_something(client):
    res = client.get('/login')
```

### `logged_in_client`
Test client with a pre-authenticated session (`user_id=1`, `username='testuser'`).
```python
def test_todos(logged_in_client):
    res = logged_in_client.get('/todos')
```

### `patched_get_db_connection`
Mocked MySQL connection that returns configurable data.
```python
def test_login(client, patched_get_db_connection):
    mock_conn, mock_cursor = patched_get_db_connection
    mock_cursor.fetchone.return_value = {'id': 1, 'username': 'test'}
```

### `patched_get_db_connection_none`
Simulates database connection failure (returns None).
```python
def test_db_fail(logged_in_client, patched_get_db_connection_none):
    res = logged_in_client.get('/todos')
    assert b'Database connection failed' in res.data
```

### `mock_db_connection`, `mock_cursor`
Low-level mocks for custom test scenarios.
```python
def test_custom(client, mock_db_connection, mock_cursor):
    # Configure mocks as needed
```

## Common Test Patterns

### Testing Input Validation

```python
def test_register_username_too_short(client, patched_get_db_connection):
    res = client.post('/register', data={
        'username': 'ab',  # Too short
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert res.status_code == 200
    assert b'Username must be at least 3 characters' in res.data
```

### Testing Authentication Requirements

```python
def test_todos_requires_login(client):
    res = client.get('/todos')
    assert res.status_code == 302  # Redirect
    assert res.headers['Location'].endswith('/login')
```

### Testing Successful Database Operations

```python
def test_add_todo_success(logged_in_client, patched_get_db_connection):
    mock_db_connection, mock_cursor = patched_get_db_connection
    
    res = logged_in_client.post('/todos/add', data={'title': 'Test'})
    
    # Verify redirect
    assert res.status_code == 302
    
    # Verify database was called
    mock_cursor.execute.assert_called()
    mock_db_connection.commit.assert_called()
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'app'"
Ensure you're running pytest from the root directory (where `app.py` is located):
```bash
cd d:\Abishek\DEVOPS_EMC\Project\todo_app
pytest
```

### "pytest: command not found"
Install pytest first:
```bash
pip install -r requirements.txt
```

### Tests pass but database operations didn't happen
Tests use mocks by default. To verify database calls were made:
```python
mock_cursor.execute.assert_called()
mock_db_connection.commit.assert_called()
```

### Session not persisting across requests in tests
Use the same `client` instance across multiple requests:
```python
def test_session_persistence(logged_in_client):
    # Request 1
    res1 = logged_in_client.get('/todos')
    # Request 2 - session still active
    res2 = logged_in_client.post('/todos/add', data={...})
```

## Extending the Tests

To add more tests:

1. **For new routes**, add test functions to appropriate file
2. **For new validation**, add to validation test classes
3. **For edge cases**, create new test classes for grouping
4. **Follow naming convention**: `test_<feature>_<scenario>`

Example:
```python
def test_add_todo_with_special_characters(logged_in_client, patched_get_db_connection):
    """Test that special chars in todo title are handled safely."""
    mock_db_connection, mock_cursor = patched_get_db_connection
    
    res = logged_in_client.post('/todos/add', data={
        'title': "Buy \"eggs\" & 'bacon' <today>"
    })
    assert res.status_code == 302
```

## CI/CD Integration

For GitHub Actions or similar CI/CD:

```yaml
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=. --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

## Best Practices Used

✅ **No real database** - All tests use mocks  
✅ **Isolated tests** - Each test is independent  
✅ **Clear test names** - Function names describe what's tested  
✅ **Organized by feature** - Test classes group related tests  
✅ **Proper fixtures** - DRY principle with reusable fixtures  
✅ **Error scenarios** - Both success and failure paths tested  
✅ **Flash message checks** - User feedback verified  
✅ **Session management** - Authentication properly tested  

---

**Total Test Cases**: 40+ comprehensive tests
**Framework**: pytest with unittest.mock
**Coverage**: Auth, authorization, validation, CRUD, error handling
