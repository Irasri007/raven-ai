# database.py

import pyodbc
from dotenv import load_dotenv
import os

load_dotenv()

SERVER   = os.getenv("DB_SERVER", "localhost")
DATABASE = os.getenv("DB_NAME", "raven_db")

def get_connection():
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"Trusted_Connection=yes;"
    )
    return conn

def init_db():
    # Step 1: Connect to master DB with autocommit to create raven_db
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE=master;"
        f"Trusted_Connection=yes;"
    )
    conn.autocommit = True   # ← must be set AFTER connect, not inside string
    cursor = conn.cursor()

    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'raven_db')
        CREATE DATABASE raven_db
    """)

    cursor.close()
    conn.close()

    # Step 2: Now connect to raven_db and create tables
    conn = get_connection()
    conn.autocommit = False
    cursor = conn.cursor()

    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
        CREATE TABLE users (
            id INT IDENTITY(1,1) PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            email VARCHAR(150),
            password_hash VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT GETDATE(),
            last_login DATETIME
        )
    """)

    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='chat_logs' AND xtype='U')
        CREATE TABLE chat_logs (
            id INT IDENTITY(1,1) PRIMARY KEY,
            user_id INT NOT NULL,
            command TEXT NOT NULL,
            response TEXT,
            timestamp DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ SQL Server Database initialized.")