# main_app.py
import streamlit as st
import matplotlib.pyplot as plt
import datetime
import pandas as pd

# Set page configuration
st.set_page_config(page_title="To-Do List", layout="wide", initial_sidebar_state="expanded")

# Import modul yang diperlukan
from model import Tugas
from manajer_tugas import ManajerTugas
from konfigurasi import DAFTAR_PRIORITAS, STATUS_TUGAS, PRIORITAS_DEFAULT, STATUS_DEFAULT

# Inisialisasi manajer tugas
@st.cache_resource(show_spinner=False)
def get_manajer_tugas():
    return ManajerTugas()

manajer = get_manajer_tugas()

# Fungsi untuk format tanggal agar seragam
def format_tanggal(tanggal):
    if isinstance(tanggal, str):
        try:
            tgl = datetime.datetime.strptime(tanggal, "%Y-%m-%d").date()
            return tgl.strftime("%d-%m-%Y")
        except:
            return tanggal
    elif isinstance(tanggal, datetime.date):
        return tanggal.strftime("%d-%m-%Y")
    return tanggal

# Halaman Input Tugas
def halaman_tambah():
    st.header("📝 Tambah Tugas Baru")
    with st.form("form_tambah_tugas", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            matkul = st.text_input("Mata Kuliah", placeholder="Contoh: Pemrograman Berorientasi Objek")
        with col2:
            deskripsi = st.text_input("Deskripsi Tugas", placeholder="Contoh: Selesaikan soal latihan")
        deadline = st.date_input("Deadline", value=datetime.date.today())
        prioritas = st.selectbox("Prioritas", DAFTAR_PRIORITAS, index=DAFTAR_PRIORITAS.index(PRIORITAS_DEFAULT))
        status = st.selectbox("Status Tugas", STATUS_TUGAS, index=STATUS_TUGAS.index(STATUS_DEFAULT))
        submitted = st.form_submit_button("💾 Simpan Tugas")
        
        if submitted:
            if not matkul:
                st.warning("Mata Kuliah tidak boleh kosong!", icon="⚠️")
            elif not deskripsi:
                st.warning("Deskripsi tugas tidak boleh kosong!", icon="⚠️")
            else:
                tugas_baru = Tugas(
                    matkul=matkul,
                    deskripsi=deskripsi,
                    deadline=deadline,
                    prioritas=prioritas,
                    status=status
                )
                if manajer.tambah_tugas(tugas_baru):
                    st.success("Tugas berhasil disimpan!", icon="✅")
                    st.cache_data.clear()  # Clear cache jika diperlukan untuk memperbarui tampilan data
                    st.rerun()
                else:
                    st.error("Gagal menyimpan tugas.")

# Halaman Daftar Tugas
def halaman_daftar():
    st.header("🗂️ Daftar Tugas")
    
    # Filter
    col1, col2 = st.columns(2)
    with col1:
        # Filter status
        status_filter = st.selectbox("Filter Status", ["Semua"] + STATUS_TUGAS)
        if status_filter == "Semua":
            status_filter = None
    
    with col2:
        # Filter prioritas
        prioritas_filter = st.selectbox("Filter Prioritas", ["Semua"] + DAFTAR_PRIORITAS)
        if prioritas_filter == "Semua":
            prioritas_filter = None

    
    # Tombol refresh
    if st.button("🔄 Refresh Daftar"):
        st.cache_data.clear()
        st.rerun()
        
    # Tampilkan data tugas dalam bentuk tabel menggunakan Pandas DataFrame
    df_tugas = manajer.get_dataframe_tugas(status_filter=status_filter, prioritas_filter=prioritas_filter)
    if df_tugas.empty:
        st.info("Belum ada tugas yang tersimpan.")
    else:
        # Format tanggal agar lebih mudah dibaca
        df_tugas["deadline"] = df_tugas["deadline"].apply(format_tanggal)
        st.dataframe(df_tugas.set_index("id"), use_container_width=True)
    
    # Edit Tugas
    st.subheader("Edit Tugas")
    id_edit = st.number_input("ID Tugas yang akan diedit", min_value=1, step=1, format="%d", key="edit_id")
    if st.session_state.get("edit_mode") or st.button("✏️ Edit Tugas"):
        st.session_state.edit_mode = True
        semua = manajer.get_semua_tugas_obj()
        tugas_terpilih = next((t for t in semua if t.id == id_edit), None)
        
        if not tugas_terpilih:
            st.error("Tugas tidak ditemukan.")
        else:
            with st.form("form_edit_tugas"):
                matkul_baru = st.text_input("Mata Kuliah", value=tugas_terpilih.matkul)
                deskripsi_baru = st.text_input("Deskripsi", value=tugas_terpilih.deskripsi)
                deadline_baru = st.date_input("Deadline", value=tugas_terpilih.deadline)
                prioritas_baru = st.selectbox("Prioritas", DAFTAR_PRIORITAS, index=DAFTAR_PRIORITAS.index(tugas_terpilih.prioritas))
                status_baru = st.selectbox("Status", STATUS_TUGAS, index=STATUS_TUGAS.index(tugas_terpilih.status))
                simpan = st.form_submit_button("Simpan Perubahan")

                if simpan:
                    tugas_baru = Tugas(
                        matkul=matkul_baru,
                        deskripsi=deskripsi_baru,
                        deadline=deadline_baru,
                        prioritas=prioritas_baru,
                        status=status_baru,
                        id_tugas=id_edit
                    )
                    if manajer.update_tugas(tugas_baru):
                        st.success(f"Tugas ID {tugas_baru.id} berhasil diperbarui.", icon="✅")
                        st.session_state.edit_mode = False
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Gagal memperbarui tugas.")

    # Kolom untuk aksi hapus dan tandai selesai
    st.subheader("Aksi Tugas")
    col1, col2 = st.columns(2)
    with col1:
        hapus_id = st.number_input("ID Tugas yang akan dihapus", min_value=1, step=1, format="%d")
        if st.button("🗑️ Hapus Tugas"):
            if manajer.hapus_tugas(hapus_id):
                st.success(f"Tugas ID {hapus_id} berhasil dihapus.", icon="✅")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Gagal menghapus tugas. Pastikan ID benar.")
    with col2:
        selesai_id = st.number_input("ID Tugas yang akan diselesaikan", min_value=1, step=1, format="%d", key="selesai")
        if st.button("✅ Tandai Selesai"):
            if manajer.tandai_selesai(selesai_id):
                st.success(f"Tugas ID {selesai_id} telah ditandai sebagai Complete.", icon="✅")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Gagal memperbarui status tugas. Pastikan ID benar.")


# Halaman Ringkasan Tugas 
def halaman_ringkasan():
    st.header("📊 Ringkasan & Analisis Tugas")
    col1, col2 = st.columns([1, 2])
    with col1:
        pilihan_periode = st.selectbox("Filter Periode:", ["Semua Waktu", "Hari Ini", "Pilih Tanggal Tertentu"], key="filter_periode")
        
    tanggal_filter = None
    label_periode = "(Semua Waktu)"
    if pilihan_periode == "Hari Ini":
        tanggal_filter = datetime.date.today()
        label_periode = f"({tanggal_filter.strftime('%d %b')})"
    elif pilihan_periode == "Pilih Tanggal Tertentu":
        tanggal_filter = st.date_input("Pilih Tanggal", value=datetime.date.today())
        label_periode = f"({tanggal_filter.strftime('%d %b %Y')})"

    with col2:
        total_tugas = manajer.hitung_total_tugas(tanggal_filter)
        st.metric(label=f"Total Tugas {label_periode}", value=f"{total_tugas} Tugas")
    
    df_tugas = manajer.get_dataframe_tugas(tanggal=tanggal_filter)
    if df_tugas.empty:
        st.info("Belum ada data tugas.")
        return

    # ==== Ringkasan berdasarkan Status ====
    df_summary = df_tugas.groupby("status").size().reset_index(name="Jumlah Tugas")
    st.subheader("Total Tugas Berdasarkan Status")

    col1, col2 = st.columns(2)
    with col1:
        st.write("Tabel:")
        st.dataframe(df_summary, use_container_width=True, hide_index=True)
    with col2:
        st.write("Grafik:")
        fig_pie, ax = plt.subplots(facecolor="none")  # <== INI kunci agar background transparan
        ax.pie(
            df_summary["Jumlah Tugas"],
            labels=df_summary["status"],
            autopct="%1.1f%%",
            textprops={'color': 'white'}  # teks label biar kontras di dark mode
        )
        ax.axis("equal")
        fig_pie.patch.set_alpha(0)  # transparan juga bagian luar figure
        st.pyplot(fig_pie)
        
    st.markdown("---")
    
    # ==== Ringkasan berdasarkan Prioritas ====
    df_prioritas = df_tugas.groupby("prioritas").size().reset_index(name="Jumlah")
    st.subheader("Total Tugas Berdasarkan Prioritas")

    col3, col4 = st.columns(2)
    with col3:
        st.write("Tabel:")
        st.dataframe(df_prioritas, use_container_width=True, hide_index=True)
    with col4:
        st.write("Grafik:")
        st.bar_chart(df_prioritas.set_index("prioritas"))

# Fungsi utama untuk routing halaman
def main():
    st.sidebar.title("📚 TugasKu")
    pilihan = st.sidebar.radio("Pilih Menu", ("Tambah Tugas", "Daftar Tugas", "Ringkasan & Analisis Tugas"))
    
    st.sidebar.markdown("---")
    st.sidebar.info("Tugas Besar - Aplikasi To-Do List") 
    
    if pilihan == "Tambah Tugas":
        halaman_tambah()
    elif pilihan == "Daftar Tugas":
        halaman_daftar()
    elif pilihan == "Ringkasan & Analisis Tugas":
        halaman_ringkasan()

    st.markdown("---")
    st.caption("Pengembangan Aplikasi Berbasis OOP")

if __name__ == "__main__":
    main()
