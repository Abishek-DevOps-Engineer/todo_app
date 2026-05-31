from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# Configure Logging
if not os.path.exists('logs'):
    os.mkdir('logs')

file_handler = RotatingFileHandler('logs/todo_app.log', maxBytes=10240000, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s'
))
console_handler.setLevel(logging.WARNING)

app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Todo App started')

# MySQL Configuration
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'todo_app')
}

def get_db_connection():
    try:
        app.logger.debug(f"Attempting database connection to {MYSQL_CONFIG['host']}")
        return mysql.connector.connect(**MYSQL_CONFIG)
    except Error as e:
        app.logger.error(f"Database connection error: {e}", exc_info=True)
        return None


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ─── Auth Routes ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('todos'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('todos'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm_password:
            errors.append('Passwords do not match.')

        if errors:
            for error in errors:
                flash(error, 'error')
            app.logger.warning(f"Register validation failed for username: {username}. Errors: {errors}")
            return render_template('register.html')

        try:
            app.logger.info(f"Attempting registration for username: {username}")
            conn = get_db_connection()
            if not conn:
                flash('Database connection failed.', 'error')
                app.logger.error(f"Failed to register {username}: Database connection failed")
                return render_template('register.html')
            
            cur = conn.cursor(dictionary=True)
            # Check duplicates
            cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            existing = cur.fetchone()
            if existing:
                flash('Username or email already exists.', 'error')
                app.logger.warning(f"Registration failed: Username or email already exists. Username: {username}, Email: {email}")
                cur.close()
                conn.close()
                return render_template('register.html')

            hashed_pw = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_pw)
            )
            conn.commit()
            cur.close()
            conn.close()
            app.logger.info(f"User registered successfully: {username}")
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('An error occurred. Please try again.', 'error')
            app.logger.error(f"Register error for username {username}: {str(e)}", exc_info=True)

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('todos'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please fill in all fields.', 'error')
            app.logger.warning("Login attempt with missing fields")
            return render_template('login.html')

        try:
            app.logger.info(f"Login attempt for email: {email}")
            conn = get_db_connection()
            if not conn:
                flash('Database connection failed.', 'error')
                app.logger.error(f"Login failed for {email}: Database connection failed")
                return render_template('login.html')
            
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()
            conn.close()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                app.logger.info(f"Successful login for user: {user['username']} (ID: {user['id']})")
                flash(f"Welcome back, {user['username']}!", 'success')
                return redirect(url_for('todos'))
            else:
                app.logger.warning(f"Failed login attempt for email: {email} (invalid credentials)")
                flash('Invalid email or password.', 'error')
        except Exception as e:
            flash('An error occurred. Please try again.', 'error')
            app.logger.error(f"Login error for email {email}: {str(e)}", exc_info=True)

    return render_template('login.html')


@app.route('/logout')
def logout():
    username = session.get('username', 'Unknown')
    user_id = session.get('user_id', 'Unknown')
    session.clear()
    app.logger.info(f"User logged out: {username} (ID: {user_id})")
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# ─── Todo Routes ─────────────────────────────────────────────────────────────

@app.route('/todos')
@login_required
def todos():
    try:
        app.logger.debug(f"Fetching todos for user_id: {session['user_id']}")
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed.', 'error')
            app.logger.error(f"Failed to fetch todos for user {session['user_id']}: Database connection failed")
            return render_template('todos.html', todos=[])
        
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM todos WHERE user_id = %s ORDER BY is_completed ASC, created_at DESC",
            (session['user_id'],)
        )
        todo_list = cur.fetchall()
        cur.close()
        conn.close()
        app.logger.debug(f"Retrieved {len(todo_list)} todos for user {session['user_id']}")
        return render_template('todos.html', todos=todo_list)
    except Exception as e:
        app.logger.error(f"Error fetching todos for user {session['user_id']}: {str(e)}", exc_info=True)
        flash('An error occurred while fetching your tasks.', 'error')
        return render_template('todos.html', todos=[])


@app.route('/todos/add', methods=['POST'])
@login_required
def add_todo():
    try:
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'medium')
        due_date = request.form.get('due_date') or None

        if not title:
            flash('Task name is required.', 'error')
            app.logger.warning(f"Add todo failed for user {session['user_id']}: Missing task title")
            return redirect(url_for('todos'))

        app.logger.info(f"Adding todo for user {session['user_id']}: {title}")
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed.', 'error')
            app.logger.error(f"Add todo failed for user {session['user_id']}: Database connection failed")
            return redirect(url_for('todos'))
        
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO todos (user_id, title, description, priority, due_date) VALUES (%s, %s, %s, %s, %s)",
            (session['user_id'], title, description, priority, due_date)
        )
        conn.commit()
        cur.close()
        conn.close()
        app.logger.info(f"Todo added successfully for user {session['user_id']}: {title}")
        flash('Task added!', 'success')
        return redirect(url_for('todos'))
    except Exception as e:
        app.logger.error(f"Error adding todo for user {session['user_id']}: {str(e)}", exc_info=True)
        flash('An error occurred while adding the task.', 'error')
        return redirect(url_for('todos'))


@app.route('/todos/toggle/<int:todo_id>')
@login_required
def toggle_todo(todo_id):
    try:
        app.logger.info(f"Toggling todo {todo_id} for user {session['user_id']}")
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed.', 'error')
            app.logger.error(f"Toggle todo failed for user {session['user_id']}: Database connection failed")
            return redirect(url_for('todos'))
        
        cur = conn.cursor()
        cur.execute(
            "UPDATE todos SET is_completed = NOT is_completed WHERE id = %s AND user_id = %s",
            (todo_id, session['user_id'])
        )
        conn.commit()
        cur.close()
        conn.close()
        app.logger.info(f"Todo {todo_id} toggled successfully for user {session['user_id']}")
        return redirect(url_for('todos'))
    except Exception as e:
        app.logger.error(f"Error toggling todo {todo_id} for user {session['user_id']}: {str(e)}", exc_info=True)
        flash('An error occurred while updating the task.', 'error')
        return redirect(url_for('todos'))


@app.route('/todos/delete/<int:todo_id>')
@login_required
def delete_todo(todo_id):
    try:
        app.logger.info(f"Deleting todo {todo_id} for user {session['user_id']}")
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed.', 'error')
            app.logger.error(f"Delete todo failed for user {session['user_id']}: Database connection failed")
            return redirect(url_for('todos'))
        
        cur = conn.cursor()
        cur.execute("DELETE FROM todos WHERE id = %s AND user_id = %s", (todo_id, session['user_id']))
        conn.commit()
        cur.close()
        conn.close()
        app.logger.info(f"Todo {todo_id} deleted successfully for user {session['user_id']}")
        flash('Task deleted.', 'success')
        return redirect(url_for('todos'))
    except Exception as e:
        app.logger.error(f"Error deleting todo {todo_id} for user {session['user_id']}: {str(e)}", exc_info=True)
        flash('An error occurred while deleting the task.', 'error')
        return redirect(url_for('todos'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
