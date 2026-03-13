from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import pymysql
pymysql.install_as_MySQLdb()

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# MySQL Configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'todo_app')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


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
            return render_template('register.html')

        try:
            cur = mysql.connection.cursor()
            # Check duplicates
            cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            existing = cur.fetchone()
            if existing:
                flash('Username or email already exists.', 'error')
                cur.close()
                return render_template('register.html')

            hashed_pw = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_pw)
            )
            mysql.connection.commit()
            cur.close()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('An error occurred. Please try again.', 'error')
            print(f"Register error: {e}")

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
            return render_template('login.html')

        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash(f"Welcome back, {user['username']}!", 'success')
                return redirect(url_for('todos'))
            else:
                flash('Invalid email or password.', 'error')
        except Exception as e:
            flash('An error occurred. Please try again.', 'error')
            print(f"Login error: {e}")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# ─── Todo Routes ─────────────────────────────────────────────────────────────

@app.route('/todos')
@login_required
def todos():
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM todos WHERE user_id = %s ORDER BY is_completed ASC, created_at DESC",
        (session['user_id'],)
    )
    todo_list = cur.fetchall()
    cur.close()
    return render_template('todos.html', todos=todo_list)


@app.route('/todos/add', methods=['POST'])
@login_required
def add_todo():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    priority = request.form.get('priority', 'medium')
    due_date = request.form.get('due_date') or None

    if not title:
        flash('Task title is required.', 'error')
        return redirect(url_for('todos'))

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO todos (user_id, title, description, priority, due_date) VALUES (%s, %s, %s, %s, %s)",
        (session['user_id'], title, description, priority, due_date)
    )
    mysql.connection.commit()
    cur.close()
    flash('Task added!', 'success')
    return redirect(url_for('todos'))


@app.route('/todos/toggle/<int:todo_id>')
@login_required
def toggle_todo(todo_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE todos SET is_completed = NOT is_completed WHERE id = %s AND user_id = %s",
        (todo_id, session['user_id'])
    )
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('todos'))


@app.route('/todos/delete/<int:todo_id>')
@login_required
def delete_todo(todo_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM todos WHERE id = %s AND user_id = %s", (todo_id, session['user_id']))
    mysql.connection.commit()
    cur.close()
    flash('Task deleted.', 'success')
    return redirect(url_for('todos'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
