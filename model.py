# model.py
import datetime

class Tugas:
    """Merepresentasikan satu entitas tugas (To-Do Item)."""

    def __init__(self, matkul: str, deskripsi: str, deadline: datetime.date | str,
                 prioritas: str, status: str, id_tugas: int | None = None):
        self.id = id_tugas
        self.matkul = matkul.strip() if matkul else "Umum"
        self.deskripsi = deskripsi.strip() if deskripsi else "Tanpa Deskripsi"
        self.prioritas = prioritas if prioritas else "Medium"
        self.status = status if status else "Pending"

        # Validasi dan konversi tanggal
        if isinstance(deadline, datetime.date):
            self.deadline = deadline
        elif isinstance(deadline, str):
            try:
                self.deadline = datetime.datetime.strptime(deadline, "%Y-%m-%d").date()
            except ValueError:
                self.deadline = datetime.date.today()
                print(f"Peringatan: Format tanggal '{deadline}' salah, gunakan YYYY-MM-DD.")
        else:
            self.deadline = datetime.date.today()
            print("Peringatan: Tipe data deadline tidak valid, default hari ini digunakan.")

    def __repr__(self) -> str:
        return f"Tugas(ID:{self.id}, Matkul:'{self.matkul}', '{self.deskripsi}', Deadline:{self.deadline}, Prioritas:{self.prioritas}, Status:{self.status})"

    def to_dict(self) -> dict:
        return {
            "matkul": self.matkul,
            "deskripsi": self.deskripsi,
            "deadline": self.deadline.strftime("%Y-%m-%d"),
            "prioritas": self.prioritas,
            "status": self.status
        }
