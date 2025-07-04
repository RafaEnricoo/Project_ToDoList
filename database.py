# database.py

import sqlite3
import pandas as pd
from konfigurasi import DB_PATH

def get_db_connection() -> sqlite3.Connection | None:
    """Membuka dan mengembalikan koneksi baru ke database SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row  # Akses kolom seperti dict (by name)
        return conn
    except sqlite3.Error as e:
        print(f"ERROR [database.py] Gagal koneksi DB: {e}")
        return None

def execute_query(query: str, params: tuple = None) -> int | None:
    """Jalankan query non-SELECT (INSERT, UPDATE, DELETE). Return lastrowid jika INSERT."""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"ERROR [database.py] Query gagal: {e}\nQuery: {query}")
        conn.rollback()
        return None
    finally:
        conn.close()

def fetch_query(query: str, params: tuple = None, fetch_all: bool = True):
    """Jalankan query SELECT dan kembalikan hasil (list of rows)."""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall() if fetch_all else cursor.fetchone()
    except sqlite3.Error as e:
        print(f"ERROR [database.py] Fetch gagal: {e}\nQuery: {query}")
        return None
    finally:
        conn.close()

def get_dataframe(query: str, params: tuple = None) -> pd.DataFrame:
    """Jalankan query SELECT dan kembalikan hasil sebagai DataFrame Pandas."""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    try:
        return pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        print(f"ERROR [database.py] Gagal baca ke DataFrame: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def setup_database_initial() -> bool:
    """Memastikan tabel tugas ada (dipanggil oleh ManajerTugas saat inisialisasi).
    Return True jika setup berhasil atau tabel sudah ada."""
    print(f"[database.py] Memeriksa/membuat tabel 'tugas' di: {DB_PATH}")
    conn = get_db_connection()
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        sql_create_table = """
        CREATE TABLE IF NOT EXISTS tugas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matkul TEXT,
            deskripsi TEXT NOT NULL,
            deadline DATE NOT NULL,
            prioritas TEXT NOT NULL,
            status TEXT NOT NULL
        );"""
        cursor.execute(sql_create_table)
        conn.commit()
        print("[database.py] Tabel 'tugas' siap.")
        return True
    except sqlite3.Error as e:
        print(f"[database.py] Error saat setup tabel: {e}")
        return False
    finally:
        if conn:
            conn.close()