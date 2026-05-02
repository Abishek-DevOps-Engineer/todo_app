# Technical Architecture - Taska Todo Application

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Client Layer (Browser)                     │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ HTML5 Templates (Jinja2 Templating)                       ││
│  │ - base.html (layout inheritance)                          ││
│  │ - login.html, register.html, todos.html (pages)          ││
│  └──────────────────────────────────────────────────────────┘│
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Frontend Assets                                            ││
│  │ - main.js (event handlers, DOM manipulation)              ││
│  │ - main.css (styling, responsive design)                   ││
│  └──────────────────────────────────────────────────────────┘│
└────────────────┬─────────────────────────────────────────────┘
                 │ HTTP/HTTPS (Port 5000)
┌────────────────┴─────────────────────────────────────────────┐
│                   Application Layer (Flask)                   │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Flask Application (WSGI Server)                            ││
│  │ - Routes: Auth, Todo CRUD                                 ││
│  │ - Session Management                                      ││
│  │ - Request Validation                                      ││
│  │ - Error Handling                                          ││
│  └──────────────────────────────────────────────────────────┘│
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Business Logic                                             ││
│  │ - Authentication (hash verification)                      ││
│  │ - Todo CRUD operations                                    ││
│  │ - User isolation enforcement                              ││
│  │ - Input validation                                        ││
│  └──────────────────────────────────────────────────────────┘│
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Flask Extensions                                           ││
│  │ - Flask-MySQLdb: Database abstraction                     ││
│  │ - Werkzeug: Password hashing                              ││
│  │ - python-dotenv: Configuration                            ││
│  └──────────────────────────────────────────────────────────┘│
└────────────────┬─────────────────────────────────────────────┘
                 │ MySQL Protocol (Port 3306)
┌────────────────┴─────────────────────────────────────────────┐
│                   Data Layer (MySQL)                          │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Database: todo_app                                         ││
│  │ ┌──────────────────────────────────────────────────────┐ ││
│  │ │ users Table                              (PK: id)    │ ││
│  │ │ - id, username, email, password, created_at         │ ││
│  │ │ Constraints: UNIQUE(username), UNIQUE(email)        │ ││
│  │ └──────────────────────────────────────────────────────┘ ││
│  │ ┌──────────────────────────────────────────────────────┐ ││
│  │ │ todos Table                             (PK: id)     │ ││
│  │ │ - id, user_id, title, description, is_completed     │ ││
│  │ │ - priority, due_date, created_at, updated_at        │ ││
│  │ │ FK: user_id → users.id (CASCADE DELETE)             │ ││
│  │ │ Index: user_id (for query optimization)             │ ││
│  │ └──────────────────────────────────────────────────────┘ ││
│  └──────────────────────────────────────────────────────────┘│
└───────────────────────────────────────────────────────────────┘
```

---

## Authentication Flow

```
                           ┌─────────────┐
                           │   Browser   │
                           └──────┬──────┘
                                  │
                    ┌─────────────┴──────────────┐
                    │                            │
            ┌───────▼────────┐          ┌────────▼────────┐
            │  /login POST   │          │ /register POST  │
            └────────┬───────┘          └────────┬────────┘
                     │                           │
         ┌───────────┴────────────────────────────┴────────────┐
         │                                                      │
    ┌────▼──────────────────────────────────────────────────┐  │
    │ 1. Validate Input                                     │  │
    │    - Check required fields                           │  │
    │    - Check format (email, password)                 │  │
    └────┬──────────────────────────────────────────────────┘  │
         │                                                      │
    ┌────▼──────────────────────────────────────────────────┐  │
    │ 2. Check Duplicates (register only)                  │  │
    │    - Query: SELECT * FROM users WHERE username=? ... │  │
    └────┬──────────────────────────────────────────────────┘  │
         │                                                      │
    ┌────▼──────────────────────────────────────────────────┐  │
    │ 3. Hash Password / Verify Hash                       │  │
    │    - Create: generate_password_hash(password)        │  │
    │    - Verify: check_password_hash(stored, input)     │  │
    └────┬──────────────────────────────────────────────────┘  │
         │                                                      │
    ┌────▼──────────────────────────────────────────────────┐  │
    │ 4. Database Operation                                │  │
    │    - INSERT (register)                              │  │
    │    - SELECT (login)                                 │  │
    └────┬──────────────────────────────────────────────────┘  │
         │                                                      │
    ┌────▼──────────────────────────────────────────────────┐  │
    │ 5. Session Management                                │  │
    │    - Create session['user_id'] and session['username']
    │    - Set SECRET_KEY for signing                     │  │
    └────┬──────────────────────────────────────────────────┘  │
         │                                                      │
    ┌────▼──────────────────────────────────────────────────┐  │
    │ 6. Redirect & Flash Message                          │  │
    │    - Flash success/error message                     │  │
    │    - Redirect to /todos or /login                   │  │
    └────┴──────────────────────────────────────────────────┘  │
         │                                                      │
         └──────────────────────────────────────────────────────┘
