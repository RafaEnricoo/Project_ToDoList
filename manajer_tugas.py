import datetime
import pandas as pd
from model import Tugas
import database  # modul database.py

class ManajerTugas:
    """Mengelola logika bisnis to-do list (CRUD untuk tugas)."""
    _db_setup_done = False # Flag untuk memastikan setup DB hanya dicek sekali per sesi

    def __init__(self):
        if not ManajerTugas._db_setup_done:
            print("[ManajerTugas] Memeriksa inisialisasi database...")
            if database.setup_database_initial(): # Panggil fungsi setup dari database.py
                ManajerTugas._db_setup_done = True
                print("[ManajerTugas] Database siap.")
            else:
                print("[ManajerTugas] ERROR: Inisialisasi database gagal!")
            
    def tambah_tugas(self, tugas: Tugas) -> bool:
        if not isinstance(tugas, Tugas):
            return False

        sql = """
        INSERT INTO tugas (matkul, deskripsi, deadline, prioritas, status)
        VALUES (?, ?, ?, ?, ?)
        """
        params = (
            tugas.matkul,
            tugas.deskripsi,
            tugas.deadline.strftime("%Y-%m-%d"),
            tugas.prioritas,
            tugas.status
        )
        
        print(">> Menyimpan tugas:", params)
        
        last_id = database.execute_query(sql, params)
        if last_id is not None:
            tugas.id = last_id
            return True
        return False

    def get_semua_tugas_obj(self) -> list[Tugas]:
        sql = "SELECT id, matkul, deskripsi, deadline, prioritas, status FROM tugas ORDER BY deadline ASC, id ASC"
        rows = database.fetch_query(sql)
        daftar_tugas = []
        if rows:
            for row in rows:
                tugas = Tugas(
                    id_tugas=row["id"],
                    matkul=row["matkul"],
                    deskripsi=row["deskripsi"],
                    deadline=row["deadline"],
                    prioritas=row["prioritas"],
                    status=row["status"]
                )
                daftar_tugas.append(tugas)
        return daftar_tugas

    def get_dataframe_tugas(self, status_filter: str | None = None, prioritas_filter: str | None = None, tanggal: datetime.date | None = None) -> pd.DataFrame:
        sql = "SELECT id, matkul, deskripsi, deadline, prioritas, status FROM tugas"
        params = []
        kondisi = []

        if status_filter:
            kondisi.append("status = ?")
            params.append(status_filter)

        if prioritas_filter:
            kondisi.append("prioritas = ?")
            params.append(prioritas_filter)
        
        if tanggal:
            kondisi.append("DATE(deadline) = ?")
            params.append(tanggal.strftime("%Y-%m-%d"))

        if kondisi:
            sql += " WHERE " + " AND ".join(kondisi)

        sql += " ORDER BY deadline ASC, id ASC"
        return database.get_dataframe(sql, tuple(params))


    def hapus_tugas(self, id_tugas: int) -> bool:
        sql = "DELETE FROM tugas WHERE id = ?"
        params = (id_tugas,)
        conn = database.get_db_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            if cursor.rowcount == 0:
                print(f"ERROR saat menghapus tugas: ID {id_tugas} tidak ditemukan.")
                return False
            return True
        except Exception as e:
            print(f"ERROR saat menghapus tugas: {e}")
            return False
        finally:
            conn.close()

    def tandai_selesai(self, id_tugas: int) -> bool:
        sql = "UPDATE tugas SET status = 'Complete' WHERE id = ?"
        params = (id_tugas,)
        conn = database.get_db_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            if cursor.rowcount == 0:
                print(f"ERROR saat tandai selesai: ID {id_tugas} tidak ditemukan.")
                return False
            return True
        except Exception as e:
            print(f"ERROR saat tandai selesai: {e}")
            return False
        finally:
            conn.close()

    def update_tugas(self, tugas: Tugas) -> bool:
        sql = """
        UPDATE tugas
        SET matkul = ?, deskripsi = ?, deadline = ?, prioritas = ?, status = ?
        WHERE id = ?
        """
        params = (
            tugas.matkul,
            tugas.deskripsi,
            tugas.deadline.strftime("%Y-%m-%d"),
            tugas.prioritas,
            tugas.status,
            tugas.id
        )
        conn = database.get_db_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            if cursor.rowcount == 0:
                print(f"ERROR saat update: ID {tugas.id} tidak ditemukan.")
                return False
            return True
        except Exception as e:
            print(f"ERROR saat update tugas: {e}")
            return False
        finally:
            conn.close()

    def hitung_total_tugas(self, tanggal: datetime.date | None = None) -> int:
        sql = "SELECT COUNT(*) FROM tugas"
        params = ()
        if tanggal:
            sql += " WHERE DATE(deadline) = ?"
            params = (tanggal.strftime("%Y-%m-%d"),)

        conn = database.get_db_connection()
        if not conn:
            return 0
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"[ERROR hitung_total_tugas] {e}")
            return 0
        finally:
            conn.close()
