import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('studyclub.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        telegram_username TEXT,
        name TEXT,
        specialty TEXT,
        language TEXT DEFAULT 'ar',
        points INTEGER DEFAULT 0,
        total_points INTEGER DEFAULT 0,
        streak INTEGER DEFAULT 0,
        last_study DATE,
        charter_done INTEGER DEFAULT 0,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        duration_hours REAL,
        points_earned INTEGER,
        status TEXT DEFAULT 'active'
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS challenges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        challenger_id INTEGER,
        challenged_id INTEGER,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        item TEXT,
        cost INTEGER,
        expires_at TIMESTAMP,
        purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        session_id INTEGER,
        task TEXT,
        completed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('studyclub.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(user_id, telegram_username, language='ar'):
    conn = sqlite3.connect('studyclub.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id, telegram_username, language) VALUES (?, ?, ?)',
              (user_id, telegram_username, language))
    conn.commit()
    conn.close()

def update_user(user_id, **kwargs):
    conn = sqlite3.connect('studyclub.db')
    c = conn.cursor()
    for key, value in kwargs.items():
        c.execute(f'UPDATE users SET {key} = ? WHERE user_id = ?', (value, user_id))
    conn.commit()
    conn.close()

def add_points(user_id, points):
    conn = sqlite3.connect('studyclub.db')
    c = conn.cursor()
    c.execute('UPDATE users SET points = points + ?, total_points = total_points + ? WHERE user_id = ?',
              (points, points, user_id))
    conn.commit()
    conn.close()

def deduct_points(user_id, points):
    conn = sqlite3.connect('studyclub.db')
    c = conn.cursor()
    c.execute('UPDATE users SET points = MAX(0, points - ?) WHERE user_id = ?', (points, user_id))
    conn.commit()
    conn.close()

def get_rank(total_points):
    if total_points >= 1000:
        return "العرّاب 👑"
    elif total_points >= 500:
        return "ماسي 💎"
    elif total_points >= 250:
        return "بلاتيني 🔥"
    elif total_points >= 100:
        return "ذهبي 🥇"
    elif total_points >= 30:
        return "فضي 🥈"
    else:
        return "برونزي 🥉"

def get_all_users():
    conn = sqlite3.connect('studyclub.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users WHERE charter_done = 1')
    users = c.fetchall()
    conn.close()
    return users

def start_session(user_id, duration_hours):
    conn = sqlite3.connect('studyclub.db')
    c = conn.cursor()
    c.execute('INSERT INTO sessions (user_id, start_time, duration_hours, status) VALUES (?, ?, ?, ?)',
              (user_id, datetime.now(), duration_hours, 'active'))
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    return session_id

def end_session(session_id, points_earned):
    conn = sqlite3.connect('studyclub.db')
    c = conn.cursor()
    c.execute('UPDATE sessions SET end_time = ?, points_earned = ?, status = ? WHERE id = ?',
              (datetime.now(), points_earned, 'completed', session_id))
    conn.commit()
    conn.close()

def get_active_session(user_id):
    conn = sqlite3.connect('studyclub.db')
    c = conn.cursor()
    c.execute('SELECT * FROM sessions WHERE user_id = ? AND status = ?', (user_id, 'active'))
    session = c.fetchone()
    conn.close()
    return session

def add_task(user_id, session_id, task):
    conn = sqlite3.connect('studyclub.db')
    c = conn.cursor()
    c.execute('INSERT INTO tasks (user_id, session_id, task) VALUES (?, ?, ?)',
              (user_id, session_id, task))
    conn.commit()
    conn.close()

def get_tasks(user_id, session_id):
    conn = sqlite3.connect('studyclub.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE user_id = ? AND session_id = ?', (user_id, session_id))
    tasks = c.fetchall()
    conn.close()
    return tasks

def complete_task(task_id):
    conn = sqlite3.connect('studyclub.db')
    c = conn.cursor()
    c.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def has_active_protection(user_id):
    conn = sqlite3.connect('studyclub.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM purchases WHERE user_id = ? 
                 AND item IN ("daily_alibi", "weekly_break") 
                 AND expires_at > ?''', (user_id, datetime.now()))
    result = c.fetchone()
    conn.close()
    return result is not None