```

---

## Request-Response Cycle

### Example: Adding a Todo

```
1. User fills form: title="Buy milk", priority="high", due_date="2026-03-25"
                    ↓
2. Form submission:  POST /todos/add with form data
                    ↓
3. Server receives:  request.form.get('title'), etc.
                    ↓
4. Validation:      if not title: error
                    ↓
5. Database:        INSERT INTO todos (user_id, title, description, ...)
                       VALUES (session['user_id'], ...)
                    ↓
6. Commit:          mysql.connection.commit()
                    ↓
7. Flash message:   flash('Task added!', 'success')
                    ↓
8. Redirect:        return redirect(url_for('todos'))
                    ↓
9. Browser:         GET /todos → Load todos list
                    ↓
10. Display:        Render todos.html with updated todo list
                    ↓
11. Message:        Show "Task added!" flash message (auto-dismiss in 4s)
```

---

## Database Query Operations

### Authentication Queries

**Check existing user (register)**
```sql
SELECT id FROM users 
WHERE username = %s OR email = %s
```

**Insert new user (register)**
```sql
INSERT INTO users (username, email, password) 
VALUES (%s, %s, %s)
```

**Get user (login)**
```sql
SELECT * FROM users 
WHERE email = %s
```

### Todo Queries

**Get user's todos**
```sql
SELECT * FROM todos 
WHERE user_id = %s 
ORDER BY is_completed ASC, created_at DESC
```

**Add todo**
```sql
INSERT INTO todos (user_id, title, description, priority, due_date) 
VALUES (%s, %s, %s, %s, %s)
```

**Toggle completion**
```sql
UPDATE todos 
SET is_completed = NOT is_completed 
WHERE id = %s AND user_id = %s
```

**Delete todo**
```sql
DELETE FROM todos 
WHERE id = %s AND user_id = %s
```

---

## Security Measures

### 1. Password Security
```python
# Hashing (at registration)
hashed_pw = generate_password_hash(password)  # Werkzeug
INSERT INTO users (password) VALUES (hashed_pw)

# Verification (at login)
check_password_hash(stored_hash, provided_password)  # Returns bool
```

### 2. SQL Injection Prevention
```python
# ✅ SAFE: Parameterized queries
cur.execute("SELECT * FROM users WHERE email = %s", (email,))

# ❌ UNSAFE (not used): String concatenation
cur.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### 3. Session Security
```python
app.secret_key = os.getenv('SECRET_KEY')  # Required for signing
session['user_id'] = user['id']           # Server-side storage
# Client only receives signed session cookie
```

### 4. User Isolation
```python
# Every query includes user_id check
cur.execute("SELECT * FROM todos WHERE id = %s AND user_id = %s", 
            (todo_id, session['user_id']))
```

### 5. Input Validation
```python
# Server-side validation (always)
if not username or len(username) < 3:
    errors.append('Username must be at least 3 characters.')

# Client-side validation (convenience, not security)
<input type="email" required />  <!-- HTML5 validation -->
```

---

## Frontend JavaScript Functions

### 1. Password Visibility Toggle
```javascript
// Find all toggle buttons and add click handler
document.querySelectorAll('.toggle-pw').forEach(btn => {
    btn.addEventListener('click', () => {
        const input = document.getElementById(btn.dataset.target);
        input.type = input.type === 'password' ? 'text' : 'password';
        btn.style.opacity = input.type === 'text' ? '1' : '0.5';
    });
});
```

### 2. Password Strength Indicator
```javascript
// Calculate strength: 0-5
let score = 0;
if (val.length >= 6) score++;      // Length 6+
if (val.length >= 10) score++;     // Length 10+
if (/[A-Z]/.test(val)) score++;    // Uppercase
if (/[0-9]/.test(val)) score++;    // Numbers
if (/[^A-Za-z0-9]/.test(val)) score++; // Special chars

// Color code: red → orange → yellow → lime → green
```

