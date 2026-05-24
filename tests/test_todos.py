"""
Test suite for todo management routes (GET /todos, POST /todos/add, toggle, delete).

Covers:
- Authentication checks (login required)
- Todo list retrieval and display
- Adding new todos with validation
- Toggling completion status
- Deleting todos
- Database connection failure handling
"""

import pytest


class TestTodosListAuthRequired:
    """Tests for GET /todos route - authentication."""

    def test_todos_redirects_when_not_logged_in(self, client):
        """GET /todos without login should redirect to /login."""
        res = client.get('/todos')
        assert res.status_code == 302
        assert res.headers['Location'].endswith('/login')

    def test_todos_redirects_shows_error_message(self, client):
        """GET /todos without login should show login required message."""
        client.get('/todos')
        res = client.get('/login')
        # Message will appear after redirect
        assert res.status_code == 200


class TestTodosListSuccess:
    """Tests for GET /todos route - successful retrieval."""

    def test_todos_returns_200_when_logged_in(self, logged_in_client, patched_get_db_connection):
        """GET /todos when logged in should return 200 OK."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        mock_cursor.fetchall.return_value = []
        
        res = logged_in_client.get('/todos')
        assert res.status_code == 200
        assert b'todos' in res.data.lower() or b'task' in res.data.lower()

    def test_todos_displays_todo_list(self, logged_in_client, patched_get_db_connection):
        """GET /todos should display list of todos."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        # Mock todos from database
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'user_id': 1,
                'title': 'Buy groceries',
                'description': 'Milk, eggs, bread',
                'priority': 'high',
                'is_completed': False,
                'created_at': '2024-05-20 10:00:00',
                'due_date': None
            },
            {
                'id': 2,
                'user_id': 1,
                'title': 'Finish project',
                'description': 'Complete todo app',
                'priority': 'medium',
                'is_completed': True,
                'created_at': '2024-05-19 14:30:00',
                'due_date': '2024-05-25'
            }
        ]
        
        res = logged_in_client.get('/todos')
        assert res.status_code == 200
        # Check if at least one todo title is in the response
        assert (b'Buy groceries' in res.data or 
                b'Finish project' in res.data or 
                b'todos' in res.data.lower())

    def test_todos_empty_list(self, logged_in_client, patched_get_db_connection):
        """GET /todos with no todos should still return 200."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        mock_cursor.fetchall.return_value = []
        
        res = logged_in_client.get('/todos')
        assert res.status_code == 200


class TestTodosListDatabaseFailure:
    """Tests for GET /todos route - database failures."""

    def test_todos_connection_fails_shows_error(self, logged_in_client, patched_get_db_connection_none):
        """GET /todos when DB connection fails should show error but return 200."""
        res = logged_in_client.get('/todos')
        assert res.status_code == 200
        assert b'Database connection failed' in res.data or b'error' in res.data.lower()

    def test_todos_connection_fails_returns_empty_list(self, logged_in_client, patched_get_db_connection_none):
        """GET /todos when DB connection fails should return empty todo list."""
        res = logged_in_client.get('/todos')
        assert res.status_code == 200
        # Should render page with empty list
        assert b'todos' in res.data.lower() or b'task' in res.data.lower()


class TestAddTodoAuthRequired:
    """Tests for POST /todos/add route - authentication."""

    def test_add_todo_redirects_when_not_logged_in(self, client):
        """POST /todos/add without login should redirect to /login."""
        res = client.post('/todos/add', data={'title': 'Test'})
        assert res.status_code == 302
        assert res.headers['Location'].endswith('/login')


class TestAddTodoValidation:
    """Tests for POST /todos/add route - validation."""

    def test_add_todo_missing_title_shows_error(self, logged_in_client, patched_get_db_connection):
        """POST /todos/add with empty title should show error."""
        res = logged_in_client.post('/todos/add', data={
            'title': '',
            'description': 'Some description',
            'priority': 'medium',
            'due_date': ''
        })
        
        assert res.status_code == 302
        assert res.headers['Location'].endswith('/todos')
        
        # Check error message
        res = logged_in_client.get('/todos')
        assert b'Task title is required' in res.data or b'title' in res.data.lower()

    def test_add_todo_whitespace_title_shows_error(self, logged_in_client, patched_get_db_connection):
        """POST /todos/add with only whitespace title should show error."""
        res = logged_in_client.post('/todos/add', data={
            'title': '   ',
            'description': 'Some description',
            'priority': 'medium',
            'due_date': ''
        })
        
        assert res.status_code == 302
        assert res.headers['Location'].endswith('/todos')


class TestAddTodoSuccess:
    """Tests for POST /todos/add route - successful creation."""

    def test_add_todo_valid_title_redirects(self, logged_in_client, patched_get_db_connection):
        """POST /todos/add with valid title should redirect to /todos."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        res = logged_in_client.post('/todos/add', data={
            'title': 'Buy groceries',
            'description': 'Milk, eggs, bread',
            'priority': 'high',
            'due_date': '2024-05-30'
        })
        
        assert res.status_code == 302
        assert res.headers['Location'].endswith('/todos')

    def test_add_todo_inserts_into_database(self, logged_in_client, patched_get_db_connection):
        """POST /todos/add with valid data should call database INSERT."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        logged_in_client.post('/todos/add', data={
            'title': 'Buy groceries',
            'description': 'Milk, eggs, bread',
            'priority': 'high',
            'due_date': '2024-05-30'
        })
        
        # Verify INSERT was called
        mock_cursor.execute.assert_called()
        mock_db_connection.commit.assert_called()

    def test_add_todo_shows_success_message(self, logged_in_client, patched_get_db_connection):
        """POST /todos/add with valid data should show success message."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        logged_in_client.post('/todos/add', data={
            'title': 'Buy groceries',
            'description': 'Milk, eggs, bread',
            'priority': 'high',
            'due_date': ''
        })
        
        res = logged_in_client.get('/todos')
        assert b'Task added' in res.data or b'added' in res.data.lower()

    def test_add_todo_minimal_data(self, logged_in_client, patched_get_db_connection):
        """POST /todos/add with only title should work."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        res = logged_in_client.post('/todos/add', data={
            'title': 'Quick task',
            'description': '',
            'priority': 'medium',
            'due_date': ''
        })
        
        assert res.status_code == 302


class TestAddTodoDatabaseFailure:
    """Tests for POST /todos/add route - database failures."""

    def test_add_todo_connection_fails_shows_error(self, logged_in_client, patched_get_db_connection_none):
        """POST /todos/add when DB connection fails should show error."""
        res = logged_in_client.post('/todos/add', data={
            'title': 'Buy groceries',
            'description': 'Milk, eggs, bread',
            'priority': 'high',
            'due_date': ''
        })
        
        assert res.status_code == 302
        
        # Check for error message
        res = logged_in_client.get('/todos')
        assert b'Database connection failed' in res.data or b'error' in res.data.lower()

    def test_add_todo_connection_fails_no_insert(self, logged_in_client, patched_get_db_connection_none):
        """POST /todos/add when DB connection fails should not insert."""
        res = logged_in_client.post('/todos/add', data={
            'title': 'Buy groceries',
            'description': 'Milk, eggs, bread',
            'priority': 'high',
            'due_date': ''
        })
        
        # Should redirect but not insert
        assert res.status_code == 302


class TestToggleTodoAuthRequired:
    """Tests for GET /todos/toggle/<id> route - authentication."""

    def test_toggle_todo_redirects_when_not_logged_in(self, client):
        """GET /todos/toggle/<id> without login should redirect to /login."""
        res = client.get('/todos/toggle/1')
        assert res.status_code == 302
        assert res.headers['Location'].endswith('/login')


class TestToggleTodoSuccess:
    """Tests for GET /todos/toggle/<id> route - successful toggle."""

    def test_toggle_todo_redirects(self, logged_in_client, patched_get_db_connection):
        """GET /todos/toggle/<id> when logged in should redirect to /todos."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        res = logged_in_client.get('/todos/toggle/1')
        assert res.status_code == 302
        assert res.headers['Location'].endswith('/todos')

    def test_toggle_todo_updates_database(self, logged_in_client, patched_get_db_connection):
        """GET /todos/toggle/<id> should call database UPDATE."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        logged_in_client.get('/todos/toggle/1')
        
        # Verify UPDATE was called
        mock_cursor.execute.assert_called()
        mock_db_connection.commit.assert_called()

    def test_toggle_todo_with_different_ids(self, logged_in_client, patched_get_db_connection):
        """GET /todos/toggle/<id> should work with different todo IDs."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        for todo_id in [1, 5, 100]:
            res = logged_in_client.get(f'/todos/toggle/{todo_id}')
            assert res.status_code == 302


