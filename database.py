import sqlite3

def init_db():
    conn = sqlite3.connect('peek.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  language TEXT DEFAULT 'ar',
                  credits INTEGER DEFAULT 3,
                  referrals INTEGER DEFAULT 0,
                  joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('peek.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(user_id, username, referred_by=None):
    conn = sqlite3.connect('peek.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', 
              (user_id, username))
    if referred_by:
        c.execute('UPDATE users SET credits = credits + 2, referrals = referrals + 1 WHERE user_id = ?', 
                  (referred_by,))
    conn.commit()
    conn.close()

def update_credits(user_id, amount):
    conn = sqlite3.connect('peek.db')
    c = conn.cursor()
    c.execute('UPDATE users SET credits = credits + ? WHERE user_id = ?', 
              (amount, user_id))
    conn.commit()
    conn.close()

def set_language(user_id, language):
    conn = sqlite3.connect('peek.db')
    c = conn.cursor()
    c.execute('UPDATE users SET language = ? WHERE user_id = ?', 
              (language, user_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('peek.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    users = c.fetchall()
    conn.close()
    return users
