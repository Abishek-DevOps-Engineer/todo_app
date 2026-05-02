# Flask Todo Application - Complete Flow Documentation

**Last Updated:** April 3, 2026  
**Purpose:** DevOps Engineer Reference - Understanding App Flow & MySQL Connections

---

## TABLE OF CONTENTS
1. [Architecture Overview](#architecture-overview)
2. [Startup Flow](#startup-flow)
3. [High-Level Application Flow](#high-level-application-flow)
4. [MySQL Connection Points](#mysql-connection-points)
5. [User Journey (Register → Login → Create Todos)](#user-journey)
6. [Database Schema](#database-schema)
7. [Requirements & Dependencies](#requirements-and-dependencies)
8. [Environment Configuration](#environment-configuration)
9. [Running the Application](#running-the-application)
10. [Key Concepts for DevOps](#key-concepts-for-devops)

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                             │
│                  (Web Interface - Port 5000)                    │
└────────────────────────────┬──────────────────────────────────┘
                             │
                    HTTP Request/Response
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│         FLASK APPLICATION SERVER (app.py)                       │
│              Running on localhost:5000                          │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  .env Configuration File                              │   │
│  │  (MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, etc.)      │   │
│  └────────────────────────────────────────────────────────┘   │
│           │                                                    │
│           │ load_dotenv() - Reads environment variables        │
│           ▼                                                    │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  MYSQL_CONFIG Dictionary                              │   │
│  │  Routes (Login, Register, Todos)                      │   │
│  │  get_db_connection() - Creates DB connections         │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────┬──────────────────────────────────────────────┘
                  │
         MySQL Connection (Port 3306)
         TCP/IP Connection String
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              MYSQL DATABASE (localhost:3306)                    │
│                                                                 │
│  Database: todo_app                                            │
│                                                                 │
│  Tables:                                                        │
│  ├─ users (id, username, email, password, created_at)         │
│  └─ todos (id, user_id, title, description, etc.)             │
└─────────────────────────────────────────────────────────────────┘
```

---

## STARTUP FLOW

```
1. Python Interpreter Starts
   │
   ├─ app.py executes line by line
   │
   ├─ Line 3: from dotenv import load_dotenv
   │   └─ Imports the dotenv module
   │
   ├─ Line 8: load_dotenv()
   │   └─ ✓ READS .env FILE from disk
   │   └─ Loads MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, SECRET_KEY
   │
   ├─ Line 10: app = Flask(__name__)
   │   └─ Creates Flask web application instance
   │
   ├─ Line 11: app.secret_key = os.getenv('SECRET_KEY', ...)
   │   └─ Sets encryption key for sessions (from .env or default)
   │
   ├─ Lines 13-20: MYSQL_CONFIG = {...}
   │   └─ Dictionary defined with database connection credentials
   │   └─ Values pulled from environment variables (set by .env)
   │
   ├─ Lines 23-27: def get_db_connection():
   │   └─ Function DEFINED (not executed yet)
   │
   └─ Lines 218-219: if __name__ == '__main__':
      └─ app.run(debug=True, host='0.0.0.0', port=5000)
         └─ ✓ SERVER STARTS - Listening on port 5000
         └─ Waiting for HTTP requests
```

---

## HIGH-LEVEL APPLICATION FLOW

```
START
  │
  ├─→ User opens browser: http://localhost:5000
  │
  ├─→ Flask checks: Is user logged in? (Check session cookie)
  │   │
  │   ├─YES─→ Redirect to /todos page
  │   │
  │   └─NO──→ Redirect to /login page
  │
  ├─→ User sees Login Form
  │   │
  │   ├─ Option 1: Login (POST /login)
  │   │   │
  │   │   ├─→ ✓ MYSQL CONNECTION #1
  │   │   │   └─ SELECT * FROM users WHERE email = ?
  │   │   │
  │   │   ├─→ Verify password
  │   │   │
  │   │   ├─→ If valid: Store user_id in session cookie
  │   │   │
  │   │   └─→ Redirect to /todos
  │   │
  │   └─ Option 2: Register (POST /register)
  │       │
  │       ├─→ Validate input (username length, email format, password match)
  │       │
  │       ├─→ ✓ MYSQL CONNECTION #2
  │       │   └─ SELECT FROM users (check if email/username exists)
  │       │
  │       ├─→ Hash password (Werkzeug security)
  │       │
  │       ├─→ ✓ MYSQL CONNECTION #3
  │       │   └─ INSERT INTO users (username, email, password)
  │       │
  │       └─→ Redirect to /login
  │
  ├─→ User logged in - Now at /todos page
  │   │
  │   ├─→ ✓ MYSQL CONNECTION #4
  │   │   └─ SELECT * FROM todos WHERE user_id = ? (Fetch user's todos)
  │   │
  │   ├─→ Display todos list with options
  │   │
  │   ├─ User can:
  │   │  │
  │   │  ├─ Add TODO (POST /todos/add)
  │   │  │  └─ ✓ MYSQL CONNECTION #5
  │   │  │     └─ INSERT INTO todos (...)
  │   │  │
  │   │  ├─ Toggle TODO (GET /todos/toggle/<id>)
  │   │  │  └─ ✓ MYSQL CONNECTION #6
  │   │  │     └─ UPDATE todos SET is_completed = NOT is_completed
  │   │  │
  │   │  ├─ Delete TODO (GET /todos/delete/<id>)
  │   │  │  └─ ✓ MYSQL CONNECTION #7
  │   │  │     └─ DELETE FROM todos WHERE id = ?
  │   │  │
  │   │  └─ Logout (GET /logout)
  │   │     └─ Clear session cookie
  │   │
  │   └─ Redirect to /login
  │
  └─ END
```

---

## MYSQL CONNECTION POINTS

### Connection Function (at app.py lines 23-27):

```python
def get_db_connection():
    try:
        return mysql.connector.connect(**MYSQL_CONFIG)
    except Error as e:
        print(f"Database connection error: {e}")
        return None
```

**How it works:**
- Uses `mysql.connector` library (from mysql-connector-python package)
- Connects using credentials from `.env` file
- Returns connection object if successful
- Returns None if connection fails

---

### CONNECTION POINT #1: LOGIN DATABASE QUERY (app.py ~line 135)

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()  # ✓ CONNECTS TO MYSQL HERE
        if not conn:
            flash('Database connection failed.')
            return render_template('login.html')
        
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()  # ✓ FETCHES USER FROM DATABASE
        
        cur.close()
        conn.close()  # ✓ CLOSES CONNECTION
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']  # Store in cookie
            return redirect(url_for('todos'))
```

**MySQL Flow:**
```
User submits login form
        ↓
get_db_connection() called
        ↓
mysql.connector.connect(**MYSQL_CONFIG)
        ↓
Connection established to MySQL (localhost:3306)
        ↓
SELECT query executed
        ↓
Cursor fetches result
        ↓
Connection closes (explicit)
```

---

### CONNECTION POINT #2: REGISTER - CHECK DUPLICATE (app.py ~line 88)

```python
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # VALIDATION
        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        # ... more validations ...
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        conn = get_db_connection()  # ✓ MYSQL CONNECTION HERE - CHECK DUPLICATES
        if not conn:
            return render_template('register.html')
        
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", 
                   (username, email))
        existing = cur.fetchone()  # Check if exists
```

**MySQL Flow:**
```
User receives register form
        ↓
Submits username, email, password
        ↓
Flask validates (length, format, etc.)
        ↓
get_db_connection() called
        ↓
SELECT query to check if email/username already exists
        ↓
If found: Return error message
If not found: Continue to insert
```

---

### CONNECTION POINT #3: REGISTER - INSERT NEW USER (app.py ~line 104)

```python
        # After checking duplicates...
        hashed_pw = generate_password_hash(password)
        cur.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_pw)
        )
        conn.commit()  # ✓ WRITES TO DATABASE
        cur.close()
        conn.close()
```

**MySQL Flow:**
```
Password hashed using Werkzeug
        ↓
INSERT query with: username, email, hashed_password
        ↓
conn.commit() WRITES data to MySQL
        ↓
Connection closes
        ↓
Redirect to login page
```

---

### CONNECTION POINT #4: FETCH TODOS FOR USER (app.py ~line 177)

```python
@app.route('/todos')
@login_required  # Decorator checks if user_id in session
def todos():
    conn = get_db_connection()  # ✓ MYSQL CONNECTION HERE
    if not conn:
        return render_template('todos.html', todos=[])
    
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM todos WHERE user_id = %s ORDER BY is_completed ASC, created_at DESC",
        (session['user_id'],)  # Use user_id from session cookie
    )
    todo_list = cur.fetchall()  # ✓ FETCHES ALL TODOS
    cur.close()
    conn.close()
    
    return render_template('todos.html', todos=todo_list)
```

**MySQL Flow:**
```
User navigates to /todos
        ↓
@login_required decorator checks session
        ↓
If no session → Redirect to login
If session exists → Continue
        ↓
get_db_connection() called
        ↓
SELECT * FROM todos WHERE user_id = [logged_in_user_id]
        ↓
Fetches all todos belonging to that user only
        ↓
Renders HTML page with todos
```

---

### CONNECTION POINT #5: ADD NEW TODO (app.py ~line 195)

```python
@app.route('/todos/add', methods=['POST'])
@login_required
def add_todo():
    title = request.form.get('title').strip()
    description = request.form.get('description').strip()
    priority = request.form.get('priority', 'medium')
    due_date = request.form.get('due_date') or None
    
    conn = get_db_connection()  # ✓ MYSQL CONNECTION HERE
    if not conn:
        return redirect(url_for('todos'))
    
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO todos (user_id, title, description, priority, due_date) VALUES (%s, %s, %s, %s, %s)",
        (session['user_id'], title, description, priority, due_date)
    )
    conn.commit()  # ✓ WRITES NEW TODO TO DATABASE
    cur.close()
    conn.close()
    
    flash('Task added!', 'success')
    return redirect(url_for('todos'))
```

**MySQL Flow:**
```
User fills add-todo form
        ↓
POST request to /todos/add
        ↓
Validate title is not empty
        ↓
get_db_connection() called
        ↓
INSERT INTO todos with: user_id, title, description, priority, due_date
        ↓
conn.commit() WRITES to database
        ↓
Redirect to /todos (show updated list)
```

---

### CONNECTION POINT #6: TOGGLE TODO COMPLETION (app.py ~line 215)

```python
@app.route('/todos/toggle/<int:todo_id>')
@login_required
def toggle_todo(todo_id):
    conn = get_db_connection()  # ✓ MYSQL CONNECTION HERE
    if not conn:
        return redirect(url_for('todos'))
    
    cur = conn.cursor()
    cur.execute(
        "UPDATE todos SET is_completed = NOT is_completed WHERE id = %s AND user_id = %s",
        (todo_id, session['user_id'])
    )
    conn.commit()  # ✓ UPDATES DATABASE
    cur.close()
    conn.close()
    
    return redirect(url_for('todos'))
```

**MySQL Flow:**
```
User clicks checkbox to mark todo as done
        ↓
Navigate to /todos/toggle/[todo_id]
        ↓
get_db_connection() called
        ↓
UPDATE query flips is_completed from 0 to 1 (or vice versa)
        ↓
Security: WHERE user_id = ? (prevents user from toggling others' todos)
        ↓
conn.commit() WRITES change
        ↓
Reload /todos page
```

---

### CONNECTION POINT #7: DELETE TODO (app.py ~line 229)

```python
@app.route('/todos/delete/<int:todo_id>')
@login_required
def delete_todo(todo_id):
    conn = get_db_connection()  # ✓ MYSQL CONNECTION HERE
    if not conn:
        return redirect(url_for('todos'))
    
    cur = conn.cursor()
    cur.execute("DELETE FROM todos WHERE id = %s AND user_id = %s", 
               (todo_id, session['user_id']))
    conn.commit()  # ✓ DELETES FROM DATABASE
    cur.close()
    conn.close()
    
    flash('Task deleted.', 'success')
    return redirect(url_for('todos'))
```

**MySQL Flow:**
```
User clicks delete button
        ↓
Navigate to /todos/delete/[todo_id]
        ↓
get_db_connection() called
        ↓
DELETE query removes todo from database
        ↓
Security: WHERE user_id = ? (only allows deleting own todos)
        ↓
conn.commit() WRITES deletion
        ↓
Reload /todos page with updated list
```

---

## USER JOURNEY

### JOURNEY FLOW DIAGRAM:

```
┌─────────────────────────────────────────────────────────────┐
│               STAGE 1: FIRST TIME USER                      │
└─────────────────────────────────────────────────────────────┘

1. Open browser → http://localhost:5000
   └─ Flask checks session (no user_id found)
   └─ Redirects to /login

2. At login page, click "Register"

3. Fill Registration Form:
   ├─ Username: john_doe
   ├─ Email: john@example.com
   ├─ Password: securepass123
   └─ Confirm Password: securepass123

4. Submit Form (POST /register)
   ├─ MYSQL CONNECTION #1: Check if email/username exists
   ├─ MYSQL CONNECTION #2: INSERT new user
   ├─ Password hashed before storing
   └─ Success page: "Account created! Please log in."

5. Click "Login" link

6. Fill Login Form:
   ├─ Email: john@example.com
   └─ Password: securepass123

7. Submit Form (POST /login)
   ├─ MYSQL CONNECTION #3: SELECT * FROM users WHERE email
   ├─ Password verification (check_password_hash)
   ├─ Store user_id in session cookie
   └─ Redirect to /todos


┌─────────────────────────────────────────────────────────────┐
│               STAGE 2: LOGGED IN - TODOS PAGE               │
└─────────────────────────────────────────────────────────────┘

8. Now at /todos page
   ├─ MYSQL CONNECTION #4: Fetch all user's todos
   └─ Display todo list with add/edit/delete options

9. Add a new todo:
   ├─ Title: "Buy groceries"
   ├─ Priority: "high"
   ├─ Due Date: 2026-04-10
   ├─ Click "Add Task"
   │
   └─ MYSQL CONNECTION #5: INSERT into todos table
      └─ user_id = 1 (from session)

10. Mark todo as complete:
    ├─ Click checkbox next to "Buy groceries"
    │
    └─ MYSQL CONNECTION #6: UPDATE is_completed = True

11. Delete a todo:
    ├─ Click delete button
    │
    └─ MYSQL CONNECTION #7: DELETE from todos table

12. Logout:
    ├─ Click "Logout" button
    ├─ Session cookie cleared (user_id removed)
    └─ Redirect to /login


┌─────────────────────────────────────────────────────────────┐
│               STAGE 3: RETURN VISITOR                       │
└─────────────────────────────────────────────────────────────┘

13. Open browser next day → http://localhost:5000
    └─ Flask checks session (cookie still valid if not expired)
    └─ MYSQL CONNECTION #4: Fetch todos
    └─ Shows user's todos directly (no need to login)
```

---

## DATABASE SCHEMA

### TABLE 1: USERS

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,           -- Stores hashed password
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Sample Data:**
```
id | username  | email              | password (hashed)              | created_at
1  | john_doe  | john@example.com   | pbkdf2:sha256:600000$...      | 2026-04-01
2  | jane_smith| jane@example.com   | pbkdf2:sha256:600000$...      | 2026-04-02
```

---

### TABLE 2: TODOS

```sql
CREATE TABLE todos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,                      -- Links to users table
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_completed BOOLEAN DEFAULT FALSE,
    priority ENUM('low', 'medium', 'high'),
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Sample Data:**
```
id | user_id | title          | description      | is_completed | priority | due_date   | created_at
1  | 1       | Buy groceries  | Milk, bread, eggs| FALSE        | high     | 2026-04-10 | 2026-04-03
2  | 1       | Complete report| Business proposal| TRUE         | high     | 2026-04-05 | 2026-04-02
3  | 2       | Walk dog       | Evening walk     | FALSE        | low      | 2026-04-04 | 2026-04-03
```

**Multi-Tenant Design:**
- Each todo belongs to exactly ONE user (user_id)
- User 1 only sees their own todos
- User 2 only sees their own todos
- Queries always filter: `WHERE user_id = ?`

---

## REQUIREMENTS AND DEPENDENCIES

### File: requirements.txt

```
Flask==3.0.0
mysql-connector-python==8.2.0
Flask-Login==0.6.3
Werkzeug==3.0.0
python-dotenv==1.0.0
```

### Installation:

```bash
pip install -r requirements.txt
```

### What Each Package Does:

| Package | Version | Purpose | DevOps Note |
|---------|---------|---------|-------------|
| **Flask** | 3.0.0 | Web framework, creates HTTP server, handles routes | Core app framework |
| **mysql-connector-python** | 8.2.0 | MySQL driver, connects Python to MySQL database | Required for DB connectivity |
| **Flask-Login** | 0.6.3 | User session management (login/logout) | Session handling |
| **Werkzeug** | 3.0.0 | Security utilities (password hashing/checking) | Password security |
| **python-dotenv** | 1.0.0 | Loads .env file into environment variables | Config management |

---

## ENVIRONMENT CONFIGURATION

### File: .env

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=test@123
MYSQL_DB=todo_app
SECRET_KEY=anyrandomstring123
```

### Variable Explanation:

| Variable | Value | Used For | Production Note |
|----------|-------|----------|-----------------|
| **MYSQL_HOST** | localhost | MySQL server address | Change to service name in Docker/K8s |
| **MYSQL_USER** | root | Database username | Use dedicated user in production |
| **MYSQL_PASSWORD** | test@123 | Database password | Use secrets management tool |
| **MYSQL_DB** | todo_app | Database name to use | Must exist before app starts |
| **SECRET_KEY** | anyrandomstring123 | Flask session encryption | Generate strong random key |

### How .env is Loaded:

```python
# app.py line 3
from dotenv import load_dotenv

# app.py line 8
load_dotenv()  # Reads .env file from disk

# app.py line 12-20
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),      # From .env
    'user': os.getenv('MYSQL_USER', 'root'),           # From .env
    'password': os.getenv('MYSQL_PASSWORD', ''),       # From .env
    'database': os.getenv('MYSQL_DB', 'todo_app')      # From .env
}
```

### Security Best Practices:

```
❌ NEVER commit .env to Git
✅ .env should be in .gitignore
✅ In production, use secrets management:
   - Docker: Use secrets/environment variables
   - Kubernetes: Use ConfigMaps and Secrets
   - Cloud: Use AWS Secrets Manager, Azure Key Vault, etc.
```

---

## RUNNING THE APPLICATION

### STEP 1: Verify Prerequisites

```bash
# Check Python version (need 3.7+)
python --version
# Output: Python 3.9.x

# Check pip (package manager)
pip --version
# Output: pip 24.x from ...

# Verify MySQL is running
mysql --version
# Output: mysql Ver 8.x

# Test MySQL connectivity
mysql -u root -p
# Password: test@123
# Should see: mysql>
# Exit with: exit
```

### STEP 2: Install Dependencies

```bash
# Navigate to project directory
cd d:\Abishek\DEVOPS_EMC\Project\todo_app

# Install all packages from requirements.txt
pip install -r requirements.txt

# Output should show:
# Collecting Flask==3.0.0
# Collecting mysql-connector-python==8.2.0
# ... [all packages downloaded and installed]
# Successfully installed Flask mysql-connector-python ...
```

### STEP 3: Setup Database

```bash
# Option A: Run schema.sql file
mysql -u root -p < schema.sql
# Password: test@123

# Option B: Manually in MySQL shell
mysql -u root -p
mysql> CREATE DATABASE IF NOT EXISTS todo_app;
mysql> USE todo_app;
mysql> [Paste contents of schema.sql]
mysql> exit
```

### STEP 4: Verify Configuration

```bash
# Check .env file exists and has correct values
cat .env
# Output should show:
# MYSQL_HOST=localhost
# MYSQL_USER=root
# MYSQL_PASSWORD=test@123
# MYSQL_DB=todo_app
# SECRET_KEY=anyrandomstring123
```

### STEP 5: Run the Application

```bash
# Start Flask development server
python app.py

# Output should show:
# WARNING: This is a development server. Do not use it in production
# Running on http://0.0.0.0:5000
# Press CTRL+C to quit
```

### STEP 6: Access the Application

```
Open browser: http://localhost:5000
Or: http://127.0.0.1:5000
Or: http://[your-machine-ip]:5000  (if accessing from another machine)

You should see login page
```

### STEP 7: Test the Application

```
1. Click "Register"
2. Fill form: username, email, password
3. Click "Register"
4. Login with credentials
5. Add some todos
6. Mark them complete
7. Delete some
8. Logout
```

### STEP 8: Stop the Server

```bash
# In terminal where server is running:
Press CTRL+C

# Output should show:
# * Shutting down Flask development server
```

---

## KEY CONCEPTS FOR DEVOPS

### 1. PACKAGE MANAGEMENT

**What:** `requirements.txt` specifies exact package versions  
**Why:** Ensures consistency across dev/staging/production  
**DevOps Action:** Generate lock file for production
```bash
pip freeze > requirements-lock.txt  # Creates exact versions
```

---

### 2. ENVIRONMENT CONFIGURATION

**What:** `.env` file holds environment-specific values  
**Why:** Same code works in dev/prod with different configs  
**DevOps Action:** Use secrets management in production
```
Dev:  .env with localhost credentials
Prod: Environment variables with real credentials
```

---

### 3. DATABASE CONNECTIONS

**What:** Each operation opens/closes a connection  
**Why:** Prevents connection leaks  
**DevOps Action:** Monitor connection pool in production
```python
conn = get_db_connection()  # Opens connection
# ... do work ...
conn.close()  # Closes connection
```

**Scalability Note:** In production with many users, connection pooling is recommended:
```python
# Production: Use connection pool instead of opening new connection each time
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **MYSQL_CONFIG
)
```

---

### 4. SECURITY LAYERS

**Layer 1: Password Hashing**
```python
from werkzeug.security import generate_password_hash
hashed = generate_password_hash("password123")  # Can't reverse
```

**Layer 2: Session Cookies**
```python
session['user_id'] = 1  # Encrypted with SECRET_KEY
```

**Layer 3: SQL Injection Prevention**
```python
# SAFE: Uses parameterized query
cur.execute("SELECT * FROM users WHERE email = %s", (email,))

# UNSAFE: String concatenation
cur.execute(f"SELECT * FROM users WHERE email = '{email}'")  # Vulnerable!
```

**Layer 4: Login Required Decorator**
```python
@login_required  # Checks session before allowing access
def todos():
    # Only logged-in users reach this code
```

---

### 5. ERROR HANDLING

**Connection Error:**
```python
conn = get_db_connection()
if not conn:
    flash('Database connection failed.', 'error')
    return render_template('login.html')
```

**Database Error:**
```python
try:
    conn = get_db_connection()
    # ... query ...
except Exception as e:
    print(f"Database error: {e}")
    flash('An error occurred.', 'error')
```

---

### 6. FILE STRUCTURE FOR DEPLOYMENT

```
todo_app/
├── app.py                 # Flask application (main entry point)
├── requirements.txt       # Python dependencies
├── .env                   # Environment config (NOT in Git)
├── .gitignore            # Tells Git to ignore .env
├── schema.sql            # Database setup script
├── dockerfile            # Container image definition
├── docker-compose.yaml   # Multi-container orchestration
├── templates/            # HTML files (rendered by Flask)
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   └── todos.html
└── static/               # Static files (CSS, JS, images)
    ├── css/
    │   └── main.css
    └── main.js
```

---

### 7. PERFORMANCE CONSIDERATIONS

**MySQL Connections:**
- Current: Opens/closes connection for each request
- Problem: Slow with many concurrent users
- Solution: Use connection pooling

**Template Rendering:**
- Flask caches compiled templates
- Static files served directly by reverse proxy in production

**Database Indexes:**
- Current: No indexes on frequently queried fields
- Improvement: Add index on `users.email`:
  ```sql
  CREATE INDEX idx_users_email ON users(email);
  ```

---

### 8. MONITORING CHECKLIST

For DevOps monitoring, watch these:

```
✓ Flask application status
✓ MySQL database connectivity
✓ Database connection count
✓ Query response time
✓ Memory usage
✓ Disk space (database growth)
✓ Error logs
✓ Failed login attempts
✓ API response times
```

---

## COMPLETE REQUEST/RESPONSE CYCLE

### Example: User Adding a Todo

```
┌─────── TIME SEQUENCE ───────┐

T1: User's Action
    └─ User fills "Buy groceries" form
    └─ Clicks "Add Task" button

T2: HTTP Request Sent
    └─ Browser sends POST request to http://localhost:5000/todos/add
    └─ Request body: {title: "Buy groceries", priority: "high", ...}

T3: Flask Route Handler
    └─ app.py line 195: @app.route('/todos/add', methods=['POST'])
    └─ add_todo() function called

T4: Validation
    └─ Check if title is empty
    └─ If valid, continue; else show error

T5: MySQL Connection
    └─ conn = get_db_connection()
    └─ Uses credentials from .env file
    └─ Connects to MySQL on localhost:3306
    └─ Selects database: todo_app

T6: Database Operation
    └─ INSERT INTO todos (user_id, title, priority, ...)
    └─ user_id = 1 (from session cookie)
    └─ MySQL inserts row

T7: Commit Transaction
    └─ conn.commit()
    └─ Changes write to disk permanently

T8: Close Connection
    └─ cur.close()
    └─ conn.close()
    └─ Connection returned to pool/closed

T9: Response Sent
    └─ Flask redirects to /todos
    └─ HTTP 302 redirect response sent to browser

T10: Browser Receives Response
    └─ Browser navigates to new URL
    └─ Sends GET request to /todos

T11: New Page Load
    └─ Flask fetches updated todo list from MySQL
    └─ Renders HTML with new todo included
    └─ HTML sent to browser

T12: User Sees Result
    └─ Page refreshes
    └─ New todo appears in list
    └─ "Task added!" success message displays

└─── TOTAL TIME: ~100-500ms ─────┘
```

---

## SUMMARY

**4-Layer Architecture:**
1. **Browser Layer** - User interface (HTML/CSS/JS)
2. **Flask Layer** - Application logic (routes, validation, business rules)
3. **Configuration Layer** - Environment variables (.env file)
4. **Database Layer** - MySQL storage (persistent data)

**7 Primary MySQL Connection Points:**
1. Register - Check duplicates
2. Register - Insert new user
3. Login - Fetch user
4. Todos page - Fetch user's todos
5. Add todo - Insert new todo
6. Toggle todo - Update completion status
7. Delete todo - Remove todo

**Key DevOps Takeaways:**
- Stateless app (except session cookie)
- Configuration via environment variables
- Secure password storage (hashing)
- SQL injection prevention (parameterized queries)
- Connection management (close after use)
- Error handling and logging

---

**Document Version:** 1.0  
**Last Updated:** April 3, 2026  
**Audience:** DevOps Engineers  
**Maintainer:** Development Team
