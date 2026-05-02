# Taska — Task Management App

A clean, full-stack task management web app built with Python, Flask, and MySQL. Taska lets users register, log in, and manage their personal to-do lists with priority levels, due dates, and completion tracking.

---

## Features

- **User Authentication** — Register, log in, and log out securely. Passwords are hashed using Werkzeug's `generate_password_hash`.
- **Session Protection** — All task routes are protected; unauthenticated users are redirected to login.
- **Task Management** — Create, complete/uncomplete, and delete tasks.
- **Priority Levels** — Assign Low, Medium, or High priority to each task, with color-coded indicators.
- **Due Dates** — Optionally set a due date for any task.
- **Flash Messages** — Real-time feedback for actions (success/error), auto-dismissed after 4 seconds.
- **Responsive Design** — Mobile-friendly layout that adapts to smaller screens.
- **Password Strength Indicator** — Visual feedback on password strength during registration.

---

## Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | Python 3, Flask                   |
| Database   | MySQL (via Flask-MySQLdb, PyMySQL)|
| Frontend   | Jinja2, HTML5, CSS3, Vanilla JS   |
| Auth       | Werkzeug password hashing, Flask sessions |
| Fonts      | Google Fonts (Syne, DM Sans)      |

---

## Project Structure

```
taska/
├── app.py                  # Main Flask application & routes
├── schema.sql              # Database schema (users + todos tables)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not committed)
├── static/
│   ├── css/
│   │   └── main.css        # All styles (CSS variables, components)
│   └── js/
│       └── main.js         # Password toggle, strength bar, flash dismissal
└── templates/
    ├── base.html           # Base layout with flash messages
    ├── login.html          # Login page
    ├── register.html       # Registration page
    └── todos.html          # Main task dashboard
```

---

## Getting Started

### Prerequisites

- Python 3.8+
- MySQL 5.7+ or 8.0+
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/taska.git
cd taska
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up the Database

Log in to MySQL and run the schema file:

```bash
mysql -u root -p < schema.sql
```

This creates the `todo_app` database and the `users` and `todos` tables.

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=todo_app
SECRET_KEY=your_random_secret_key
```

### 5. Run the App

```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

---

## Database Schema

```sql
-- Users table
CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50) UNIQUE NOT NULL,
    email       VARCHAR(100) UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Todos table
CREATE TABLE todos (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT NOT NULL,
    title        VARCHAR(255) NOT NULL,
    description  TEXT,
    is_completed BOOLEAN DEFAULT FALSE,
    priority     ENUM('low', 'medium', 'high') DEFAULT 'medium',
    due_date     DATE,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## Routes

| Method | Route                      | Description                  |
|--------|----------------------------|------------------------------|
| GET    | `/`                        | Redirects to login or todos  |
| GET    | `/login`                   | Login page                   |
| POST   | `/login`                   | Authenticate user            |
| GET    | `/register`                | Registration page            |
| POST   | `/register`                | Create new account           |
| GET    | `/logout`                  | Clear session and log out    |
| GET    | `/todos`                   | View all tasks (auth required)|
| POST   | `/todos/add`               | Add a new task               |
| GET    | `/todos/toggle/<id>`       | Toggle task completion       |
| GET    | `/todos/delete/<id>`       | Delete a task                |

---

## Environment Variables

| Variable         | Description                        |
|------------------|------------------------------------|
| `MYSQL_HOST`     | MySQL server host (e.g. localhost) |
| `MYSQL_USER`     | MySQL username                     |
| `MYSQL_PASSWORD` | MySQL password                     |
| `MYSQL_DB`       | Database name                      |
| `SECRET_KEY`     | Flask session secret key           |

---

## Security Notes

- Passwords are never stored in plain text — Werkzeug's PBKDF2-based hashing is used.
- All todo queries filter by `user_id` from the session, preventing cross-user data access.
- The `.env` file should never be committed to version control. Add it to `.gitignore`.

---

## License

MIT License. Feel free to use, modify, and distribute this project.