### 3. Flash Message Auto-Dismiss
```javascript
// Remove flash messages after 4 seconds with fade out
document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => {
        el.style.transition = 'opacity 0.4s';
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 400);
    }, 4000);
});
```

---

## Environment Configuration

### Required .env Variables
```bash
MYSQL_HOST=db              # Docker: 'db', Local: 'localhost'
MYSQL_USER=root            # MySQL username
MYSQL_PASSWORD=secret123   # MySQL password
MYSQL_DB=todo_app          # Database name
SECRET_KEY=your_secret_key # Flask session secret
```

### Flask Config
```python
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'todo_app')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # Return dicts, not tuples
```

---

## Error Handling Strategy

### Application-Level Errors
```python
try:
    cur = mysql.connection.cursor()
    # Database operations
    mysql.connection.commit()
except Exception as e:
    print(f"Error: {e}")
    flash('An error occurred. Please try again.', 'error')
```

### Validation Errors
```python
errors = []
if not username:
    errors.append('Username is required.')
if errors:
    for error in errors:
        flash(error, 'error')
```

### User-Facing Error Messages
- Generic messages for security (avoid database errors in UI)
- Helpful validation messages for forms
- Flash messages for operation results

---

## Performance Considerations

1. **Database Indexing**
   - `todos.user_id` implicitly indexed (FK)
   - `users.username, users.email` indexed (UNIQUE)

2. **Query Optimization**
   - `ORDER BY` on indexed columns (created_at)
   - `WHERE` filter on user_id (FK query optimization)

3. **Connection Pooling**
   - Flask-MySQLdb manages connection pool
   - Connections reused across requests

4. **Frontend Optimization**
   - Vanilla JS (no framework overhead)
   - Minimal CSS (single main.css file)
   - No build process required

---

## Deployment Architecture (Docker)

```
┌─────────────────────────────────────┐
│      docker-compose.yaml             │
├─────────────────────────────────────┤
│                                      │
│  Services:                          │
│  ┌──────────────────┐              │
│  │ mysqldb         │              │
│  │ - Image: mysql   │              │
│  │ - Port: 3306    │              │
│  │ - Env: ROOT_PASS │              │
│  └──────────────────┘              │
│                                      │
│  ┌──────────────────┐              │
│  │ my-app          │              │
│  │ - Build: ./     │              │
│  │ - Port: 5000    │              │
│  │ - Env: MYSQL_*  │              │
│  │ - Depends: db   │              │
│  └──────────────────┘              │
│                                      │
└─────────────────────────────────────┘
```

---

## Codebase Organization

```
app.py
├── Imports & Setup
│   ├── Flask initialization
│   ├── MySQL configuration
│   └── Environment variables
├── Helper Functions
│   └── login_required decorator
├── Auth Routes
│   ├── GET/POST /register
│   ├── GET/POST /login
│   ├── GET /logout
│   └── GET /
├── Todo Routes
│   ├── GET /todos (list)
│   ├── POST /todos/add (create)
│   ├── GET /todos/toggle/<id> (update)
│   └── GET /todos/delete/<id> (delete)
└── App Entry Point
    └── if __name__ == '__main__': app.run(...)
```

---

## Data Flow Summary

### Synchronous Request-Response Flow
```
Browser  →  Flask App  →  MySQL DB  →  Flask App  →  Browser
  (GET)      (Route)       (Query)      (Render)      (HTML)
```

### Session Management
```
1. User logs in → Flask creates signed cookie with session ID
2. Cookie stored in browser (httponly, secure flags optional)
3. Each request sends cookie → Flask verifies signature
4. Session data retrieved from server-side storage
5. Routes check session['user_id'] existence
```

---

## Testing Entry Points

1. **Authentication Testing**
   - Bad credentials → error message
   - Valid credentials → session created
   - Invalid email format → validation error

2. **Authorization Testing**
   - Unauthorized access to /todos → redirect to login
   - Modify other user's todo → WHERE user_id check prevented

3. **CRUD Operations Testing**
   - Create with missing title → validation error
   - Update todo completion → verify in DB
   - Delete todo → verify removed from DB and list

4. **Database Integrity Testing**
   - Delete user → cascade delete todos
   - Duplicate username → constraint violation
   - Foreign key validation

---

**Last Updated**: March 2026  
**Version**: 1.0 MVP