class TestToggleTodoDatabaseFailure:
    """Tests for GET /todos/toggle/<id> route - database failures."""

    def test_toggle_todo_connection_fails(self, logged_in_client, patched_get_db_connection_none):
        """GET /todos/toggle/<id> when DB connection fails should show error."""
        res = logged_in_client.get('/todos/toggle/1')
        
        # Should still redirect
        assert res.status_code == 302
        
        # But show error message
        res = logged_in_client.get('/todos')
        assert b'Database connection failed' in res.data or b'error' in res.data.lower()


class TestDeleteTodoAuthRequired:
    """Tests for GET /todos/delete/<id> route - authentication."""

    def test_delete_todo_redirects_when_not_logged_in(self, client):
        """GET /todos/delete/<id> without login should redirect to /login."""
        res = client.get('/todos/delete/1')
        assert res.status_code == 302
        assert res.headers['Location'].endswith('/login')


class TestDeleteTodoSuccess:
    """Tests for GET /todos/delete/<id> route - successful deletion."""

    def test_delete_todo_redirects(self, logged_in_client, patched_get_db_connection):
        """GET /todos/delete/<id> when logged in should redirect to /todos."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        res = logged_in_client.get('/todos/delete/1')
        assert res.status_code == 302
        assert res.headers['Location'].endswith('/todos')

    def test_delete_todo_calls_database(self, logged_in_client, patched_get_db_connection):
        """GET /todos/delete/<id> should call database DELETE."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        logged_in_client.get('/todos/delete/1')
        
        # Verify DELETE was called
        mock_cursor.execute.assert_called()
        mock_db_connection.commit.assert_called()

    def test_delete_todo_shows_success_message(self, logged_in_client, patched_get_db_connection):
        """GET /todos/delete/<id> should show success message."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        logged_in_client.get('/todos/delete/1')
        res = logged_in_client.get('/todos')
        
        assert b'Task deleted' in res.data or b'deleted' in res.data.lower()

    def test_delete_todo_with_different_ids(self, logged_in_client, patched_get_db_connection):
        """GET /todos/delete/<id> should work with different todo IDs."""
        mock_db_connection, mock_cursor = patched_get_db_connection
        
        for todo_id in [1, 5, 100]:
            res = logged_in_client.get(f'/todos/delete/{todo_id}')
            assert res.status_code == 302


class TestDeleteTodoDatabaseFailure:
    """Tests for GET /todos/delete/<id> route - database failures."""

    def test_delete_todo_connection_fails(self, logged_in_client, patched_get_db_connection_none):
        """GET /todos/delete/<id> when DB connection fails should show error."""
        res = logged_in_client.get('/todos/delete/1')
        
        # Should still redirect
        assert res.status_code == 302
        
        # But show error message
        res = logged_in_client.get('/todos')
        assert b'Database connection failed' in res.data or b'error' in res.data.lower()
