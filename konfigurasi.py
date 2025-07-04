# konfigurasi.py
import os

# Lokasi file database SQLite (di direktori yang sama dengan script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NAMA_DB = 'todolist.db'
DB_PATH = os.path.join(BASE_DIR, NAMA_DB)

# Daftar prioritas yang tersedia
DAFTAR_PRIORITAS = ["Urgent","High", "Medium", "Low"]

# Status tugas yang mungkin
STATUS_TUGAS = ["In Progress","Need Approval","Pending", "Complete"]

# Default nilai jika user tidak memilih
PRIORITAS_DEFAULT = "Medium"
STATUS_DEFAULT = "Pending"
