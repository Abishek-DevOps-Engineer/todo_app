# Quick Start Guide - Taska Todo Application

## 📋 Project at a Glance

| Aspect | Details |
|--------|---------|
| **Project Name** | Taska - Todo/Task Management App |
| **Type** | Full-Stack Web Application |
| **Backend** | Flask (Python) |
| **Database** | MySQL |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Status** | ✅ MVP Complete & Ready for Deployment |
| **Deployed Port** | 5000 (Flask), 3306 (MySQL) |

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# 1. Navigate to project directory
cd d:\Abishek\DEVOPS_EMC\Project\todo_app

# 2. Create .env file
echo MYSQL_PASSWORD=root123 > .env
echo SECRET_KEY=dev-secret-key >> .env

# 3. Build and run
docker-compose up --build

# 4. Access app
# Open browser: http://localhost:5000
```

### Option 2: Local Development
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup MySQL
mysql -u root -p < schema.sql

# 3. Create .env file
# (See .env template below)

# 4. Run Flask app
python app.py

# 5. Access app
# http://localhost:5000
```

---

## 📁 File Structure Quick Reference

| File/Folder | Purpose |
|-------------|---------|
| `app.py` | Main Flask application with all routes |
| `requirements.txt` | Python dependencies |
| `schema.sql` | Database initialization |
| `docker_compose.yaml` | Container orchestration |
| `Dockerfile` | Docker image configuration |
| `templates/base.html` | Base HTML template |
| `templates/login.html` | Login page |
| `templates/register.html` | Registration page |
| `templates/todos.html` | Todo management page |
| `static/main.js` | Frontend logic |
| `static/css/main.css` | Styling |

---

## 🔑 Key Features

### Core Functionality
- ✅ User Registration with validation
- ✅ Secure Login/Logout
- ✅ Create/Read/Update/Delete Todos
- ✅ Mark todos as complete/incomplete
- ✅ Priority levels (low, medium, high)
- ✅ Due dates for todos
- ✅ User-specific todo isolation

### Security
- ✅ Password hashing (Werkzeug)
- ✅ SQL injection prevention (parameterized queries)
- ✅ Session-based authentication
- ✅ Login requirement decorator
- ✅ Input validation (client + server)

### Frontend
- ✅ Responsive design
- ✅ Password strength indicator
- ✅ Flash message system
- ✅ Password visibility toggle
- ✅ Auto-dismissing notifications

---

## 🗄️ Database Schema Quick Overview

### users table
```
id (PK, auto-increment)
username (UNIQUE)
email (UNIQUE)
password (hashed)
created_at (timestamp)
```

### todos table
```
id (PK)
user_id (FK → users.id, CASCADE DELETE)
title (required)
description (optional)
is_completed (default: false)
priority (low/medium/high)
due_date (optional)
created_at, updated_at (timestamps)
```

---

## 🛣️ API Routes Summary

### Public Routes (No Login Required)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Redirect to login or todos |
| `/register` | GET | Show registration form |
| `/register` | POST | Create new user account |
| `/login` | GET | Show login form |
| `/login` | POST | Authenticate user |

### Protected Routes (Login Required)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/logout` | GET | End session |
| `/todos` | GET | List user's todos |
| `/todos/add` | POST | Create new todo |
| `/todos/toggle/<id>` | GET | Toggle completion status |
| `/todos/delete/<id>` | GET | Delete todo |

---

## 🔧 Configuration

### .env File Template
```bash
# Database Configuration
MYSQL_HOST=db           # or localhost for local dev
MYSQL_USER=root
MYSQL_PASSWORD=your_secure_password
MYSQL_DB=todo_app

# Application
SECRET_KEY=your_secret_key_here
```

### Flask Configuration (in app.py)
```python
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'todo_app')
```

---

## 📊 Request Flow Examples

### Creating a Todo
```
1. User fills form and clicks "Add Task"
2. POST /todos/add with: title, description, priority, due_date
3. Server validates: title is required
4. INSERT into todos table with user_id from session
5. Flash "Task added!" message
6. Redirect to GET /todos
7. Page refreshes with new todo in list
```

### Logging In
```
1. User enters email and password
2. POST /login with credentials
3. Query users table WHERE email = provided_email
4. Check password hash: check_password_hash(stored, provided)
5. Create session['user_id'] with user's ID
6. Flash "Welcome back!" message
7. Redirect to GET /todos
```

### Toggling Todo Completion
```
1. User clicks checkbox on todo
2. GET /todos/toggle/<todo_id>
3. UPDATE todos SET is_completed = NOT is_completed
4. Verify ownership: WHERE id = <id> AND user_id = session['user_id']
5. Commit transaction
6. Redirect to GET /todos
7. Todo shows updated status
```

---

## 🐛 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: Flask` | Run `pip install -r requirements.txt` |
| MySQL connection refused | Ensure MySQL is running, check credentials in .env |
| Port 5000 already in use | Change port in `app.run(port=5001)` or kill process |
| Flash messages not showing | Check base.html includes flash message block |
| Todos not persisting | Verify `mysql.connection.commit()` is called |
| Can't access /todos without login | Good! Login decorator is working |
| CSRF/session errors | Check SECRET_KEY is set in .env |

