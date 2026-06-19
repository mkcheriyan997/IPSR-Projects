import sqlite3
import os
import json
from datetime import datetime
DB_PATH = os.path.join(os.path.dirname(__file__), 'generated', 'autoplay.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database with playbooks and execution runs tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Playbooks schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS playbooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target_hosts TEXT NOT NULL,
            become_privilege TEXT NOT NULL,
            tasks_json TEXT NOT NULL,
            playbook_yaml TEXT NOT NULL,
            inventory_ini TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Executions/Runs schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playbook_id INTEGER,
            ip TEXT NOT NULL,
            status TEXT NOT NULL, -- 'running', 'success', 'failed'
            logs TEXT,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (playbook_id) REFERENCES playbooks(id) ON DELETE SET NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def save_playbook(name, target_hosts, become_privilege, tasks, playbook_yaml, inventory_ini):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tasks_json = json.dumps(tasks)
    
    # Check if a playbook with the exact same characteristics already exists
    cursor.execute('''
        SELECT id FROM playbooks 
        WHERE name = ? AND target_hosts = ? AND become_privilege = ? AND tasks_json = ?
    ''', (name, target_hosts, become_privilege, tasks_json))
    row = cursor.fetchone()
    if row:
        conn.close()
        return row['id']
    
    cursor.execute('''
        INSERT INTO playbooks (name, target_hosts, become_privilege, tasks_json, playbook_yaml, inventory_ini)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, target_hosts, become_privilege, tasks_json, playbook_yaml, inventory_ini))
    
    playbook_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return playbook_id

def get_playbooks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM playbooks ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_playbook(playbook_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM playbooks WHERE id = ?', (playbook_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_run(playbook_id, ip):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO runs (playbook_id, ip, status, logs)
        VALUES (?, ?, ?, ?)
    ''', (playbook_id, ip, 'running', 'Initialization... Starting Ansible Playbook Execution.\n'))
    run_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return run_id

def update_run_status(run_id, status, logs=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if logs is not None:
        cursor.execute('''
            UPDATE runs
            SET status = ?, logs = ?
            WHERE id = ?
        ''', (status, logs, run_id))
    else:
        cursor.execute('''
            UPDATE runs
            SET status = ?
            WHERE id = ?
        ''', (status, run_id))
    conn.commit()
    conn.close()

def append_run_logs(run_id, log_chunk):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT logs FROM runs WHERE id = ?', (run_id,))
    row = cursor.fetchone()
    if row:
        current_logs = row['logs'] or ''
        new_logs = current_logs + log_chunk
        cursor.execute('UPDATE runs SET logs = ? WHERE id = ?', (new_logs, run_id))
        conn.commit()
    conn.close()

def get_runs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, p.name as playbook_name
        FROM runs r
        LEFT JOIN playbooks p ON r.playbook_id = p.id
        ORDER BY r.executed_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_run(run_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, p.name as playbook_name, p.playbook_yaml, p.inventory_ini
        FROM runs r
        LEFT JOIN playbooks p ON r.playbook_id = p.id
        WHERE r.id = ?
    ''', (run_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