---

## 👤 Test Credentials (After Setup)

### Sample Accounts
```
Username: testuser1
Email: test@example.com
Password: Test@123

Username: alice
Email: alice@example.com
Password: AlicePass123
```

---

## 🧪 Testing Checklist

### Before Deployment
- [ ] User can register with valid data
- [ ] Duplicate username/email shows error
- [ ] Password validation works (min 6 chars)
- [ ] User can login with correct credentials
- [ ] Invalid credentials show error
- [ ] Logout clears session
- [ ] Can create todo with title
- [ ] Can mark todo complete/incomplete
- [ ] Can delete todo
- [ ] Flash messages appear and auto-dismiss
- [ ] Password strength indicator works
- [ ] Page is responsive on mobile
- [ ] Docker containers start correctly

---

## 📦 Dependencies Overview

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 2.3.3 | Web framework |
| Flask-MySQLdb | 2.0.0 | MySQL integration |
| PyMySQL | 1.1.0 | MySQL driver |
| Werkzeug | 2.3.7 | Password hashing |
| python-dotenv | 1.0.0 | Environment variables |
| Flask-Login | 0.6.3 | Session management helper |

---

## 🔒 Security Checklist

- [x] Passwords hashed with Werkzeug
- [x] SQL injection prevented (parameterized queries)
- [x] User isolation enforced (WHERE user_id checks)
- [x] Login decorator protects routes
- [x] Session-based authentication
- [x] Input validation on server
- [x] UNIQUE constraints on username/email
- [x] Cascade delete for data integrity
- [ ] HTTPS enabled (TODO for production)
- [ ] CORS configured (if needed)
- [ ] Rate limiting (TODO for production)

---

## 📝 Development Workflow

### Adding a New Feature
```
1. Create new route in app.py
2. Add @login_required if needed
3. Create template if form required
4. Add CSS if new UI styling needed
5. Test locally: python app.py
6. Test with Docker: docker-compose up --build
7. Verify in browser: http://localhost:5000
```

### Debugging
```bash
# Enable Flask debug mode
export FLASK_ENV=development
export FLASK_DEBUG=1

# Watch logs
docker-compose logs -f my-app

# Access container shell
docker-compose exec my-app bash
```

---

## 🚢 Deployment Checklist

Before deploying to production:
- [ ] Update `SECRET_KEY` with strong random value
- [ ] Set secure MySQL passwords
- [ ] Enable HTTPS/SSL
- [ ] Update database backups
- [ ] Test all features in staging
- [ ] Configure logging and monitoring
- [ ] Set proper environment variables
- [ ] Use production WSGI server (gunicorn)
- [ ] Enable database connection pooling
- [ ] Configure firewall rules

---

## 📚 Documentation Files

| File | Content |
|------|---------|
| `README.md` | Project overview and features |
| `IMPLEMENTATION_STATUS.md` | Detailed status of implemented features |
| `TECHNICAL_ARCHITECTURE.md` | In-depth technical design |
| `QUICK_START_GUIDE.md` | This file - quick reference |

---

## 💡 Tips & Tricks

### Flash Messages
```python
flash('Message text', 'success')  # Green
flash('Error message', 'error')   # Red
flash('Info message', 'info')     # Blue
```

### Database Debugging
```sql
-- Check all users
SELECT id, username, email FROM users;

-- Check user's todos
SELECT * FROM todos WHERE user_id = 1;

-- Count user's todos
SELECT COUNT(*) as total FROM todos WHERE user_id = 1;
```

### Browser Developer Tools
- F12 → Console tab to see JavaScript errors
- F12 → Network tab to inspect HTTP requests
- F12 → Application tab to see session cookies

---

## 🔗 Related Commands

```bash
# View running containers
docker-compose ps

# Stop containers
docker-compose down

# Rebuild container
docker-compose up --build

# View logs
docker-compose logs my-app

# Access MySQL
docker-compose exec mysqldb mysql -u root -p

# Clean images
docker system prune
```

---

## ❓ FAQ

**Q: Can I access the database directly?**  
A: Yes, use MySQL client with credentials from .env file.

**Q: How do I reset the database?**  
A: Run `schema.sql` again to drop and recreate tables.

**Q: Can I run multiple instances?**  
A: Yes, Docker Compose can scale services.

**Q: Is this production-ready?**  
A: MVP is complete. Add HTTPS, monitoring, and backups for production.

**Q: How do I add more features?**  
A: Create new routes in app.py, templates, and database tables as needed.

---

## 📞 Key Contacts/Resources

- Flask Documentation: https://flask.palletsprojects.com/
- MySQL Documentation: https://dev.mysql.com/doc/
- Docker Documentation: https://docs.docker.com/

---

**Last Updated**: March 2026  
**Version**: 1.0  
**Status**: ✅ Ready for Use
