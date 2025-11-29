import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime
from io import BytesIO
import openpyxl 
import os
import warnings
import plotly.express as px 
import xlsxwriter
warnings.filterwarnings('ignore')



def export_to_excel():
    """Export semua data ke Excel termasuk buku besar per akun"""
    try:
        buffer = BytesIO()

        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Data transaksi dasar
            export_list = {
                "df_jurnal_umum": "Jurnal Umum",
                "df_jurnal_penyesuaian": "Jurnal Penyesuaian", 
                "df_neraca_saldo_periode_sebelumnya": "Neraca Saldo Periode Sebelumnya",
                "df_buku_besar": "Buku Besar (Flat)",
                "df_neraca_saldo": "Neraca Saldo",
                "df_jurnal_penutup": "Jurnal Penutup",
                "df_neraca_saldo_setelah_penutup": "Neraca Saldo Setelah Penutup",
                "df_penjualan": "Penjualan",
                "df_pembelian": "Pembelian", 
                "df_persediaan": "Persediaan",
                "df_riwayat_persediaan": "Riwayat Persediaan"
            }

            # Export data transaksi
            for key, sheet_name in export_list.items():
                if key in st.session_state and not st.session_state[key].empty:
                    df_to_export = st.session_state[key].copy()
                    if 'Tanggal' in df_to_export.columns:
                        df_to_export['Tanggal'] = df_to_export['Tanggal'].astype(str)
                    df_to_export.to_excel(writer, sheet_name=sheet_name, index=False)

            # Export Buku Besar per Akun
            if "buku_besar_per_akun" in st.session_state and st.session_state.buku_besar_per_akun:
                for akun, df_akun in st.session_state.buku_besar_per_akun.items():
                    # Bersihkan nama akun untuk nama sheet
                    sheet_name = akun[:31]  # Excel sheet name max 31 chars
                    df_akun.to_excel(writer, sheet_name=f"Buku Besar - {sheet_name}", index=False)

            # GENERATE LAPORAN KEUANGAN
            # ... [kode untuk laporan laba rugi, perubahan modal, posisi keuangan tetap sama] ...
            
            # Sheet ringkasan buku besar
            if "buku_besar_per_akun" in st.session_state and st.session_state.buku_besar_per_akun:
                ringkasan_akun = []
                for akun, df_akun in st.session_state.buku_besar_per_akun.items():
                    if not df_akun.empty:
                        saldo_akhir = df_akun["Saldo (Rp)"].iloc[-1]
                        total_debit = df_akun["Debit (Rp)"].sum()
                        total_kredit = df_akun["Kredit (Rp)"].sum()
                        
                        ringkasan_akun.append({
                            "Nama Akun": akun,
                            "Total Debit": total_debit,
                            "Total Kredit": total_kredit, 
                            "Saldo Akhir": saldo_akhir,
                            "Jumlah Transaksi": len(df_akun),
                            "Posisi": "Debit" if saldo_akhir > 0 else "Kredit" if saldo_akhir < 0 else "Nol"
                        })
                
                if ringkasan_akun:
                    pd.DataFrame(ringkasan_akun).to_excel(writer, sheet_name="Ringkasan_Buku_Besar", index=False)

        buffer.seek(0)
        return buffer

    except Exception as e:
        print(f"❌ Error dalam export_to_excel: {str(e)}")
        return create_fallback_export()
    
def create_fallback_export():
    """Membuat export fallback jika fungsi utama error"""
    buffer = BytesIO()
    try:
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            error_data = {
                "Error": [f"Terjadi error saat export: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"],
                "Solusi": ["Refresh halaman dan coba lagi"]
            }
            pd.DataFrame(error_data).to_excel(writer, sheet_name="Error_Info", index=False)
        buffer.seek(0)
        return buffer
    except:
        buffer.write(b"Backup Data")
        buffer.seek(0)
        return buffer

def simple_export_to_excel():
    """Fungsi export sederhana sebagai fallback"""
    try:
        buffer = BytesIO()
        
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Export data dasar saja
            basic_sheets = {
                "df_jurnal_umum": "Jurnal Umum",
                "df_buku_besar": "Buku Besar", 
                "df_neraca_saldo": "Neraca Saldo"
            }
            
            for key, sheet_name in basic_sheets.items():
                if key in st.session_state and not st.session_state[key].empty:
                    st.session_state[key].to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    # Buat sheet kosong
                    pd.DataFrame(columns=["Data", "Tersedia"]).to_excel(
                        writer, sheet_name=sheet_name, index=False
                    )
        
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        # Fallback paling sederhana
        buffer = BytesIO()
        buffer.write(b"Simple Excel Export - Error in main export")
        buffer.seek(0)
        return buffer
    
    
def init_database():
    """Inisialisasi file database Excel - VERSI DIPERBAIKI"""
    try:
        if not os.path.exists("database_keuangan.xlsx"):
            with pd.ExcelWriter("database_keuangan.xlsx", engine='openpyxl') as writer:
                # Sheet untuk setiap jenis data
                pd.DataFrame(columns=["No", "Tanggal", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"]).to_excel(writer, sheet_name="jurnal_umum", index=False)
                pd.DataFrame(columns=["No", "Tanggal", "Keterangan", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"]).to_excel(writer, sheet_name="jurnal_penyesuaian", index=False)
                pd.DataFrame(columns=["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"]).to_excel(writer, sheet_name="neraca_saldo_sebelumnya", index=False)
                pd.DataFrame(columns=["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"]).to_excel(writer, sheet_name="buku_besar", index=False)
                pd.DataFrame(columns=["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"]).to_excel(writer, sheet_name="neraca_saldo", index=False)
                pd.DataFrame(columns=["No", "Tanggal", "Keterangan", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"]).to_excel(writer, sheet_name="jurnal_penutup", index=False)
                pd.DataFrame(columns=["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"]).to_excel(writer, sheet_name="neraca_setelah_penutup", index=False)
                
                # SHEET BARU: Sistem Penjualan dan Persediaan
                pd.DataFrame(columns=["No", "Tanggal", "Keterangan", "Akun Debit 1", "Debit 1 (Rp)", "Akun Debit 2", "Debit 2 (Rp)", 
                                    "Akun Kredit 1", "Kredit 1 (Rp)", "Akun Kredit 2", "Kredit 2 (Rp)", "Barang", "Jumlah", "Harga Jual", "HPP"]).to_excel(writer, sheet_name="penjualan", index=False)
                pd.DataFrame(columns=["No", "Tanggal", "Keterangan", "Barang", "Jumlah", "Harga Beli", "Total Pembelian"]).to_excel(writer, sheet_name="pembelian", index=False)
                pd.DataFrame(columns=["Barang", "Stok Awal", "Pembelian", "Penjualan", "Stok Akhir", "Harga Rata-rata", "Total Nilai"]).to_excel(writer, sheet_name="persediaan", index=False)
                pd.DataFrame(columns=["Tanggal", "Jenis", "Barang", "Jumlah", "Harga", "Total", "Stok", "Keterangan"]).to_excel(writer, sheet_name="riwayat_persediaan", index=False)
                pd.DataFrame(columns=["Periode", "Tanggal_Simpan", "Data"]).to_excel(writer, sheet_name="riwayat_periode", index=False)
            print("✅ Database berhasil dibuat!")
    except Exception as e:
        print(f"❌ Error dalam init_database: {str(e)}")
        
# Tambahkan di bagian inisialisasi sistem (setelah init_database())
def init_session_state_fixed():
    """Inisialisasi session state dengan nilai default yang aman - VERSI DIPERBAIKI"""
    try:
        default_dataframes = {
            "df_jurnal_umum": ["No", "Tanggal", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"],
            "df_jurnal_penyesuaian": ["No", "Tanggal", "Keterangan", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"],
            "df_neraca_saldo_periode_sebelumnya": ["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"],
            "df_buku_besar": ["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"],
            "df_neraca_saldo": ["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"],
            "df_jurnal_penutup": ["No", "Tanggal", "Keterangan", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"],
            "df_neraca_saldo_setelah_penutup": ["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"],
            "df_penjualan": ["No", "Tanggal", "Keterangan", "Barang", "Jumlah", "Harga Jual", "Total Penjualan", "HPP", "Total HPP"],
            "df_pembelian": ["No", "Tanggal", "Keterangan", "Barang", "Jumlah", "Harga Beli", "Total Pembelian"],
            "df_persediaan": ["Barang", "Stok Awal", "Pembelian", "Penjualan", "Stok Akhir", "Harga Rata-rata", "Total Nilai"],
            "df_riwayat_persediaan": ["Tanggal", "Jenis", "Barang", "Jumlah", "Harga", "Total", "Stok", "Keterangan"],
            "df_laporan_laba_rugi": ["Keterangan", "Nilai (Rp)"],
            "df_laporan_perubahan_modal": ["Keterangan", "Nilai (Rp)"],
            "df_laporan_posisi_keuangan": ["Keterangan", "Nilai (Rp)"]
        }
        
        for df_key, columns in default_dataframes.items():
            if df_key not in st.session_state:
                st.session_state[df_key] = pd.DataFrame(columns=columns)
        
        # Inisialisasi counter transaksi
        if "transaction_counter" not in st.session_state:
            st.session_state.transaction_counter = 1
        
        # Inisialisasi buku besar per akun
        if "buku_besar_per_akun" not in st.session_state:
            st.session_state.buku_besar_per_akun = {}
        
        # INISIALISASI PENTING: Pastikan tanggal_awal_periode ada
        if "tanggal_awal_periode" not in st.session_state:
            from datetime import date
            # Default: awal bulan ini
            st.session_state.tanggal_awal_periode = date.today().replace(day=1)
            print("✅ tanggal_awal_periode diinisialisasi:", st.session_state.tanggal_awal_periode)
        
        # INISIALISASI PENTING: Pastikan periode_sekarang ada
        if "periode_sekarang" not in st.session_state:
            from datetime import datetime
            st.session_state.periode_sekarang = datetime.now().strftime("%B %Y")
            print("✅ periode_sekarang diinisialisasi:", st.session_state.periode_sekarang)
        
        # Inisialisasi variabel laporan keuangan
        if "total_pendapatan" not in st.session_state:
            st.session_state.total_pendapatan = 0
        if "total_beban" not in st.session_state:
            st.session_state.total_beban = 0
        if "laba_bersih" not in st.session_state:
            st.session_state.laba_bersih = 0
        if "modal_awal" not in st.session_state:
            st.session_state.modal_awal = 0
        if "modal_akhir" not in st.session_state:
            st.session_state.modal_akhir = 0
            
        # INISIALISASI PENTING: Pastikan neraca saldo periode sebelumnya ada data contoh untuk testing
        if "df_neraca_saldo_periode_sebelumnya" in st.session_state and st.session_state.df_neraca_saldo_periode_sebelumnya.empty:
            # Data contoh untuk memulai sistem
            contoh_data = [
                {"No": 1, "Nama Akun": "Kas", "Debit (Rp)": 100000000, "Kredit (Rp)": 0},
                {"No": 2, "Nama Akun": "Persediaan", "Debit (Rp)": 50000000, "Kredit (Rp)": 0},
                {"No": 3, "Nama Akun": "Peralatan", "Debit (Rp)": 75000000, "Kredit (Rp)": 0},
                {"No": 4, "Nama Akun": "Utang Usaha", "Debit (Rp)": 0, "Kredit (Rp)": 45000000},
                {"No": 5, "Nama Akun": "Modal", "Debit (Rp)": 0, "Kredit (Rp)": 180000000},
            ]
            st.session_state.df_neraca_saldo_periode_sebelumnya = pd.DataFrame(contoh_data)
            print("✅ Data contoh neraca saldo periode sebelumnya diinisialisasi")
        
        print("✅ Session state berhasil diinisialisasi dengan lengkap")
        return True
        
    except Exception as e:
        print(f"❌ Error dalam init_session_state_fixed: {str(e)}")
        return False

def load_data_periode(periode):
    """Memuat data untuk periode tertentu - VERSI DIPERBAIKI"""
    try:
        # Coba muat neraca saldo sebelumnya dari riwayat
        neraca_sebelumnya = muat_dari_riwayat_periode(periode)
        
        if not neraca_sebelumnya.empty:
            st.session_state.df_neraca_saldo_periode_sebelumnya = neraca_sebelumnya
            st.success(f"✅ Berhasil memuat neraca saldo periode sebelumnya untuk {periode}")
        else:
            # Jika tidak ada data, pertahankan data yang ada atau gunakan contoh
            if st.session_state.df_neraca_saldo_periode_sebelumnya.empty:
                st.info(f"ℹ️ Tidak ada data periode sebelumnya untuk {periode}. Menggunakan data default.")
        
        # Reset data transaksi untuk periode baru
        reset_data_periode_baru()
        
        print(f"✅ Data periode {periode} berhasil dimuat")
        return True
    except Exception as e:
        print(f"❌ Error load data periode: {str(e)}")
        return False
    
    
def load_from_database():
    """Load semua data dari database Excel - VERSI DIPERBAIKI"""
    try:
        if os.path.exists("database_keuangan.xlsx"):
            sheets_to_load = {
                "jurnal_umum": "df_jurnal_umum",
                "jurnal_penyesuaian": "df_jurnal_penyesuaian",
                "neraca_saldo_sebelumnya": "df_neraca_saldo_periode_sebelumnya", 
                "buku_besar": "df_buku_besar",
                "neraca_saldo": "df_neraca_saldo",
                "jurnal_penutup": "df_jurnal_penutup",
                "neraca_setelah_penutup": "df_neraca_saldo_setelah_penutup",
                # SHEET BARU
                "penjualan": "df_penjualan",
                "pembelian": "df_pembelian",
                "persediaan": "df_persediaan",
                "riwayat_persediaan": "df_riwayat_persediaan"
            }
            
            loaded_count = 0
            for sheet_name, session_key in sheets_to_load.items():
                try:
                    df = pd.read_excel("database_keuangan.xlsx", sheet_name=sheet_name)
                    if not df.empty:
                        if 'Tanggal' in df.columns:
                            df['Tanggal'] = pd.to_datetime(df['Tanggal']).dt.date
                        st.session_state[session_key] = df
                        loaded_count += 1
                except:
                    st.session_state[session_key] = pd.DataFrame()
            
            print(f"✅ Successfully loaded {loaded_count} sheets from database")
            return True
        else:
            print("❌ Database file not found")
            return False
    except Exception as e:
        print(f"❌ Error in load_from_database: {str(e)}")
        return False

def save_to_database():
    """Simpan semua data ke database Excel - VERSI DIPERBAIKI"""
    try:
        sheets_to_save = {
            "jurnal_umum": "df_jurnal_umum",
            "jurnal_penyesuaian": "df_jurnal_penyesuaian",
            "neraca_saldo_sebelumnya": "df_neraca_saldo_periode_sebelumnya",
            "buku_besar": "df_buku_besar", 
            "neraca_saldo": "df_neraca_saldo",
            "jurnal_penutup": "df_jurnal_penutup",
            "neraca_setelah_penutup": "df_neraca_saldo_setelah_penutup",
            # SHEET BARU
            "penjualan": "df_penjualan",
            "pembelian": "df_pembelian",
            "persediaan": "df_persediaan",
            "riwayat_persediaan": "df_riwayat_persediaan"
        }
        
        with pd.ExcelWriter("database_keuangan.xlsx", engine='openpyxl') as writer:
            for sheet_name, session_key in sheets_to_save.items():
                if session_key in st.session_state and not st.session_state[session_key].empty:
                    df_to_save = st.session_state[session_key].copy()
                    if 'Tanggal' in df_to_save.columns:
                        df_to_save['Tanggal'] = df_to_save['Tanggal'].astype(str)
                    df_to_save.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return True
    except Exception as e:
        st.error(f"Error saving to database: {str(e)}")
        return False

def simpan_ke_riwayat_periode(periode, data_neraca_setelah_penutup):
    """Menyimpan neraca saldo setelah penutup ke riwayat periode - VERSI DIPERBAIKI"""
    try:
        if os.path.exists("database_keuangan.xlsx"):
            # Load existing data
            try:
                df_riwayat = pd.read_excel("database_keuangan.xlsx", sheet_name="riwayat_periode")
            except:
                df_riwayat = pd.DataFrame(columns=["Periode", "Tanggal_Simpan", "Data"])
            
            # Convert DataFrame to JSON string for storage
            data_json = data_neraca_setelah_penutup.to_json()
            
            # Check if periode already exists
            if periode in df_riwayat["Periode"].values:
                # Update existing
                df_riwayat.loc[df_riwayat["Periode"] == periode, ["Tanggal_Simpan", "Data"]] = [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    data_json
                ]
            else:
                # Add new
                new_row = {
                    "Periode": periode,
                    "Tanggal_Simpan": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Data": data_json
                }
                df_riwayat = pd.concat([df_riwayat, pd.DataFrame([new_row])], ignore_index=True)
            
            # Save back to Excel
            with pd.ExcelWriter("database_keuangan.xlsx", engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df_riwayat.to_excel(writer, sheet_name="riwayat_periode", index=False)
            
            print(f"✅ Data periode {periode} berhasil disimpan ke riwayat")
            return True
    except Exception as e:
        print(f"❌ Error menyimpan riwayat periode: {str(e)}")
        return False

def muat_dari_riwayat_periode(periode):
    """Memuat neraca saldo setelah penutup dari riwayat periode - VERSI DIPERBAIKI"""
    try:
        if os.path.exists("database_keuangan.xlsx"):
            df_riwayat = pd.read_excel("database_keuangan.xlsx", sheet_name="riwayat_periode")
            
            if not df_riwayat.empty and periode in df_riwayat["Periode"].values:
                data_json = df_riwayat[df_riwayat["Periode"] == periode]["Data"].iloc[0]
                data_neraca = pd.read_json(data_json)
                print(f"✅ Data periode {periode} berhasil dimuat dari riwayat")
                return data_neraca
    except Exception as e:
        print(f"❌ Error memuat riwayat periode: {str(e)}")
    
    return pd.DataFrame()

def dapatkan_periode_sebelumnya(periode_sekarang):
    """Mendapatkan nama periode sebelumnya berdasarkan periode saat ini"""
    try:
        bulan_tahun = periode_sekarang.split()
        if len(bulan_tahun) == 2:
            bulan, tahun = bulan_tahun
            tahun = int(tahun)
            
            # Mapping nama bulan ke angka
            bulan_ke_angka = {
                "Januari": 1, "Februari": 2, "Maret": 3, "April": 4, "Mei": 5, "Juni": 6,
                "Juli": 7, "Agustus": 8, "September": 9, "Oktober": 10, "November": 11, "Desember": 12
            }
            
            if bulan in bulan_ke_angka:
                bulan_angka = bulan_ke_angka[bulan]
                
                # Hitung periode sebelumnya
                if bulan_angka == 1:
                    bulan_sebelumnya = "Desember"
                    tahun_sebelumnya = tahun - 1
                else:
                    bulan_sebelumnya = list(bulan_ke_angka.keys())[bulan_angka - 2]
                    tahun_sebelumnya = tahun
                
                return f"{bulan_sebelumnya} {tahun_sebelumnya}"
    except Exception as e:
        print(f"Error mendapatkan periode sebelumnya: {e}")
    
    return "Periode Sebelumnya"

def muat_dari_riwayat_periode(periode):
    """Memuat neraca saldo setelah penutup dari riwayat periode"""
    try:
        if os.path.exists("database_keuangan.xlsx"):
            df_riwayat = pd.read_excel("database_keuangan.xlsx", sheet_name="riwayat_periode")
            
            if not df_riwayat.empty and periode in df_riwayat["Periode"].values:
                data_json = df_riwayat[df_riwayat["Periode"] == periode]["Data"].iloc[0]
                data_neraca = pd.read_json(data_json)
                print(f"✅ Data periode {periode} berhasil dimuat dari riwayat")
                return data_neraca
    except Exception as e:
        print(f"❌ Error memuat riwayat periode: {str(e)}")
    
    return pd.DataFrame()
    

def load_from_database():
    """Load semua data dari database Excel - VERSI DIPERBAIKI"""
    try:
        if os.path.exists("database_keuangan.xlsx"):
            # Load setiap sheet
            sheets_to_load = {
                "jurnal_umum": "df_jurnal_umum",
                "jurnal_penyesuaian": "df_jurnal_penyesuaian",
                "neraca_saldo_sebelumnya": "df_neraca_saldo_periode_sebelumnya", 
                "buku_besar": "df_buku_besar",
                "neraca_saldo": "df_neraca_saldo",
                "jurnal_penutup": "df_jurnal_penutup",
                "neraca_setelah_penutup": "df_neraca_saldo_setelah_penutup"
            }
            
            loaded_count = 0
            for sheet_name, session_key in sheets_to_load.items():
                try:
                    df = pd.read_excel("database_keuangan.xlsx", sheet_name=sheet_name)
                    if not df.empty:
                        # Konversi tipe data kolom tanggal jika ada
                        if 'Tanggal' in df.columns:
                            df['Tanggal'] = pd.to_datetime(df['Tanggal']).dt.date
                        
                        st.session_state[session_key] = df
                        loaded_count += 1
                        print(f"✅ Loaded {len(df)} rows from {sheet_name}")
                    else:
                        # Jika sheet kosong, inisialisasi dengan DataFrame kosong
                        st.session_state[session_key] = pd.DataFrame()
                except Exception as e:
                    print(f"❌ Error loading {sheet_name}: {str(e)}")
                    # Inisialisasi dengan DataFrame kosong jika error
                    st.session_state[session_key] = pd.DataFrame()
            
            print(f"✅ Successfully loaded {loaded_count} sheets from database")
            return True
        else:
            print("❌ Database file not found")
            return False
    except Exception as e:
        print(f"❌ Error in load_from_database: {str(e)}")
        return False
    
    
def safe_dataframe_display(df):
    """Membuat DataFrame yang aman untuk ditampilkan dengan format yang benar"""
    try:
        df_display = df.copy()
        
        # Format kolom numerik ke string Rupiah
        numeric_columns = ["Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"]
        
        for col in numeric_columns:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(
                    lambda x: f"Rp {safe_float_convert(x):,.0f}" if pd.notna(x) and x != "" and safe_float_convert(x) != 0 else ""
                )
        
        return df_display
    except Exception as e:
        print(f"Error dalam safe_dataframe_display: {str(e)}")
        return df


    # ==================== INISIALISASI SISTEM ====================

# Inisialisasi database
init_database()

# Load data dari database saat aplikasi dimulai
if "system_initialized" not in st.session_state:
    print("🔄 Initializing system and loading data from database...")
    load_from_database()
    st.session_state.system_initialized = True
    print("✅ System initialization completed")

# Inisialisasi session state untuk data yang belum ada
default_dataframes = {
    "df_jurnal_umum": ["No", "Tanggal", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"],
    "df_jurnal_penyesuaian": ["No", "Tanggal", "Keterangan", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"],
    "df_neraca_saldo_periode_sebelumnya": ["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"],
    "df_buku_besar": ["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"],
    "df_neraca_saldo": ["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"],
    "df_jurnal_penutup": ["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"],
    "df_neraca_saldo_setelah_penutup": ["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"],
    "df_jurnal_umum_old_format": ["Tanggal", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"],
    "df_semua_transaksi": ["Tanggal", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"]
}

for df_key, columns in default_dataframes.items():
    if df_key not in st.session_state:
        st.session_state[df_key] = pd.DataFrame(columns=columns)

# user data - Tetap di session state karena bersifat sementara
if "users" not in st.session_state:
    st.session_state.users = {
        "admin": "admin123",
       
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    
if "periode_sekarang" not in st.session_state:
    from datetime import datetime
    st.session_state.periode_sekarang = datetime.now().strftime("%B %Y")

# Daftar periode yang tersedia
if "daftar_periode" not in st.session_state:
    st.session_state.daftar_periode = [st.session_state.periode_sekarang]



def load_data_periode(periode):
    """Memuat data untuk periode tertentu"""
    try:
        # Load neraca saldo sebelumnya dari riwayat
        neraca_sebelumnya = muat_dari_riwayat_periode(periode)
        
        if not neraca_sebelumnya.empty:
            st.session_state.df_neraca_saldo_periode_sebelumnya = neraca_sebelumnya
        else:
            # Jika tidak ada data, buat neraca kosong
            st.session_state.df_neraca_saldo_periode_sebelumnya = pd.DataFrame(
                columns=["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"]
            )
        
        # Reset data transaksi untuk periode baru
        st.session_state.df_jurnal_umum = pd.DataFrame(
            columns=["No", "Tanggal", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"]
        )
        st.session_state.df_jurnal_penyesuaian = pd.DataFrame(
            columns=["No", "Tanggal", "Keterangan", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"]
        )
        st.session_state.df_jurnal_penutup = pd.DataFrame(
            columns=["No", "Tanggal", "Keterangan", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"]
        )
        
        # Reset buku besar dan neraca saldo
        st.session_state.df_buku_besar = pd.DataFrame(columns=["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"])
        st.session_state.df_neraca_saldo = pd.DataFrame(columns=["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"])
        st.session_state.df_neraca_saldo_setelah_penutup = pd.DataFrame(columns=["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"])
        
        print(f"✅ Data periode {periode} berhasil dimuat")
        return True
    except Exception as e:
        print(f"❌ Error load data periode: {str(e)}")
        return False
    
def reset_data_periode_baru():
    """Reset semua data transaksi untuk periode baru, tetapi pertahankan neraca saldo periode sebelumnya"""
    try:
        # Reset data transaksi periode berjalan
        st.session_state.df_jurnal_umum = pd.DataFrame(
            columns=["No", "Tanggal", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"]
        )
        st.session_state.df_jurnal_penyesuaian = pd.DataFrame(
            columns=["No", "Tanggal", "Keterangan", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"]
        )
        st.session_state.df_jurnal_penutup = pd.DataFrame(
            columns=["No", "Tanggal", "Keterangan", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"]
        )
        
        # Reset buku besar dan neraca saldo periode berjalan
        st.session_state.df_buku_besar = pd.DataFrame(columns=["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"])
        st.session_state.df_neraca_saldo = pd.DataFrame(columns=["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"])
        
        # Reset transaction counter untuk periode baru
        st.session_state.transaction_counter = 1
        
        # Reset buku besar per akun
        st.session_state.buku_besar_per_akun = {}
        
        # Reset laporan keuangan periode berjalan
        st.session_state.df_laporan_laba_rugi = pd.DataFrame()
        st.session_state.df_laporan_perubahan_modal = pd.DataFrame()
        st.session_state.df_laporan_posisi_keuangan = pd.DataFrame()
        
        print(f"✅ Data transaksi berhasil direset untuk periode baru")
        return True
    except Exception as e:
        print(f"❌ Error reset data periode: {str(e)}")
        return False
    
    
def save_to_database():
    """Simpan semua data ke database Excel - VERSI DIPERBAIKI"""
    try:
        sheets_to_save = {
            "jurnal_umum": "df_jurnal_umum",
            "jurnal_penyesuaian": "df_jurnal_penyesuaian",
            "neraca_saldo_sebelumnya": "df_neraca_saldo_periode_sebelumnya",
            "buku_besar": "df_buku_besar", 
            "neraca_saldo": "df_neraca_saldo",
            "jurnal_penutup": "df_jurnal_penutup",
            "neraca_setelah_penutup": "df_neraca_saldo_setelah_penutup"
        }
        
        with pd.ExcelWriter("database_keuangan.xlsx", engine='openpyxl') as writer:
            for sheet_name, session_key in sheets_to_save.items():
                if session_key in st.session_state and not st.session_state[session_key].empty:
                    # Buat copy untuk menghindari modifikasi session state
                    df_to_save = st.session_state[session_key].copy()
                    
                    # Konversi tanggal ke string untuk menghindari Excel warning
                    if 'Tanggal' in df_to_save.columns:
                        df_to_save['Tanggal'] = df_to_save['Tanggal'].astype(str)
                    
                    df_to_save.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"✅ Saved {len(df_to_save)} rows to {sheet_name}")
                else:
                    # Buat sheet kosong jika data tidak ada
                    pd.DataFrame().to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"ℹ️ No data to save for {sheet_name}")
        
        print("✅ All data successfully saved to database")
        return True
    except Exception as e:
        print(f"❌ Error saving to database: {str(e)}")
        st.error(f"Gagal menyimpan ke database: {str(e)}")
        return False

def hapus_catatan_persediaan_terkait(transaksi_yang_dihapus, transaction_no):
    """Menghapus catatan persediaan yang terkait dengan transaksi yang dihapus"""
    try:
        # Cek apakah ini transaksi pembelian (mengandung akun "Persediaan" di debit)
        is_pembelian = False
        barang_dibeli = None
        jumlah_pembelian = 0
        total_pembelian = 0
        
        for _, transaksi in transaksi_yang_dihapus.iterrows():
            if transaksi["Akun Debit"] == "Persediaan" and transaksi["Debit (Rp)"] > 0:
                is_pembelian = True
                total_pembelian = transaksi["Debit (Rp)"]
                # Cari informasi barang dari dataframe pembelian
                if "df_pembelian" in st.session_state and not st.session_state.df_pembelian.empty:
                    pembelian_terkait = st.session_state.df_pembelian[
                        st.session_state.df_pembelian["Total Pembelian"] == total_pembelian
                    ]
                    if not pembelian_terkait.empty:
                        barang_dibeli = pembelian_terkait.iloc[0]["Barang"]
                        jumlah_pembelian = pembelian_terkait.iloc[0]["Jumlah"]
                break
        
        if is_pembelian and barang_dibeli:
            # 1. Hapus dari dataframe pembelian
            if "df_pembelian" in st.session_state and not st.session_state.df_pembelian.empty:
                st.session_state.df_pembelian = st.session_state.df_pembelian[
                    st.session_state.df_pembelian["Total Pembelian"] != total_pembelian
                ].copy()
                # Reset nomor urut pembelian
                st.session_state.df_pembelian = st.session_state.df_pembelian.reset_index(drop=True)
                st.session_state.df_pembelian["No"] = range(1, len(st.session_state.df_pembelian) + 1)
            
            # 2. Update persediaan - kurangi stok
            if "df_persediaan" in st.session_state and not st.session_state.df_persediaan.empty:
                barang_index = st.session_state.df_persediaan[
                    st.session_state.df_persediaan["Barang"] == barang_dibeli
                ].index
                
                if len(barang_index) > 0:
                    idx = barang_index[0]
                    
                    # Kurangi pembelian dan update stok
                    st.session_state.df_persediaan.at[idx, "Pembelian"] = max(
                        0, st.session_state.df_persediaan.at[idx, "Pembelian"] - jumlah_pembelian
                    )
                    
                    # Hitung ulang stok akhir
                    stok_awal = st.session_state.df_persediaan.at[idx, "Stok Awal"]
                    pembelian_baru = st.session_state.df_persediaan.at[idx, "Pembelian"]
                    penjualan = st.session_state.df_persediaan.at[idx, "Penjualan"]
                    st.session_state.df_persediaan.at[idx, "Stok Akhir"] = stok_awal + pembelian_baru - penjualan
                    
                    # Hitung ulang total nilai
                    stok_akhir = st.session_state.df_persediaan.at[idx, "Stok Akhir"]
                    harga_rata = st.session_state.df_persediaan.at[idx, "Harga Rata-rata"]
                    st.session_state.df_persediaan.at[idx, "Total Nilai"] = stok_akhir * harga_rata
            
            # 3. Hapus dari riwayat persediaan
            if "df_riwayat_persediaan" in st.session_state and not st.session_state.df_riwayat_persediaan.empty:
                # Hapus entri pembelian dengan total yang sama
                st.session_state.df_riwayat_persediaan = st.session_state.df_riwayat_persediaan[
                    ~(
                        (st.session_state.df_riwayat_persediaan["Jenis"] == "Pembelian") &
                        (st.session_state.df_riwayat_persediaan["Barang"] == barang_dibeli) &
                        (st.session_state.df_riwayat_persediaan["Total"] == total_pembelian)
                    )
                ].copy()
                
                # Reset index riwayat
                st.session_state.df_riwayat_persediaan = st.session_state.df_riwayat_persediaan.reset_index(drop=True)
            
            print(f"✅ Berhasil hapus catatan persediaan untuk transaksi #{transaction_no}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error dalam hapus_catatan_persediaan_terkait: {str(e)}")
        return False
    
    
def hapus_catatan_penjualan_terkait(transaksi_yang_dihapus, transaction_no):
    """Menghapus catatan penjualan yang terkait dengan transaksi yang dihapus"""
    try:
        # Cek apakah ini transaksi penjualan (mengandung akun "Penjualan" di kredit)
        is_penjualan = False
        barang_dijual = None
        total_penjualan = 0
        
        for _, transaksi in transaksi_yang_dihapus.iterrows():
            if transaksi["Akun Kredit"] == "Penjualan" and transaksi["Kredit (Rp)"] > 0:
                is_penjualan = True
                total_penjualan = transaksi["Kredit (Rp)"]
                # Cari informasi barang dari dataframe penjualan
                if "df_penjualan" in st.session_state and not st.session_state.df_penjualan.empty:
                    penjualan_terkait = st.session_state.df_penjualan[
                        st.session_state.df_penjualan["Total Penjualan"] == total_penjualan
                    ]
                    if not penjualan_terkait.empty:
                        barang_dijual = penjualan_terkait.iloc[0]["Barang"]
                break
        
        if is_penjualan and barang_dijual:
            # 1. Hapus dari dataframe penjualan
            if "df_penjualan" in st.session_state and not st.session_state.df_penjualan.empty:
                st.session_state.df_penjualan = st.session_state.df_penjualan[
                    st.session_state.df_penjualan["Total Penjualan"] != total_penjualan
                ].copy()
                # Reset nomor urut penjualan
                st.session_state.df_penjualan = st.session_state.df_penjualan.reset_index(drop=True)
                st.session_state.df_penjualan["No"] = range(1, len(st.session_state.df_penjualan) + 1)
            
            # 2. Update persediaan - tambah stok (karena penjualan dibatalkan)
            if "df_persediaan" in st.session_state and not st.session_state.df_persediaan.empty:
                barang_index = st.session_state.df_persediaan[
                    st.session_state.df_persediaan["Barang"] == barang_dijual
                ].index
                
                if len(barang_index) > 0:
                    idx = barang_index[0]
                    
                    # Kurangi penjualan (karena dibatalkan)
                    penjualan_terkait_df = st.session_state.df_penjualan[
                        (st.session_state.df_penjualan["Barang"] == barang_dijual) &
                        (st.session_state.df_penjualan["Total Penjualan"] == total_penjualan)
                    ]
                    
                    if not penjualan_terkait_df.empty:
                        jumlah_penjualan = penjualan_terkait_df.iloc[0]["Jumlah"]
                        st.session_state.df_persediaan.at[idx, "Penjualan"] = max(
                            0, st.session_state.df_persediaan.at[idx, "Penjualan"] - jumlah_penjualan
                        )
                        
                        # Hitung ulang stok akhir
                        stok_awal = st.session_state.df_persediaan.at[idx, "Stok Awal"]
                        pembelian = st.session_state.df_persediaan.at[idx, "Pembelian"]
                        penjualan_baru = st.session_state.df_persediaan.at[idx, "Penjualan"]
                        st.session_state.df_persediaan.at[idx, "Stok Akhir"] = stok_awal + pembelian - penjualan_baru
            
            # 3. Hapus dari riwayat persediaan
            if "df_riwayat_persediaan" in st.session_state and not st.session_state.df_riwayat_persediaan.empty:
                # Hapus entri penjualan dengan total yang sama
                st.session_state.df_riwayat_persediaan = st.session_state.df_riwayat_persediaan[
                    ~(
                        (st.session_state.df_riwayat_persediaan["Jenis"] == "Penjualan") &
                        (st.session_state.df_riwayat_persediaan["Barang"] == barang_dijual) &
                        (st.session_state.df_riwayat_persediaan["Total"] == total_penjualan)
                    )
                ].copy()
                
                # Reset index riwayat
                st.session_state.df_riwayat_persediaan = st.session_state.df_riwayat_persediaan.reset_index(drop=True)
            
            print(f"✅ Berhasil hapus catatan penjualan untuk transaksi #{transaction_no}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error dalam hapus_catatan_penjualan_terkait: {str(e)}")
        return False
    
    
def delete_transaction(transaction_no, password):
    """Hapus transaksi dari jurnal umum dengan verifikasi password - VERSI DIPERBAIKI"""
    try:
        # Verifikasi password admin
        if password != "admin123":
            return False, "Password salah!"
        
        if "df_jurnal_umum" in st.session_state and not st.session_state.df_jurnal_umum.empty:
            # Simpan data transaksi yang akan dihapus untuk referensi
            transaksi_yang_dihapus = st.session_state.df_jurnal_umum[
                st.session_state.df_jurnal_umum["No"] == transaction_no
            ].copy()
            
            # Hapus semua entri dengan nomor transaksi yang sama dari jurnal umum
            df_awal = st.session_state.df_jurnal_umum
            df_setelah_hapus = df_awal[df_awal["No"] != transaction_no].copy()
            
            # Reset nomor urut dengan benar
            df_setelah_hapus = df_setelah_hapus.reset_index(drop=True)
            
            # Dapatkan nomor transaksi unik yang tersisa
            unique_nos = df_setelah_hapus["No"].unique()
            unique_nos.sort()
            
            # Buat mapping dari nomor lama ke nomor baru yang berurutan
            mapping = {old_no: new_no for new_no, old_no in enumerate(unique_nos, 1)}
            
            # Terapkan mapping ke kolom No
            df_setelah_hapus["No"] = df_setelah_hapus["No"].map(mapping)
            
            st.session_state.df_jurnal_umum = df_setelah_hapus
            
            # ========== HAPUS CATATAN PERSEDIAAN/PENJUALAN YANG TERKAIT ==========
            if not transaksi_yang_dihapus.empty:
                # Cek jenis transaksi dan hapus catatan terkait
                hapus_catatan_persediaan_terkait(transaksi_yang_dihapus, transaction_no)
                hapus_catatan_penjualan_terkait(transaksi_yang_dihapus, transaction_no)
            # ====================================================================
            
            # Update sistem
            update_sistem_dengan_struktur_baru()
            
            # AUTO-SAVE SETELAH DELETE
            auto_save()
            
            return True, "Transaksi dan catatan persediaan terkait berhasil dihapus!"
        else:
            return False, "Tidak ada data transaksi!"
            
    except Exception as e:
        return False, f"Error: {str(e)}"
    
    
def safe_float_convert(value, default=0.0):
    """Mengonversi value ke float dengan aman - VERSI DIPERBAIKI"""
    try:
        if pd.isna(value) or value == '' or value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Bersihkan string dari format Rupiah dan karakter non-numerik
            cleaned = str(value).replace('Rp', '').replace('.', '').replace(',', '.').replace(' ', '').strip()
            # Hapus karakter non-digit kecuali titik dan minus
            cleaned = ''.join(ch for ch in cleaned if ch.isdigit() or ch in ['.', '-'])
            if cleaned == '' or cleaned == '-' or cleaned == '.':
                return default
            return float(cleaned)
        return float(value)
    except (ValueError, TypeError):
        return default
    
def parse_rupiah(rupiah_str):
    """Parse string rupiah menjadi float"""
    if not rupiah_str:
        return 0.0
    # Hapus titik dan spasi, ganti koma dengan titik untuk decimal
    clean_str = str(rupiah_str).replace('.', '').replace(' ', '').replace(',', '.')
    try:
        return float(clean_str)
    except:
        return 0.0

def format_rupiah(angka):
    """Format angka menjadi string dengan pemisah ribuan"""
    try:
        if pd.isna(angka) or angka == 0:
            return "0"
        # Pastikan angka adalah float/int
        angka_float = float(angka)
        return f"{angka_float:,.0f}".replace(",", ".")
    except Exception as e:
        print(f"Error format_rupiah: {e}")
        return "0"

def format_angka(x):
    """Format angka menjadi string dengan pemisah ribuan - VERSI DIPERBAIKI"""
    try:
        if pd.isna(x) or x == 0:
            return "0"
        # Pastikan x adalah numerik
        if isinstance(x, str):
            # Jika string, coba konversi ke float
            x_clean = safe_float_convert(x)
        else:
            x_clean = float(x)
        
        return f"Rp {x_clean:,.0f}".replace(",", ".")
    except Exception as e:
        print(f"Error format_angka: {e}, value: {x}, type: {type(x)}")
        return "0"
    


def tambah_transaksi_double_entry(tanggal, keterangan, entries):
    """
    Tambah transaksi dengan multiple debit dan kredit
    Format entries: [{"akun": "Kas", "debit": 100000, "kredit": 0}, ...]
    SEMUA ENTRI DALAM SATU TRANSAKSI MEMPUNYAI NOMOR YANG SAMA
    """
    try:
        if "df_jurnal_umum" not in st.session_state:
            st.session_state.df_jurnal_umum = pd.DataFrame(
                columns=["No", "Tanggal", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"]
            )
        
        # Validasi keseimbangan
        total_debit = sum(entry["debit"] for entry in entries)
        total_kredit = sum(entry["kredit"] for entry in entries)
        
        if abs(total_debit - total_kredit) > 1:
            return False, f"Transaksi tidak seimbang! Debit: {total_debit:,} vs Kredit: {total_kredit:,}"
        
        # GUNAKAN SATU NOMOR UNTUK SEMUA ENTRI DALAM TRANSAKSI INI
        nomor_transaksi = st.session_state.transaction_counter
        
        # Tambahkan setiap entry dengan NOMOR YANG SAMA
        for entry in entries:
            row = {
                "No": nomor_transaksi,  # NOMOR SAMA untuk semua entri
                "Tanggal": tanggal,
                "Akun Debit": entry["akun"] if entry["debit"] > 0 else "",
                "Debit (Rp)": entry["debit"],
                "Akun Kredit": entry["akun"] if entry["kredit"] > 0 else "",
                "Kredit (Rp)": entry["kredit"]
            }
            
            st.session_state.df_jurnal_umum = pd.concat([
                st.session_state.df_jurnal_umum,
                pd.DataFrame([row])
            ], ignore_index=True)
        
        # Hanya increment transaction counter SEKALI untuk satu transaksi
        st.session_state.transaction_counter += 1
        
        # Update sistem
        update_sistem_dengan_struktur_baru()
        auto_save()
        
        return True, f"Transaksi double entry berhasil ditambahkan! (No: {nomor_transaksi})"
        
    except Exception as e:
        return False, f"Error: {str(e)}"
    
    
def create_number_input_with_format(label, value, key):
    """Membuat input number dengan format rupiah yang user-friendly"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Input text untuk format ribuan
        formatted_value = format_rupiah(value) if value > 0 else ""
        input_str = st.text_input(
            label,
            value=formatted_value,
            placeholder="0",
            key=f"text_{key}"
        )
    
    with col2:
        # Input number untuk backup (hidden)
        number_val = st.number_input(
            label,
            min_value=0.0,
            value=float(value),
            step=1000.0,
            key=f"num_{key}",
            label_visibility="collapsed"
        )
    
    # Prioritaskan input text jika ada isinya
    if input_str and input_str != "0":
        return parse_rupiah(input_str)
    else:
        return number_val
    
    
def reset_dan_renumber_jurnal_umum():
    """Reset dan beri nomor ulang semua transaksi jurnal umum"""
    try:
        if "df_jurnal_umum" in st.session_state and not st.session_state.df_jurnal_umum.empty:
            df = st.session_state.df_jurnal_umum.copy()
            
            # Dapatkan nomor transaksi unik
            unique_nos = df["No"].unique()
            unique_nos.sort()
            
            # Buat mapping dari nomor lama ke nomor baru
            mapping = {old_no: new_no for new_no, old_no in enumerate(unique_nos, 1)}
            
            # Terapkan mapping
            df["No"] = df["No"].map(mapping)
            
            st.session_state.df_jurnal_umum = df
            
            # Update transaction counter
            st.session_state.transaction_counter = len(unique_nos) + 1
            
            # Update sistem
            update_sistem_dengan_struktur_baru()
            auto_save()
            
            return True
        return False
    except Exception as e:
        st.error(f"Error reset numbering: {str(e)}")
        return False
    
    
def export_to_excel():
    """Export semua data ke Excel dengan error handling yang lebih baik"""
    try:
        buffer = BytesIO()

        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Export standar
            export_list = {
                "df_jurnal_umum": "Jurnal Umum",
                "df_jurnal_penyesuaian": "Jurnal Penyesuaian",
                "df_neraca_saldo_periode_sebelumnya": "Neraca Saldo Periode Sebelumnya",
                "df_buku_besar": "Buku Besar",
                "df_neraca_saldo": "Neraca Saldo",
                "df_laporan_laba_rugi": "Laporan Laba Rugi",
                "df_laporan_perubahan_modal": "Laporan Perubahan Modal",
                "df_laporan_posisi_keuangan": "Laporan Posisi Keuangan",
                "df_jurnal_penutup": "Jurnal Penutup",
                "df_neraca_saldo_setelah_penutup": "Neraca Saldo Setelah Penutup",
                # DATA BARU
                "df_penjualan": "Penjualan",
                "df_pembelian": "Pembelian",
                "df_persediaan": "Persediaan",
                "df_riwayat_persediaan": "Riwayat Persediaan"
            }

            # Counter untuk mengecek apakah ada data yang diexport
            data_exported = False

            for key, sheet_name in export_list.items():
                if key in st.session_state and not st.session_state[key].empty:
                    df_to_export = st.session_state[key].copy()
                    if 'Tanggal' in df_to_export.columns:
                        df_to_export['Tanggal'] = df_to_export['Tanggal'].astype(str)
                    df_to_export.to_excel(writer, sheet_name=sheet_name, index=False)
                    data_exported = True
                    print(f"✅ Exported {len(df_to_export)} rows to {sheet_name}")

            # Tambahkan sheet ringkasan
            summary_data = {
                "Jenis Laporan": ["Jurnal Umum", "Jurnal Penyesuaian", "Buku Besar", "Neraca Saldo", "Penjualan", "Pembelian", "Persediaan"],
                "Jumlah Transaksi": [
                    len(st.session_state.get("df_jurnal_umum", pd.DataFrame())),
                    len(st.session_state.get("df_jurnal_penyesuaian", pd.DataFrame())),
                    len(st.session_state.get("df_buku_besar", pd.DataFrame())),
                    len(st.session_state.get("df_neraca_saldo", pd.DataFrame())),
                    len(st.session_state.get("df_penjualan", pd.DataFrame())),
                    len(st.session_state.get("df_pembelian", pd.DataFrame())),
                    len(st.session_state.get("df_persediaan", pd.DataFrame()))
                ],
                "Tanggal Backup": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * 7
            }
            
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="Ringkasan_Backup", index=False)
            data_exported = True

            # Jika tidak ada data sama sekali, buat sheet kosong
            if not data_exported:
                pd.DataFrame({"Pesan": ["Tidak ada data untuk diexport"]}).to_excel(
                    writer, sheet_name="Info", index=False
                )

        buffer.seek(0)
        
        # Validasi buffer tidak kosong
        if buffer.getbuffer().nbytes == 0:
            raise ValueError("Buffer export kosong")
            
        return buffer

    except Exception as e:
        print(f"❌ Error dalam export_to_excel: {str(e)}")
        
        # Buat buffer error sebagai fallback
        buffer_fallback = BytesIO()
        try:
            with pd.ExcelWriter(buffer_fallback, engine='xlsxwriter') as writer:
                error_data = {
                    "Error": [f"Terjadi error saat export: {str(e)}"],
                    "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                }
                pd.DataFrame(error_data).to_excel(writer, sheet_name="Error", index=False)
            buffer_fallback.seek(0)
            return buffer_fallback
        except:
            # Fallback ekstrem: return buffer dengan data minimal
            buffer_minimal = BytesIO()
            buffer_minimal.write(b"Error during export")
            buffer_minimal.seek(0)
            return buffer_minimal

def update_buku_besar():
    """
    Fungsi update buku besar yang kompatibel dengan struktur data baru
    dengan validasi keseimbangan debit-kredit - VERSI DIPERBAIKI
    """
    try:
        # Reset debug messages
        st.session_state.debug_error = None
        st.session_state.debug_jurnal_used = None
        st.session_state.debug_saldo_awal_used = None
        
        # Gunakan data jurnal format lama jika tersedia
        if "df_jurnal_umum_old_format" in st.session_state and not st.session_state.df_jurnal_umum_old_format.empty:
            df_jurnal = st.session_state.df_jurnal_umum_old_format.copy()
            st.session_state.debug_jurnal_used = f"Menggunakan {len(df_jurnal)} transaksi dari jurnal"
        else:
            # Jika tidak ada data jurnal, buat DataFrame kosong
            df_jurnal = pd.DataFrame(columns=["Nama Akun", "Debit (Rp)", "Kredit (Rp)"])
            st.session_state.debug_jurnal_used = "Tidak ada data jurnal"
        
        # Gunakan saldo awal jika tersedia
        if "df_neraca_saldo_periode_sebelumnya" in st.session_state and not st.session_state.df_neraca_saldo_periode_sebelumnya.empty:
            df_saldo_awal = st.session_state.df_neraca_saldo_periode_sebelumnya[["Nama Akun", "Debit (Rp)", "Kredit (Rp)"]].copy()
            st.session_state.debug_saldo_awal_used = f"Menggunakan {len(df_saldo_awal)} akun dari saldo awal"
        else:
            df_saldo_awal = pd.DataFrame(columns=["Nama Akun", "Debit (Rp)", "Kredit (Rp)"])
            st.session_state.debug_saldo_awal_used = "Tidak ada saldo awal"
        
        # Gabungkan data saldo awal dan transaksi
        if not df_jurnal.empty or not df_saldo_awal.empty:
            all_data = pd.concat([df_saldo_awal, df_jurnal], ignore_index=True)
            
            # Group by akun dan hitung total debit/kredit per akun
            buku_besar = all_data.groupby("Nama Akun").agg({
                "Debit (Rp)": "sum",
                "Kredit (Rp)": "sum"
            }).reset_index()
            
            # Hitung saldo (Debit - Kredit)
            buku_besar["Saldo (Rp)"] = buku_besar["Debit (Rp)"] - buku_besar["Kredit (Rp)"]
            
            # Urutkan berdasarkan nama akun
            buku_besar = buku_besar.sort_values("Nama Akun").reset_index(drop=True)
            
            # Tambahkan nomor urut
            buku_besar.insert(0, "No", range(1, len(buku_besar) + 1))
            
            st.session_state.df_buku_besar = buku_besar
            st.session_state.debug_buku_besar = f"Berhasil membuat buku besar dengan {len(buku_besar)} akun"
            
            # BUAT NERACA SALDO DARI BUKU BESAR
            neraca_saldo = buku_besar.copy()
            # Hapus kolom saldo untuk neraca saldo
            neraca_saldo = neraca_saldo[["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"]]
            
            # Tambahkan baris total
            total_debit = neraca_saldo["Debit (Rp)"].sum()
            total_kredit = neraca_saldo["Kredit (Rp)"].sum()
            total_row = {
                "No": "",
                "Nama Akun": "TOTAL",
                "Debit (Rp)": total_debit,
                "Kredit (Rp)": total_kredit
            }
            
            neraca_final = pd.concat([neraca_saldo, pd.DataFrame([total_row])], ignore_index=True)
            st.session_state.df_neraca_saldo = neraca_final
            st.session_state.debug_neraca_saldo = f"Neraca saldo dibuat - Debit: {total_debit}, Kredit: {total_kredit}"
            
            auto_save()
        else:
            # Jika tidak ada data sama sekali
            st.session_state.df_buku_besar = pd.DataFrame(columns=["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"])
            st.session_state.df_neraca_saldo = pd.DataFrame(columns=["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"])
            st.session_state.debug_error = "Tidak ada data untuk membuat buku besar"
            
    except Exception as e:
        error_msg = f"Error dalam update_buku_besar: {str(e)}"
        st.session_state.debug_error = error_msg
        st.session_state.df_buku_besar = pd.DataFrame(columns=["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"])
        st.session_state.df_neraca_saldo = pd.DataFrame(columns=["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"])
        

        
        
        
        
def update_buku_besar_per_akun():
    """
    Update buku besar yang dikelompokkan per akun - VERSI DIPERBAIKI
    """
    try:
        # Kumpulkan semua transaksi dari berbagai sumber
        semua_transaksi = []
        
        # 1. Transaksi dari Jurnal Umum - DIPERBAIKI
        
        if "df_neraca_saldo_periode_sebelumnya" in st.session_state and not st.session_state.df_neraca_saldo_periode_sebelumnya.empty:
            for _, row in st.session_state.df_neraca_saldo_periode_sebelumnya.iterrows():
                nama_akun = row["Nama Akun"]
                saldo_debit = safe_float_convert(row["Debit (Rp)"])
                saldo_kredit = safe_float_convert(row["Kredit (Rp)"])
                
                # Hitung saldo awal (Debit - Kredit)
                saldo_awal = saldo_debit - saldo_kredit
                
                if saldo_awal != 0:
                    # Tambahkan sebagai transaksi saldo awal
                    if saldo_awal > 0:
                        semua_transaksi.append({
                            "Tanggal": st.session_state.tanggal_awal_periode,
                            "Sumber": "Saldo Awal",
                            "Keterangan": f"Saldo Awal Periode {st.session_state.periode_sekarang}",
                            "Nama Akun": nama_akun,
                            "Debit (Rp)": saldo_awal,
                            "Kredit (Rp)": 0.0,
                            "No_Transaksi": 0
                        })
                    else:
                        semua_transaksi.append({
                            "Tanggal": st.session_state.tanggal_awal_periode,
                            "Sumber": "Saldo Awal", 
                            "Keterangan": f"Saldo Awal Periode {st.session_state.periode_sekarang}",
                            "Nama Akun": nama_akun,
                            "Debit (Rp)": 0.0,
                            "Kredit (Rp)": abs(saldo_awal),
                            "No_Transaksi": 0
                        })
        if "df_jurnal_umum" in st.session_state and not st.session_state.df_jurnal_umum.empty:
            for _, row in st.session_state.df_jurnal_umum.iterrows():
                # Pastikan tipe data numerik dengan safe_float_convert
                debit_val = safe_float_convert(row["Debit (Rp)"])
                kredit_val = safe_float_convert(row["Kredit (Rp)"])
                
                # Entri Debit dari Jurnal Umum
                if debit_val > 0:
                    semua_transaksi.append({
                        "Tanggal": row["Tanggal"],
                        "Sumber": "Jurnal Umum",
                        "Keterangan": f"Transaksi No {row['No']}",
                        "Nama Akun": str(row["Akun Debit"]),
                        "Debit (Rp)": debit_val,
                        "Kredit (Rp)": 0.0,
                        "No_Transaksi": safe_float_convert(row["No"], 0)
                    })
                
                # Entri Kredit dari Jurnal Umum
                if kredit_val > 0:
                    semua_transaksi.append({
                        "Tanggal": row["Tanggal"],
                        "Sumber": "Jurnal Umum", 
                        "Keterangan": f"Transaksi No {row['No']}",
                        "Nama Akun": str(row["Akun Kredit"]),
                        "Debit (Rp)": 0.0,
                        "Kredit (Rp)": kredit_val,
                        "No_Transaksi": safe_float_convert(row["No"], 0)
                    })
        
        # 2. Transaksi dari Jurnal Penyesuaian - DIPERBAIKI
        if "df_jurnal_penyesuaian" in st.session_state and not st.session_state.df_jurnal_penyesuaian.empty:
            for _, row in st.session_state.df_jurnal_penyesuaian.iterrows():
                debit_val = safe_float_convert(row["Debit (Rp)"])
                kredit_val = safe_float_convert(row["Kredit (Rp)"])
                
                # Entri Debit dari Penyesuaian
                if debit_val > 0:
                    semua_transaksi.append({
                        "Tanggal": row["Tanggal"],
                        "Sumber": "Jurnal Penyesuaian",
                        "Keterangan": str(row["Keterangan"]),
                        "Nama Akun": str(row["Akun Debit"]),
                        "Debit (Rp)": debit_val,
                        "Kredit (Rp)": 0.0,
                        "No_Transaksi": safe_float_convert(row["No"], 0)
                    })
                
                # Entri Kredit dari Penyesuaian
                if kredit_val > 0:
                    semua_transaksi.append({
                        "Tanggal": row["Tanggal"],
                        "Sumber": "Jurnal Penyesuaian",
                        "Keterangan": str(row["Keterangan"]),
                        "Nama Akun": str(row["Akun Kredit"]),
                        "Debit (Rp)": 0.0,
                        "Kredit (Rp)": kredit_val,
                        "No_Transaksi": safe_float_convert(row["No"], 0)
                    })
        
        # 3. Transaksi dari Jurnal Penutup - DIPERBAIKI
        if "df_jurnal_penutup" in st.session_state and not st.session_state.df_jurnal_penutup.empty:
            for _, row in st.session_state.df_jurnal_penutup.iterrows():
                debit_val = safe_float_convert(row["Debit (Rp)"])
                kredit_val = safe_float_convert(row["Kredit (Rp)"])
                
                # Entri Debit dari Penutup
                if debit_val > 0:
                    semua_transaksi.append({
                        "Tanggal": row["Tanggal"],
                        "Sumber": "Jurnal Penutup",
                        "Keterangan": str(row["Keterangan"]),
                        "Nama Akun": str(row["Akun Debit"]),
                        "Debit (Rp)": debit_val,
                        "Kredit (Rp)": 0.0,
                        "No_Transaksi": safe_float_convert(row["No"], 0)
                    })
                
                # Entri Kredit dari Penutup
                if kredit_val > 0:
                    semua_transaksi.append({
                        "Tanggal": row["Tanggal"],
                        "Sumber": "Jurnal Penutup",
                        "Keterangan": str(row["Keterangan"]),
                        "Nama Akun": str(row["Akun Kredit"]),
                        "Debit (Rp)": 0.0,
                        "Kredit (Rp)": kredit_val,
                        "No_Transaksi": safe_float_convert(row["No"], 0)
                    })
                    
                update_neraca_saldo_dari_buku_besar_per_akun(st.session_state.buku_besar_per_akun)
        if not st.session_state.tanggal_awal_periode:
            st.warning("Silakan atur periode akuntansi terlebih dahulu di menu 'Neraca Saldo Periode Sebelumnya'.")
            return 

        # Jika tidak ada transaksi, buat buku besar kosong
        if not semua_transaksi:
            st.session_state.df_buku_besar = pd.DataFrame(columns=[
                "No", "Tanggal", "Sumber", "Keterangan", "Nama Akun", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"
            ])
            st.session_state.buku_besar_per_akun = {}
            return
        
        # Konversi ke DataFrame dengan validasi
        df_semua_transaksi = pd.DataFrame(semua_transaksi)
        
        # PERBAIKAN: Validasi dan cleaning data sebelum processing
        if not df_semua_transaksi.empty:
            # Pastikan kolom tanggal dalam format yang benar
            df_semua_transaksi['Tanggal'] = pd.to_datetime(df_semua_transaksi['Tanggal'], errors='coerce').dt.date
            
            # Pastikan tipe data numerik konsisten
            df_semua_transaksi['Debit (Rp)'] = df_semua_transaksi['Debit (Rp)'].apply(safe_float_convert)
            df_semua_transaksi['Kredit (Rp)'] = df_semua_transaksi['Kredit (Rp)'].apply(safe_float_convert)
            df_semua_transaksi['No_Transaksi'] = df_semua_transaksi['No_Transaksi'].apply(lambda x: int(safe_float_convert(x, 0)))
            
            # Hapus baris dengan Nama Akun yang tidak valid
            df_semua_transaksi = df_semua_transaksi[df_semua_transaksi['Nama Akun'].notna()]
            df_semua_transaksi = df_semua_transaksi[df_semua_transaksi['Nama Akun'] != '']
            
            # Urutkan berdasarkan tanggal dan nama akun
            df_semua_transaksi = df_semua_transaksi.sort_values(["Nama Akun", "Tanggal"]).reset_index(drop=True)
        
        # Buat struktur buku besar per akun
        buku_besar_per_akun = {}
        
        # Kelompokkan transaksi per akun
        for akun in df_semua_transaksi["Nama Akun"].unique():
            transaksi_akun = df_semua_transaksi[df_semua_transaksi["Nama Akun"] == akun].copy()
            transaksi_akun = transaksi_akun.sort_values("Tanggal").reset_index(drop=True)
            
            # Hitung saldo running untuk akun ini
            saldo_running = 0.0
            detail_akun = []
            
            for idx, transaksi in transaksi_akun.iterrows():
                debit = safe_float_convert(transaksi["Debit (Rp)"])
                kredit = safe_float_convert(transaksi["Kredit (Rp)"])
                saldo_running += debit - kredit
                
                detail_akun.append({
                    "No": idx + 1,
                    "Tanggal": transaksi["Tanggal"],
                    "Sumber": transaksi["Sumber"],
                    "Keterangan": transaksi["Keterangan"],
                    "No_Transaksi": int(transaksi["No_Transaksi"]),
                    "Debit (Rp)": debit,
                    "Kredit (Rp)": kredit,
                    "Saldo (Rp)": saldo_running
                })
            
            # Simpan detail akun
            if detail_akun:  # Hanya simpan jika ada transaksi
                buku_besar_per_akun[akun] = pd.DataFrame(detail_akun)
        
        # Simpan ke session state
        st.session_state.buku_besar_per_akun = buku_besar_per_akun
        
        # Juga simpan dalam format flat untuk kompatibilitas
        semua_detail = []
        for akun, df_akun in buku_besar_per_akun.items():
            for _, row in df_akun.iterrows():
                semua_detail.append({
                    "No": int(row["No"]),
                    "Tanggal": row["Tanggal"],
                    "Sumber": row["Sumber"],
                    "Keterangan": row["Keterangan"],
                    "Nama Akun": akun,
                    "Debit (Rp)": safe_float_convert(row["Debit (Rp)"]),
                    "Kredit (Rp)": safe_float_convert(row["Kredit (Rp)"]),
                    "Saldo (Rp)": safe_float_convert(row["Saldo (Rp)"])
                })
        
        if semua_detail:
            st.session_state.df_buku_besar = pd.DataFrame(semua_detail)
        else:
            st.session_state.df_buku_besar = pd.DataFrame(columns=[
                "No", "Tanggal", "Sumber", "Keterangan", "Nama Akun", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"
            ])
        
        # Update neraca saldo
        update_neraca_saldo_dari_buku_besar_per_akun(buku_besar_per_akun)
        
        print(f"✅ Buku besar per akun diperbarui: {len(buku_besar_per_akun)} akun")
        
    except Exception as e:
        st.error(f"Error dalam update_buku_besar_per_akun: {str(e)}")
        import traceback
        st.error(f"Detail error: {traceback.format_exc()}")
        # Fallback: buat buku besar kosong
        st.session_state.df_buku_besar = pd.DataFrame(columns=[
            "No", "Tanggal", "Sumber", "Keterangan", "Nama Akun", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"
        ])
        st.session_state.buku_besar_per_akun = {}

def update_buku_besar_per_akun_fixed():
    """
    Update buku besar yang dikelompokkan per akun - VERSI DIPERBAIKI DENGAN ERROR HANDLING
    """
    try:
        # PERBAIKAN: Pastikan tanggal_awal_periode sudah diinisialisasi
        if "tanggal_awal_periode" not in st.session_state:
            from datetime import date
            st.session_state.tanggal_awal_periode = date.today().replace(day=1)
            st.warning("⚠️ Tanggal awal periode diatur otomatis ke awal bulan ini. Silakan atur di menu 'Neraca Saldo Periode Sebelumnya' jika perlu disesuaikan.")
            print("⚠️ tanggal_awal_periode diatur otomatis")
        
        # PERBAIKAN: Pastikan periode_sekarang sudah diinisialisasi
        if "periode_sekarang" not in st.session_state:
            from datetime import datetime
            st.session_state.periode_sekarang = datetime.now().strftime("%B %Y")
            print("⚠️ periode_sekarang diatur otomatis")
        
        # Kumpulkan semua transaksi dari berbagai sumber
        semua_transaksi = []
        
        # ========== 1. TAMBAHKAN SALDO AWAL DARI NERACA SALDO PERIODE SEBELUMNYA ==========
        if "df_neraca_saldo_periode_sebelumnya" in st.session_state and not st.session_state.df_neraca_saldo_periode_sebelumnya.empty:
            for _, row in st.session_state.df_neraca_saldo_periode_sebelumnya.iterrows():
                nama_akun = row["Nama Akun"]
                saldo_debit = safe_float_convert(row["Debit (Rp)"])
                saldo_kredit = safe_float_convert(row["Kredit (Rp)"])
                
                # Hitung saldo awal (Debit - Kredit)
                saldo_awal = saldo_debit - saldo_kredit
                
                if saldo_awal != 0:
                    # Tambahkan sebagai transaksi saldo awal
                    if saldo_awal > 0:
                        semua_transaksi.append({
                            "Tanggal": st.session_state.tanggal_awal_periode,
                            "Sumber": "Saldo Awal",
                            "Keterangan": f"Saldo Awal Periode {st.session_state.periode_sekarang}",
                            "Nama Akun": nama_akun,
                            "Debit (Rp)": saldo_awal,
                            "Kredit (Rp)": 0.0,
                            "No_Transaksi": 0  # Nomor khusus untuk saldo awal
                        })
                    else:
                        semua_transaksi.append({
                            "Tanggal": st.session_state.tanggal_awal_periode,
                            "Sumber": "Saldo Awal", 
                            "Keterangan": f"Saldo Awal Periode {st.session_state.periode_sekarang}",
                            "Nama Akun": nama_akun,
                            "Debit (Rp)": 0.0,
                            "Kredit (Rp)": abs(saldo_awal),
                            "No_Transaksi": 0
                        })
                    print(f"✅ Menambahkan saldo awal untuk {nama_akun}: {saldo_awal:,.0f}")

        # ========== 2. TRANSAKSI DARI JURNAL UMUM ==========
        if "df_jurnal_umum" in st.session_state and not st.session_state.df_jurnal_umum.empty:
            for _, row in st.session_state.df_jurnal_umum.iterrows():
                # Pastikan tipe data numerik dengan safe_float_convert
                debit_val = safe_float_convert(row["Debit (Rp)"])
                kredit_val = safe_float_convert(row["Kredit (Rp)"])
                
                # Entri Debit dari Jurnal Umum
                if debit_val > 0:
                    semua_transaksi.append({
                        "Tanggal": row["Tanggal"],
                        "Sumber": "Jurnal Umum",
                        "Keterangan": f"Transaksi No {row['No']}",
                        "Nama Akun": str(row["Akun Debit"]),
                        "Debit (Rp)": debit_val,
                        "Kredit (Rp)": 0.0,
                        "No_Transaksi": safe_float_convert(row["No"], 0)
                    })
                
                # Entri Kredit dari Jurnal Umum
                if kredit_val > 0:
                    semua_transaksi.append({
                        "Tanggal": row["Tanggal"],
                        "Sumber": "Jurnal Umum", 
                        "Keterangan": f"Transaksi No {row['No']}",
                        "Nama Akun": str(row["Akun Kredit"]),
                        "Debit (Rp)": 0.0,
                        "Kredit (Rp)": kredit_val,
                        "No_Transaksi": safe_float_convert(row["No"], 0)
                    })

        # ========== 3. TRANSAKSI DARI JURNAL PENYESUAIAN ==========
        if "df_jurnal_penyesuaian" in st.session_state and not st.session_state.df_jurnal_penyesuaian.empty:
            for _, row in st.session_state.df_jurnal_penyesuaian.iterrows():
                debit_val = safe_float_convert(row["Debit (Rp)"])
                kredit_val = safe_float_convert(row["Kredit (Rp)"])
                
                # Entri Debit dari Penyesuaian
                if debit_val > 0:
                    semua_transaksi.append({
                        "Tanggal": row["Tanggal"],
                        "Sumber": "Jurnal Penyesuaian",
                        "Keterangan": str(row["Keterangan"]),
                        "Nama Akun": str(row["Akun Debit"]),
                        "Debit (Rp)": debit_val,
                        "Kredit (Rp)": 0.0,
                        "No_Transaksi": safe_float_convert(row["No"], 0)
                    })
                
                # Entri Kredit dari Penyesuaian
                if kredit_val > 0:
                    semua_transaksi.append({
                        "Tanggal": row["Tanggal"],
                        "Sumber": "Jurnal Penyesuaian",
                        "Keterangan": str(row["Keterangan"]),
                        "Nama Akun": str(row["Akun Kredit"]),
                        "Debit (Rp)": 0.0,
                        "Kredit (Rp)": kredit_val,
                        "No_Transaksi": safe_float_convert(row["No"], 0)
                    })

        # ========== 4. TRANSAKSI DARI JURNAL PENUTUP ==========
        if "df_jurnal_penutup" in st.session_state and not st.session_state.df_jurnal_penutup.empty:
            for _, row in st.session_state.df_jurnal_penutup.iterrows():
                debit_val = safe_float_convert(row["Debit (Rp)"])
                kredit_val = safe_float_convert(row["Kredit (Rp)"])
                
                # Entri Debit dari Penutup
                if debit_val > 0:
                    semua_transaksi.append({
                        "Tanggal": row["Tanggal"],
                        "Sumber": "Jurnal Penutup",
                        "Keterangan": str(row["Keterangan"]),
                        "Nama Akun": str(row["Akun Debit"]),
                        "Debit (Rp)": debit_val,
                        "Kredit (Rp)": 0.0,
                        "No_Transaksi": safe_float_convert(row["No"], 0)
                    })
                
                # Entri Kredit dari Penutup
                if kredit_val > 0:
                    semua_transaksi.append({
                        "Tanggal": row["Tanggal"],
                        "Sumber": "Jurnal Penutup",
                        "Keterangan": str(row["Keterangan"]),
                        "Nama Akun": str(row["Akun Kredit"]),
                        "Debit (Rp)": 0.0,
                        "Kredit (Rp)": kredit_val,
                        "No_Transaksi": safe_float_convert(row["No"], 0)
                    })

        # ========== 5. PROSES BUKU BESAR PER AKUN ==========
        if not semua_transaksi:
            st.session_state.df_buku_besar = pd.DataFrame(columns=[
                "No", "Tanggal", "Sumber", "Keterangan", "Nama Akun", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"
            ])
            st.session_state.buku_besar_per_akun = {}
            st.info("📊 Buku Besar masih kosong. Silakan tambah transaksi di Jurnal Umum terlebih dahulu.")
            return

        # Konversi ke DataFrame dengan validasi
        df_semua_transaksi = pd.DataFrame(semua_transaksi)
        
        # PERBAIKAN: Validasi dan cleaning data sebelum processing
        if not df_semua_transaksi.empty:
            # Pastikan kolom tanggal dalam format yang benar
            df_semua_transaksi['Tanggal'] = pd.to_datetime(df_semua_transaksi['Tanggal'], errors='coerce').dt.date
            
            # Pastikan tipe data numerik konsisten
            df_semua_transaksi['Debit (Rp)'] = df_semua_transaksi['Debit (Rp)'].apply(safe_float_convert)
            df_semua_transaksi['Kredit (Rp)'] = df_semua_transaksi['Kredit (Rp)'].apply(safe_float_convert)
            df_semua_transaksi['No_Transaksi'] = df_semua_transaksi['No_Transaksi'].apply(lambda x: int(safe_float_convert(x, 0)))
            
            # Hapus baris dengan Nama Akun yang tidak valid
            df_semua_transaksi = df_semua_transaksi[df_semua_transaksi['Nama Akun'].notna()]
            df_semua_transaksi = df_semua_transaksi[df_semua_transaksi['Nama Akun'] != '']
            
            # Urutkan berdasarkan tanggal dan nama akun
            df_semua_transaksi = df_semua_transaksi.sort_values(["Nama Akun", "Tanggal", "No_Transaksi"]).reset_index(drop=True)

        # Buat struktur buku besar per akun
        buku_besar_per_akun = {}
        
        # Kelompokkan transaksi per akun
        for akun in df_semua_transaksi["Nama Akun"].unique():
            transaksi_akun = df_semua_transaksi[df_semua_transaksi["Nama Akun"] == akun].copy()
            transaksi_akun = transaksi_akun.sort_values(["Tanggal", "No_Transaksi"]).reset_index(drop=True)
            
            # Hitung saldo running untuk akun ini
            saldo_running = 0.0
            detail_akun = []
            
            for idx, transaksi in transaksi_akun.iterrows():
                debit = safe_float_convert(transaksi["Debit (Rp)"])
                kredit = safe_float_convert(transaksi["Kredit (Rp)"])
                saldo_running += debit - kredit
                
                detail_akun.append({
                    "No": idx + 1,
                    "Tanggal": transaksi["Tanggal"],
                    "Sumber": transaksi["Sumber"],
                    "Keterangan": transaksi["Keterangan"],
                    "No_Transaksi": int(transaksi["No_Transaksi"]),
                    "Debit (Rp)": debit,
                    "Kredit (Rp)": kredit,
                    "Saldo (Rp)": saldo_running
                })
            
            # Simpan detail akun
            if detail_akun:  # Hanya simpan jika ada transaksi
                buku_besar_per_akun[akun] = pd.DataFrame(detail_akun)

        # Simpan ke session state
        st.session_state.buku_besar_per_akun = buku_besar_per_akun
        
        # Juga simpan dalam format flat untuk kompatibilitas
        semua_detail = []
        for akun, df_akun in buku_besar_per_akun.items():
            for _, row in df_akun.iterrows():
                semua_detail.append({
                    "No": int(row["No"]),
                    "Tanggal": row["Tanggal"],
                    "Sumber": row["Sumber"],
                    "Keterangan": row["Keterangan"],
                    "Nama Akun": akun,
                    "Debit (Rp)": safe_float_convert(row["Debit (Rp)"]),
                    "Kredit (Rp)": safe_float_convert(row["Kredit (Rp)"]),
                    "Saldo (Rp)": safe_float_convert(row["Saldo (Rp)"])
                })
        
        if semua_detail:
            st.session_state.df_buku_besar = pd.DataFrame(semua_detail)
        else:
            st.session_state.df_buku_besar = pd.DataFrame(columns=[
                "No", "Tanggal", "Sumber", "Keterangan", "Nama Akun", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"
            ])
        
        # Update neraca saldo
        update_neraca_saldo_dari_buku_besar_per_akun(buku_besar_per_akun)
        
        print(f"✅ Buku besar per akun diperbarui: {len(buku_besar_per_akun)} akun")
        return True
        
    except Exception as e:
        st.error(f"❌ Error dalam update_buku_besar_per_akun_fixed: {str(e)}")
        import traceback
        st.error(f"Detail error: {traceback.format_exc()}")
        # Fallback: buat buku besar kosong
        st.session_state.df_buku_besar = pd.DataFrame(columns=[
            "No", "Tanggal", "Sumber", "Keterangan", "Nama Akun", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"
        ])
        st.session_state.buku_besar_per_akun = {}
        return False
    
def update_neraca_saldo_dari_buku_besar_per_akun(buku_besar_per_akun):
    """Update neraca saldo dari data buku besar per akun - VERSI DIPERBAIKI"""
    try:
        neraca_data = []
        
        for akun, df_akun in buku_besar_per_akun.items():
            if not df_akun.empty:
                # Pastikan tipe data numerik dengan safe_float_convert
                total_debit = sum(df_akun["Debit (Rp)"].apply(safe_float_convert))
                total_kredit = sum(df_akun["Kredit (Rp)"].apply(safe_float_convert))
                saldo_akhir = safe_float_convert(df_akun["Saldo (Rp)"].iloc[-1]) if len(df_akun) > 0 else 0.0
                
                neraca_data.append({
                    "Nama Akun": akun,
                    "Debit (Rp)": total_debit,
                    "Kredit (Rp)": total_kredit,
                    "Saldo (Rp)": saldo_akhir
                })
        
        if neraca_data:
            neraca_saldo = pd.DataFrame(neraca_data)
            # PERBAIKAN: Sorting dengan handle error
            try:
                neraca_saldo = neraca_saldo.sort_values("Nama Akun").reset_index(drop=True)
            except:
                # Fallback sorting jika ada error
                neraca_saldo = neraca_saldo.reset_index(drop=True)
            
            neraca_saldo.insert(0, "No", range(1, len(neraca_saldo) + 1))
            
            # Tambahkan baris total dengan safe_float_convert
            total_debit = sum(neraca_saldo["Debit (Rp)"].apply(safe_float_convert))
            total_kredit = sum(neraca_saldo["Kredit (Rp)"].apply(safe_float_convert))
            total_row = {
                "No": "",
                "Nama Akun": "TOTAL",
                "Debit (Rp)": total_debit,
                "Kredit (Rp)": total_kredit,
                "Saldo (Rp)": ""
            }
            
            neraca_final = pd.concat([neraca_saldo, pd.DataFrame([total_row])], ignore_index=True)
            st.session_state.df_neraca_saldo = neraca_final
            print(f"✅ Neraca saldo diperbarui: {len(neraca_data)} akun")
            
    except Exception as e:
        st.error(f"❌ Error update neraca saldo: {str(e)}")
        # Fallback: buat neraca saldo kosong
        st.session_state.df_neraca_saldo = pd.DataFrame(columns=["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"])
    
def update_setelah_penyesuaian():
    """
    Fungsi untuk update sistem setelah jurnal penyesuaian - VERSI DIPERBAIKI
    """
    try:
        # Pastikan session state untuk semua transaksi ada
        if "df_semua_transaksi" not in st.session_state:
            st.session_state.df_semua_transaksi = pd.DataFrame(columns=["Tanggal", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"])
        
        # Gabungkan jurnal umum dan jurnal penyesuaian
        if "df_jurnal_umum_old_format" in st.session_state and not st.session_state.df_jurnal_umum_old_format.empty:
            df_jurnal_umum = st.session_state.df_jurnal_umum_old_format
        else:
            df_jurnal_umum = pd.DataFrame(columns=["Tanggal", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"])
        
        if "df_jurnal_penyesuaian" in st.session_state and not st.session_state.df_jurnal_penyesuaian.empty:
            # Konversi jurnal penyesuaian ke format lama
            rows_penyesuaian = []
            for _, row in st.session_state.df_jurnal_penyesuaian.iterrows():
                # Entri debit
                if row["Debit (Rp)"] > 0:
                    rows_penyesuaian.append({
                        "Tanggal": row["Tanggal"],
                        "Nama Akun": row["Akun Debit"],
                        "Debit (Rp)": row["Debit (Rp)"],
                        "Kredit (Rp)": 0
                    })
                # Entri kredit
                if row["Kredit (Rp)"] > 0:
                    rows_penyesuaian.append({
                        "Tanggal": row["Tanggal"],
                        "Nama Akun": row["Akun Kredit"],
                        "Debit (Rp)": 0,
                        "Kredit (Rp)": row["Kredit (Rp)"]
                    })
            
            if rows_penyesuaian:
                df_penyesuaian_old_format = pd.DataFrame(rows_penyesuaian)
                # Gabungkan dengan jurnal umum
                semua_transaksi = pd.concat([df_jurnal_umum, df_penyesuaian_old_format], ignore_index=True)
                st.session_state.df_semua_transaksi = semua_transaksi
                
                # Update buku besar dengan data gabungan
                update_buku_besar_dengan_data(semua_transaksi)
                return True
            
            auto_save()
        
        # Jika tidak ada penyesuaian, gunakan data biasa
        st.session_state.df_semua_transaksi = df_jurnal_umum
        update_buku_besar_dengan_data(df_jurnal_umum)
        return True
        
    except Exception as e:
        st.error(f"Error dalam update_setelah_penyesuaian: {str(e)}")
        return False
    
    
    
def update_buku_besar_dengan_data(data_transaksi):
    """
    Fungsi update buku besar dengan data yang diberikan
    """
    try:
        if data_transaksi.empty:
            st.session_state.df_buku_besar = pd.DataFrame(columns=["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"])
            st.session_state.df_neraca_saldo = pd.DataFrame(columns=["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"])
            return
        
        # Group by akun dan hitung total debit/kredit per akun
        buku_besar = data_transaksi.groupby("Nama Akun").agg({
            "Debit (Rp)": "sum",
            "Kredit (Rp)": "sum"
        }).reset_index()
        
        # Hitung saldo (Debit - Kredit)
        buku_besar["Saldo (Rp)"] = buku_besar["Debit (Rp)"] - buku_besar["Kredit (Rp)"]
        
        # Urutkan berdasarkan nama akun
        buku_besar = buku_besar.sort_values("Nama Akun").reset_index(drop=True)
        
        # Tambahkan nomor urut
        buku_besar.insert(0, "No", range(1, len(buku_besar) + 1))
        
        st.session_state.df_buku_besar = buku_besar
        
        # BUAT NERACA SALDO DARI BUKU BESAR
        neraca_saldo = buku_besar.copy()
        neraca_saldo = neraca_saldo[["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"]]
        
        # Tambahkan baris total
        total_debit = neraca_saldo["Debit (Rp)"].sum()
        total_kredit = neraca_saldo["Kredit (Rp)"].sum()
        total_row = {
            "No": "",
            "Nama Akun": "TOTAL",
            "Debit (Rp)": total_debit,
            "Kredit (Rp)": total_kredit
        }
        
        neraca_final = pd.concat([neraca_saldo, pd.DataFrame([total_row])], ignore_index=True)
        st.session_state.df_neraca_saldo = neraca_final
        
        # Simpan ke database
        save_to_database()
        
    except Exception as e:
        st.error(f"Error dalam update_buku_besar_dengan_data: {str(e)}")
        
def update_buku_besar_per_akun_dengan_saldo_awal():
    """Update buku besar dengan saldo awal dari neraca saldo periode sebelumnya - VERSI KOMPREHENSIF"""
    try:
        # Kumpulkan semua transaksi dari berbagai sumber
        semua_transaksi = []
        
        # ========== 1. TAMBAHKAN SALDO AWAL DARI NERACA SALDO PERIODE SEBELUMNYA ==========
        if "df_neraca_saldo_periode_sebelumnya" in st.session_state and not st.session_state.df_neraca_saldo_periode_sebelumnya.empty:
            for _, row in st.session_state.df_neraca_saldo_periode_sebelumnya.iterrows():
                nama_akun = row["Nama Akun"]
                saldo_debit = safe_float_convert(row["Debit (Rp)"])
                saldo_kredit = safe_float_convert(row["Kredit (Rp)"])
                
                # Hitung saldo awal (Debit - Kredit)
                saldo_awal = saldo_debit - saldo_kredit
                
                if saldo_awal != 0:
                    # Tambahkan sebagai transaksi saldo awal
                    if saldo_awal > 0:
                        semua_transaksi.append({
                            "Tanggal": st.session_state.tanggal_awal_periode,
                            "Sumber": "Saldo Awal",
                            "Keterangan": f"Saldo Awal Periode {st.session_state.periode_sekarang}",
                            "Nama Akun": nama_akun,
                            "Debit (Rp)": saldo_awal,
                            "Kredit (Rp)": 0.0,
                            "No_Transaksi": 0  # Nomor khusus untuk saldo awal
                        })
                    else:
                        semua_transaksi.append({
                            "Tanggal": st.session_state.tanggal_awal_periode,
                            "Sumber": "Saldo Awal", 
                            "Keterangan": f"Saldo Awal Periode {st.session_state.periode_sekarang}",
                            "Nama Akun": nama_akun,
                            "Debit (Rp)": 0.0,
                            "Kredit (Rp)": abs(saldo_awal),
                            "No_Transaksi": 0
                        })
                    print(f"✅ Menambahkan saldo awal untuk {nama_akun}: {saldo_awal:,.0f}")

        # ========== 2. TRANSAKSI DARI JURNAL UMUM ==========
        if "df_jurnal_umum" in st.session_state and not st.session_state.df_jurnal_umum.empty:
            for _, row in st.session_state.df_jurnal_umum.iterrows():
                # Pastikan tipe data numerik dengan safe_float_convert
                debit_val = safe_float_convert(row["Debit (Rp)"])
                kredit_val = safe_float_convert(row["Kredit (Rp)"])
                
                # Entri Debit dari Jurnal Umum
                if debit_val > 0:
                    semua_transaksi.append({
                        "Tanggal": row["Tanggal"],
                        "Sumber": "Jurnal Umum",
                        "Keterangan": f"Transaksi No {row['No']}",
                        "Nama Akun": str(row["Akun Debit"]),
                        "Debit (Rp)": debit_val,
                        "Kredit (Rp)": 0.0,
                        "No_Transaksi": safe_float_convert(row["No"], 0)
                    })
                
                # Entri Kredit dari Jurnal Umum
                if kredit_val > 0:
                    semua_transaksi.append({
                        "Tanggal": row["Tanggal"],
                        "Sumber": "Jurnal Umum", 
                        "Keterangan": f"Transaksi No {row['No']}",
                        "Nama Akun": str(row["Akun Kredit"]),
                        "Debit (Rp)": 0.0,
                        "Kredit (Rp)": kredit_val,
                        "No_Transaksi": safe_float_convert(row["No"], 0)
                    })

        # ========== 3. TRANSAKSI DARI JURNAL PENYESUAIAN ==========
        if "df_jurnal_penyesuaian" in st.session_state and not st.session_state.df_jurnal_penyesuaian.empty:
            for _, row in st.session_state.df_jurnal_penyesuaian.iterrows():
                debit_val = safe_float_convert(row["Debit (Rp)"])
                kredit_val = safe_float_convert(row["Kredit (Rp)"])
                
                # Entri Debit dari Penyesuaian
                if debit_val > 0:
                    semua_transaksi.append({
                        "Tanggal": row["Tanggal"],
                        "Sumber": "Jurnal Penyesuaian",
                        "Keterangan": str(row["Keterangan"]),
                        "Nama Akun": str(row["Akun Debit"]),
                        "Debit (Rp)": debit_val,
                        "Kredit (Rp)": 0.0,
                        "No_Transaksi": safe_float_convert(row["No"], 0)
                    })
                
                # Entri Kredit dari Penyesuaian
                if kredit_val > 0:
                    semua_transaksi.append({
                        "Tanggal": row["Tanggal"],
                        "Sumber": "Jurnal Penyesuaian",
                        "Keterangan": str(row["Keterangan"]),
                        "Nama Akun": str(row["Akun Kredit"]),
                        "Debit (Rp)": 0.0,
                        "Kredit (Rp)": kredit_val,
                        "No_Transaksi": safe_float_convert(row["No"], 0)
                    })

        # ========== 4. TRANSAKSI DARI JURNAL PENUTUP ==========
        if "df_jurnal_penutup" in st.session_state and not st.session_state.df_jurnal_penutup.empty:
            for _, row in st.session_state.df_jurnal_penutup.iterrows():
                debit_val = safe_float_convert(row["Debit (Rp)"])
                kredit_val = safe_float_convert(row["Kredit (Rp)"])
                
                # Entri Debit dari Penutup
                if debit_val > 0:
                    semua_transaksi.append({
                        "Tanggal": row["Tanggal"],
                        "Sumber": "Jurnal Penutup",
                        "Keterangan": str(row["Keterangan"]),
                        "Nama Akun": str(row["Akun Debit"]),
                        "Debit (Rp)": debit_val,
                        "Kredit (Rp)": 0.0,
                        "No_Transaksi": safe_float_convert(row["No"], 0)
                    })
                
                # Entri Kredit dari Penutup
                if kredit_val > 0:
                    semua_transaksi.append({
                        "Tanggal": row["Tanggal"],
                        "Sumber": "Jurnal Penutup",
                        "Keterangan": str(row["Keterangan"]),
                        "Nama Akun": str(row["Akun Kredit"]),
                        "Debit (Rp)": 0.0,
                        "Kredit (Rp)": kredit_val,
                        "No_Transaksi": safe_float_convert(row["No"], 0)
                    })

        # ========== 5. PROSES BUKU BESAR PER AKUN ==========
        if not semua_transaksi:
            st.session_state.df_buku_besar = pd.DataFrame(columns=[
                "No", "Tanggal", "Sumber", "Keterangan", "Nama Akun", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"
            ])
            st.session_state.buku_besar_per_akun = {}
            return

        # Konversi ke DataFrame dengan validasi
        df_semua_transaksi = pd.DataFrame(semua_transaksi)
        
        # PERBAIKAN: Validasi dan cleaning data sebelum processing
        if not df_semua_transaksi.empty:
            # Pastikan kolom tanggal dalam format yang benar
            df_semua_transaksi['Tanggal'] = pd.to_datetime(df_semua_transaksi['Tanggal'], errors='coerce').dt.date
            
            # Pastikan tipe data numerik konsisten
            df_semua_transaksi['Debit (Rp)'] = df_semua_transaksi['Debit (Rp)'].apply(safe_float_convert)
            df_semua_transaksi['Kredit (Rp)'] = df_semua_transaksi['Kredit (Rp)'].apply(safe_float_convert)
            df_semua_transaksi['No_Transaksi'] = df_semua_transaksi['No_Transaksi'].apply(lambda x: int(safe_float_convert(x, 0)))
            
            # Hapus baris dengan Nama Akun yang tidak valid
            df_semua_transaksi = df_semua_transaksi[df_semua_transaksi['Nama Akun'].notna()]
            df_semua_transaksi = df_semua_transaksi[df_semua_transaksi['Nama Akun'] != '']
            
            # Urutkan berdasarkan tanggal dan nama akun
            df_semua_transaksi = df_semua_transaksi.sort_values(["Nama Akun", "Tanggal", "No_Transaksi"]).reset_index(drop=True)

        # Buat struktur buku besar per akun
        buku_besar_per_akun = {}
        
        # Kelompokkan transaksi per akun
        for akun in df_semua_transaksi["Nama Akun"].unique():
            transaksi_akun = df_semua_transaksi[df_semua_transaksi["Nama Akun"] == akun].copy()
            transaksi_akun = transaksi_akun.sort_values(["Tanggal", "No_Transaksi"]).reset_index(drop=True)
            
            # Hitung saldo running untuk akun ini
            saldo_running = 0.0
            detail_akun = []
            
            for idx, transaksi in transaksi_akun.iterrows():
                debit = safe_float_convert(transaksi["Debit (Rp)"])
                kredit = safe_float_convert(transaksi["Kredit (Rp)"])
                saldo_running += debit - kredit
                
                detail_akun.append({
                    "No": idx + 1,
                    "Tanggal": transaksi["Tanggal"],
                    "Sumber": transaksi["Sumber"],
                    "Keterangan": transaksi["Keterangan"],
                    "No_Transaksi": int(transaksi["No_Transaksi"]),
                    "Debit (Rp)": debit,
                    "Kredit (Rp)": kredit,
                    "Saldo (Rp)": saldo_running
                })
            
            # Simpan detail akun
            if detail_akun:  # Hanya simpan jika ada transaksi
                buku_besar_per_akun[akun] = pd.DataFrame(detail_akun)

        # Simpan ke session state
        st.session_state.buku_besar_per_akun = buku_besar_per_akun
        
        # Juga simpan dalam format flat untuk kompatibilitas
        semua_detail = []
        for akun, df_akun in buku_besar_per_akun.items():
            for _, row in df_akun.iterrows():
                semua_detail.append({
                    "No": int(row["No"]),
                    "Tanggal": row["Tanggal"],
                    "Sumber": row["Sumber"],
                    "Keterangan": row["Keterangan"],
                    "Nama Akun": akun,
                    "Debit (Rp)": safe_float_convert(row["Debit (Rp)"]),
                    "Kredit (Rp)": safe_float_convert(row["Kredit (Rp)"]),
                    "Saldo (Rp)": safe_float_convert(row["Saldo (Rp)"])
                })
        
        if semua_detail:
            st.session_state.df_buku_besar = pd.DataFrame(semua_detail)
        else:
            st.session_state.df_buku_besar = pd.DataFrame(columns=[
                "No", "Tanggal", "Sumber", "Keterangan", "Nama Akun", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"
            ])
        
        # Update neraca saldo
        update_neraca_saldo_dari_buku_besar_per_akun(buku_besar_per_akun)
        
        print(f"✅ Buku besar per akun diperbarui: {len(buku_besar_per_akun)} akun")
        
    except Exception as e:
        st.error(f"Error dalam update_buku_besar_per_akun_dengan_saldo_awal: {str(e)}")
        import traceback
        st.error(f"Detail error: {traceback.format_exc()}")
        # Fallback: buat buku besar kosong
        st.session_state.df_buku_besar = pd.DataFrame(columns=[
            "No", "Tanggal", "Sumber", "Keterangan", "Nama Akun", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"
        ])
        st.session_state.buku_besar_per_akun = {}
         
    
def buat_neraca_saldo_manual():
    """
    Fungsi untuk membuat neraca saldo secara manual dari data transaksi
    ketika fungsi utama tidak bekerja
    """
    try:
        df_akun_template = pd.DataFrame({"Nama Akun": [
            "Kas", "Persediaan", "Perlengkapan", "Aset biologis", "Peralatan",
            "Kendaraan", "Tanah", "Piutang", "Utang Usaha", "Utang Bank", "Utang Gaji",
            "Modal", "Penjualan", "Pendapatan Lain", "Beban listrik dan air", 
            "Beban transportasi", "Beban gaji", "Beban Lain"
        ]})
        # Ambil data dari berbagai sumber
        data_sources = []
        
        # 1. Dari neraca saldo periode sebelumnya
        if "df_neraca_saldo_periode_sebelumnya" in st.session_state:
            df_sebelumnya = st.session_state.df_neraca_saldo_periode_sebelumnya
            if not df_sebelumnya.empty and "Nama Akun" in df_sebelumnya.columns:
                data_sources.append(df_sebelumnya[["Nama Akun", "Debit (Rp)", "Kredit (Rp)"]])
        
        # 2. Dari jurnal umum format lama
        if "df_jurnal_umum_old_format" in st.session_state:
            df_jurnal = st.session_state.df_jurnal_umum_old_format
            if not df_jurnal.empty and "Nama Akun" in df_jurnal.columns:
                data_sources.append(df_jurnal[["Nama Akun", "Debit (Rp)", "Kredit (Rp)"]])
        
        # 3. Dari jurnal umum format baru (konversi manual)
        if "df_jurnal_umum" in st.session_state:
            df_jurnal_baru = st.session_state.df_jurnal_umum
            if not df_jurnal_baru.empty:
                # Konversi format baru ke format lama
                rows_manual = []
                for _, row in df_jurnal_baru.iterrows():
                    if row["Debit (Rp)"] > 0:
                        rows_manual.append({
                            "Nama Akun": row["Akun Debit"],
                            "Debit (Rp)": row["Debit (Rp)"],
                            "Kredit (Rp)": 0
                        })
                    if row["Kredit (Rp)"] > 0:
                        rows_manual.append({
                            "Nama Akun": row["Akun Kredit"],
                            "Debit (Rp)": 0,
                            "Kredit (Rp)": row["Kredit (Rp)"]
                        })
                if rows_manual:
                    df_manual = pd.DataFrame(rows_manual)
                    data_sources.append(df_manual)
        
        # Gabungkan semua data sumber
        if data_sources:
            all_data = pd.concat(data_sources, ignore_index=True)
            
            # Group by akun dan hitung total debit/kredit
            neraca_saldo = all_data.groupby("Nama Akun").agg({
                "Debit (Rp)": "sum",
                "Kredit (Rp)": "sum"
            }).reset_index()
            
            # Tambahkan nomor urut
            neraca_saldo.insert(0, "No", range(1, len(neraca_saldo) + 1))
            
            # Tambahkan baris total
            total_debit = neraca_saldo["Debit (Rp)"].sum()
            total_kredit = neraca_saldo["Kredit (Rp)"].sum()
            total_row = {
                "No": "",
                "Nama Akun": "TOTAL",
                "Debit (Rp)": total_debit,
                "Kredit (Rp)": total_kredit
            }
            
            neraca_final = pd.concat([neraca_saldo, pd.DataFrame([total_row])], ignore_index=True)
            return neraca_final
        
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Error dalam buat_neraca_saldo_manual: {str(e)}")
        return pd.DataFrame()
    
def update_sistem_dengan_struktur_baru():
    """
    Fungsi untuk update sistem dengan struktur data baru - VERSI DIPERBAIKI
    Memastikan double entry mempunyai satu nomor yang sama
    """
    try:
        # Pastikan nomor urut konsisten sebelum konversi
        if "df_jurnal_umum" in st.session_state and not st.session_state.df_jurnal_umum.empty:
            df_baru = st.session_state.df_jurnal_umum.copy()
            
            # Untuk double entry: pastikan entri dengan nomor sama tetap dipertahankan
            # Tidak perlu reset numbering di sini karena sudah dihandle di fungsi lain
            
            # Konversi ke format lama untuk kompatibilitas
            rows_old_format = []
            
            for _, row in df_baru.iterrows():
                # Tambahkan entri debit (hanya jika jumlah > 0)
                if row["Debit (Rp)"] > 0:
                    rows_old_format.append({
                        "Tanggal": row["Tanggal"],
                        "Nama Akun": row["Akun Debit"],
                        "Debit (Rp)": row["Debit (Rp)"],
                        "Kredit (Rp)": 0
                    })
                
                # Tambahkan entri kredit (hanya jika jumlah > 0)
                if row["Kredit (Rp)"] > 0:
                    rows_old_format.append({
                        "Tanggal": row["Tanggal"],
                        "Nama Akun": row["Akun Kredit"],
                        "Debit (Rp)": 0,
                        "Kredit (Rp)": row["Kredit (Rp)"]
                    })
            
            # Simpan dalam session state untuk kompatibilitas
            if rows_old_format:
                st.session_state.df_jurnal_umum_old_format = pd.DataFrame(rows_old_format)
            else:
                st.session_state.df_jurnal_umum_old_format = pd.DataFrame(columns=["Tanggal", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"])
            
            # UPDATE BUKU BESAR
            update_buku_besar_per_akun()
            auto_save()
            
            print("✅ Sistem berhasil diupdate dengan struktur baru")
         
        else:
            st.session_state.df_jurnal_umum_old_format = pd.DataFrame(columns=["Tanggal", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"])
            
    except Exception as e:
        st.error(f"Error dalam update_sistem_dengan_struktur_baru: {str(e)}")
        
        
def display_buku_besar_fixed():
    """Menampilkan buku besar dengan error handling yang lebih baik"""
    st.subheader("Buku Besar 📚")
    st.markdown(f"**Periode:** {st.session_state.periode_sekarang}")
    
    # Update buku besar per akun dengan error handling
    try:
        with st.spinner("Memperbarui buku besar..."):
            update_buku_besar_per_akun()
    except Exception as e:
        st.error(f"Error saat memperbarui buku besar: {str(e)}")
        st.info("Silakan coba refresh halaman atau tambah transaksi di Jurnal Umum terlebih dahulu.")
    
    # Tampilkan informasi sumber data
    st.info("""**Buku Besar ini menggabungkan data dari:**
    - ✅ **Jurnal Umum** - Transaksi harian
    - ✅ **Jurnal Penyesuaian** - Penyesuaian periode  
    - ✅ **Jurnal Penutup** - Penutupan periode
    """)
    
    if "buku_besar_per_akun" not in st.session_state or not st.session_state.buku_besar_per_akun:
        st.info("Buku Besar masih kosong. Silakan tambah transaksi di Jurnal Umum terlebih dahulu.")
        
        # Debug information
        with st.expander("🔧 Debug Information"):
            st.write("Session State Keys:", [k for k in st.session_state.keys() if 'jurnal' in k or 'buku' in k])
            if "df_jurnal_umum" in st.session_state:
                st.write("Jurnal Umum data:", len(st.session_state.df_jurnal_umum))
            if "df_jurnal_penyesuaian" in st.session_state:
                st.write("Jurnal Penyesuaian data:", len(st.session_state.df_jurnal_penyesuaian))
        
        return
    
    buku_besar_per_akun = st.session_state.buku_besar_per_akun
    
    # Tampilkan setiap akun dalam expander
    for akun in sorted(buku_besar_per_akun.keys()):
        df_akun = buku_besar_per_akun[akun]
        
        with st.expander(f"**{akun}** - {len(df_akun)} transaksi", expanded=False):
            if not df_akun.empty:
                # Header informasi akun dengan safe_float_convert
                saldo_akhir = safe_float_convert(df_akun["Saldo (Rp)"].iloc[-1])
                total_debit = sum(df_akun["Debit (Rp)"].apply(safe_float_convert))
                total_kredit = sum(df_akun["Kredit (Rp)"].apply(safe_float_convert))
                
                col_info1, col_info2, col_info3, col_info4 = st.columns(4)
                with col_info1:
                    st.metric("Total Debit", f"Rp {total_debit:,.0f}")
                with col_info2:
                    st.metric("Total Kredit", f"Rp {total_kredit:,.0f}")
                with col_info3:
                    st.metric("Saldo Akhir", f"Rp {saldo_akhir:,.0f}")
                with col_info4:
                    status = "Debit" if saldo_akhir > 0 else "Kredit" if saldo_akhir < 0 else "Nol"
                    st.metric("Posisi", status)
                
                # Tampilkan tabel transaksi dengan format aman
                st.write("### 📋 Detail Transaksi")
                
                # Buat copy untuk tampilan dengan format yang aman
                df_tampil = safe_dataframe_display(df_akun)
                
                # Tampilkan tabel
                st.dataframe(
                    df_tampil[["No", "Tanggal", "Sumber", "Keterangan", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Tidak ada transaksi untuk akun ini.")

def display_neraca_saldo_fixed():
    """Menampilkan neraca saldo dengan error handling yang lebih baik"""
    st.subheader("Neraca Saldo 📊")
    st.markdown(f"**Periode:** {st.session_state.periode_sekarang}")
    
    # Update neraca saldo terlebih dahulu
    try:
        update_buku_besar_per_akun()
    except Exception as e:
        st.error(f"Error saat memperbarui neraca saldo: {str(e)}")
    
    # Tampilkan neraca saldo
    if "df_neraca_saldo" in st.session_state and not st.session_state.df_neraca_saldo.empty:
        st.write("### 📋 Daftar Neraca Saldo")
        
        # Gunakan safe_dataframe_display untuk format yang aman
        df_tampil = safe_dataframe_display(st.session_state.df_neraca_saldo)
        
        # Tampilkan tabel
        st.dataframe(df_tampil, use_container_width=True, hide_index=True)
        
        # Hitung total dari data asli dengan safe_float_convert
        df_asli = st.session_state.df_neraca_saldo
        total_debit = 0
        total_kredit = 0
        
        # Hitung total hanya dari baris yang bukan TOTAL
        for _, row in df_asli.iterrows():
            if row["Nama Akun"] != "TOTAL":
                total_debit += safe_float_convert(row["Debit (Rp)"])
                total_kredit += safe_float_convert(row["Kredit (Rp)"])
        
        # Tampilkan total
        st.write("### 💰 Total Neraca Saldo")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Debit", f"Rp {total_debit:,.0f}")
        with col2:
            st.metric("Total Kredit", f"Rp {total_kredit:,.0f}")
        
        # Validasi keseimbangan
        selisih = abs(total_debit - total_kredit)
        if selisih < 1:
            st.success("✅ Neraca Saldo SEIMBANG")
        else:
            st.error(f"❌ Neraca Saldo TIDAK SEIMBANG - Selisih: Rp {selisih:,.0f}")
            
    else:
        st.info("""
        **Belum ada data neraca saldo.**
        
        **Untuk membuat neraca saldo:**
        1. Tambahkan transaksi di menu **Jurnal Umum**
        2. Jika diperlukan, buat penyesuaian di menu **Jurnal Penyesuaian**
        3. Neraca saldo akan otomatis terbentuk dari data transaksi yang sudah dicatat
        """)

# ==================== FUNGSI INITIALIZATION DAN CLEANUP ====================

def initialize_fixed_session_state():
    """Inisialisasi session state dengan nilai default yang aman - VERSI DIPERBAIKI"""
    default_dataframes = {
        "df_jurnal_umum": ["No", "Tanggal", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"],
        "df_jurnal_penyesuaian": ["No", "Tanggal", "Keterangan", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"],
        "df_neraca_saldo_periode_sebelumnya": ["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"],
        "df_buku_besar": ["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"],
        "df_neraca_saldo": ["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"],
        "df_jurnal_penutup": ["No", "Tanggal", "Keterangan", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"],
        "df_neraca_saldo_setelah_penutup": ["No", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"],
        "df_penjualan": ["No", "Tanggal", "Keterangan", "Barang", "Jumlah", "Harga Jual", "Total Penjualan", "HPP", "Total HPP"],
        "df_pembelian": ["No", "Tanggal", "Keterangan", "Barang", "Jumlah", "Harga Beli", "Total Pembelian"],
        "df_persediaan": ["Barang", "Stok Awal", "Pembelian", "Penjualan", "Stok Akhir", "Harga Rata-rata", "Total Nilai"],
        "df_riwayat_persediaan": ["Tanggal", "Jenis", "Barang", "Jumlah", "Harga", "Total", "Stok", "Keterangan"]
    }
    
    for df_key, columns in default_dataframes.items():
        if df_key not in st.session_state:
            st.session_state[df_key] = pd.DataFrame(columns=columns)
    
    # Inisialisasi counter transaksi
    if "transaction_counter" not in st.session_state:
        st.session_state.transaction_counter = 1
    
    # Inisialisasi buku besar per akun
    if "buku_besar_per_akun" not in st.session_state:
        st.session_state.buku_besar_per_akun = {}

        
def hitung_laba_rugi(df_jurnal):
    # PERBARUI KATEGORI DENGAN AKUN BARU
    kategori = {
        "Pendapatan": ["Penjualan", "Pendapatan Lain"],  # Tambah Pendapatan Lain
        "Beban": [
            "Beban listrik dan air", "Beban transportasi", "Beban gaji", 
            "Beban Lain"  # Tambah Beban Lain
        ]
    }

    # Jika DataFrame kosong, return 0
    if df_jurnal.empty:
        return 0, 0, 0

    # Cek apakah ini format baru atau format lama
    if "Akun Debit" in df_jurnal.columns and "Akun Kredit" in df_jurnal.columns:
        # FORMAT BARU: Gunakan df_jurnal_umum_old_format dari session state
        if "df_jurnal_umum_old_format" in st.session_state and not st.session_state.df_jurnal_umum_old_format.empty:
            df_jurnal = st.session_state.df_jurnal_umum_old_format
        else:
            return 0, 0, 0
    
    # Pastikan kolom yang diperlukan ada
    if "Nama Akun" not in df_jurnal.columns:
        st.error("Error: Kolom 'Nama Akun' tidak ditemukan dalam data jurnal.")
        return 0, 0, 0

    df_jurnal = df_jurnal.copy()
    df_jurnal["Debit (Rp)"] = df_jurnal["Debit (Rp)"].fillna(0)
    df_jurnal["Kredit (Rp)"] = df_jurnal["Kredit (Rp)"].fillna(0)

    pendapatan = df_jurnal[df_jurnal["Nama Akun"].isin(kategori["Pendapatan"])]
    beban = df_jurnal[df_jurnal["Nama Akun"].isin(kategori["Beban"])]

    total_pendapatan = pendapatan["Kredit (Rp)"].sum()  # Pendapatan di kolom Kredit
    total_beban = beban["Debit (Rp)"].sum()             # Beban di kolom Debit
    laba_bersih = total_pendapatan - total_beban
    
    if "df_semua_transaksi" in st.session_state and not st.session_state.df_semua_transaksi.empty:
        df_jurnal = st.session_state.df_semua_transaksi
    return total_pendapatan, total_beban, laba_bersih

def hitung_perubahan_modal(laba_bersih, modal_awal):
    """Menghitung perubahan modal dengan benar"""
    try:
        # Hitung modal akhir
        modal_akhir = modal_awal + laba_bersih
        
        perubahan_modal = {
            "Modal Awal": modal_awal,
            "Laba/Rugi Bersih": laba_bersih,
            "Modal Akhir": modal_akhir
        }
        
        df_perubahan = pd.DataFrame.from_dict(perubahan_modal, orient="index", columns=["Nilai (Rp)"])
        df_perubahan.index.name = "Keterangan"
        
        # Simpan ke session state untuk digunakan di laporan posisi keuangan
        st.session_state.modal_akhir = modal_akhir
        st.session_state.df_laporan_perubahan_modal = df_perubahan
        
        return df_perubahan
        
    except Exception as e:
        st.error(f"Error dalam hitung_perubahan_modal: {str(e)}")
        return pd.DataFrame()
    
def hitung_perubahan_modal_diperbaiki(laba_bersih):
    """Menghitung perubahan modal dengan benar - VERSI DIPERBAIKI"""
    try:
        # Cari modal awal dari neraca saldo periode sebelumnya
        modal_awal = 0
        if "df_neraca_saldo_periode_sebelumnya" in st.session_state and not st.session_state.df_neraca_saldo_periode_sebelumnya.empty:
            modal_data = st.session_state.df_neraca_saldo_periode_sebelumnya[
                st.session_state.df_neraca_saldo_periode_sebelumnya["Nama Akun"] == "Modal"
            ]
            if not modal_data.empty:
                # Modal biasanya di kredit, tapi bisa juga di debit tergantung saldo
                debit_modal = safe_float_convert(modal_data["Debit (Rp)"].iloc[0])
                kredit_modal = safe_float_convert(modal_data["Kredit (Rp)"].iloc[0])
                modal_awal = kredit_modal - debit_modal
        
        # Jika tidak ada di periode sebelumnya, coba cari dari buku besar
        if modal_awal == 0 and "df_buku_besar" in st.session_state and not st.session_state.df_buku_besar.empty:
            modal_data = st.session_state.df_buku_besar[
                st.session_state.df_buku_besar["Nama Akun"] == "Modal"
            ]
            if not modal_data.empty:
                modal_awal = safe_float_convert(modal_data["Saldo (Rp)"].iloc[-1])
        
        # Jika masih 0, coba dari neraca saldo saat ini
        if modal_awal == 0 and "df_neraca_saldo" in st.session_state and not st.session_state.df_neraca_saldo.empty:
            modal_data = st.session_state.df_neraca_saldo[
                st.session_state.df_neraca_saldo["Nama Akun"] == "Modal"
            ]
            if not modal_data.empty:
                debit_modal = safe_float_convert(modal_data["Debit (Rp)"].iloc[0])
                kredit_modal = safe_float_convert(modal_data["Kredit (Rp)"].iloc[0])
                modal_awal = kredit_modal - debit_modal
        
        # Hitung modal akhir
        modal_akhir = modal_awal + laba_bersih
        
        # Buat laporan perubahan modal
        perubahan_modal_data = [
            {"Keterangan": "Modal Awal", "Nilai (Rp)": modal_awal},
            {"Keterangan": "Laba (Rugi) Bersih", "Nilai (Rp)": laba_bersih},
            {"Keterangan": "**Modal Akhir**", "Nilai (Rp)": modal_akhir}
        ]
        
        df_perubahan_modal = pd.DataFrame(perubahan_modal_data)
        
        # Simpan ke session state
        st.session_state.modal_awal = modal_awal
        st.session_state.modal_akhir = modal_akhir
        st.session_state.df_laporan_perubahan_modal = df_perubahan_modal
        
        return df_perubahan_modal
        
    except Exception as e:
        st.error(f"Error dalam hitung_perubahan_modal_diperbaiki: {str(e)}")
        
        # Return default values in case of error
        perubahan_modal_data = [
            {"Keterangan": "Modal Awal", "Nilai (Rp)": 0},
            {"Keterangan": "Laba (Rugi) Bersih", "Nilai (Rp)": laba_bersih},
            {"Keterangan": "**Modal Akhir**", "Nilai (Rp)": laba_bersih}
        ]
        return pd.DataFrame(perubahan_modal_data)
    
    
def hitung_posisi_keuangan_selalu_seimbang():
    """Menghitung laporan posisi keuangan yang selalu seimbang - VERSI OPTIMIZED"""
    try:
        # Dapatkan data dari buku besar per akun (lebih akurat)
        if "buku_besar_per_akun" not in st.session_state or not st.session_state.buku_besar_per_akun:
            st.info("📊 Data buku besar kosong. Pastikan sudah ada transaksi di Jurnal Umum.")
            return buat_posisi_keuangan_kosong()
        
        buku_besar_per_akun = st.session_state.buku_besar_per_akun
        
        # ========== KLASIFIKASI AKUN YANG LEBIH LENGKAP ==========
        akun_aset_lancar = [
            "Kas", "Bank", "Deposito", "Investasi Jangka Pendek", 
            "Piutang Usaha", "Piutang Dagang", "Piutang Lainnya",
            "Persediaan", "Persediaan Barang Dagang", "Persediaan Bahan Baku",
            "Persediaan Barang Dalam Proses", "Persediaan Barang Jadi",
            "Perlengkapan", "Asuransi Dibayar Dimuka", "Sewa Dibayar Dimuka",
            "Pajak Dibayar Dimuka", "Biaya Dibayar Dimuka", "Pendapatan Ditangguhkan"
        ]
        
        akun_aset_tidak_lancar = [
            "Tanah", "Gedung", "Bangunan", "Kendaraan", "Peralatan", "Mesin",
            "Inventaris", "Akumulasi Penyusutan", "Aset Tetap Lainnya",
            "Investasi Jangka Panjang", "Aset Tidak Berwujud", "Goodwill",
            "Paten", "Merek Dagang", "Hak Cipta", "Aset Sewa Guna Usaha",
            "Aset Biologis", "Aset biologis"  # untuk kompatibilitas
        ]
        
        akun_liabilitas_jangka_pendek = [
            "Utang Usaha", "Utang Dagang", "Utang Bank Jangka Pendek",
            "Utang Wesel", "Utang Gaji", "Utang Pajak", "Utang Bunga",
            "Utang Dividen", "Pendapatan Diterima Dimuka", "Biaya Akrual",
            "Utang Jangka Pendek Lainnya", "Bagian Lancar Utang Jangka Panjang"
        ]
        
        akun_liabilitas_jangka_panjang = [
            "Utang Bank Jangka Panjang", "Utang Obligasi", "Utang Hipotek",
            "Utang Sewa Guna Usaha", "Utang Pensiun", "Utang Jangka Panjang Lainnya"
        ]
        
        akun_ekuitas = [
            "Modal Saham", "Modal Disetor", "Agio Saham",
            "Laba Ditahan", "Saldo Laba", "Deviden",
            "Prive", "Modal Pemilik", "Modal",  # untuk kompatibilitas
            "Ekuitas Lainnya", "Cadangan"
        ]
        
        # Fungsi untuk mendapatkan saldo akhir akun
        def get_saldo_akun(nama_akun):
            if nama_akun in buku_besar_per_akun:
                df_akun = buku_besar_per_akun[nama_akun]
                if not df_akun.empty:
                    return safe_float_convert(df_akun["Saldo (Rp)"].iloc[-1])
            return 0
        
        # ========== KUMPULKAN DATA ASET ==========
        aset_lancar_data = []
        aset_tidak_lancar_data = []
        total_aset_lancar = 0
        total_aset_tidak_lancar = 0
        
        # Aset Lancar
        for akun in akun_aset_lancar:
            saldo = get_saldo_akun(akun)
            if saldo > 0:  # Aset harus positif
                aset_lancar_data.append({"Keterangan": akun, "Nilai (Rp)": saldo})
                total_aset_lancar += saldo
        
        # Aset Tidak Lancar
        for akun in akun_aset_tidak_lancar:
            saldo = get_saldo_akun(akun)
            # Untuk aset tetap dengan akumulasi penyusutan
            if "Akumulasi Penyusutan" in akun and saldo != 0:
                aset_tidak_lancar_data.append({"Keterangan": akun, "Nilai (Rp)": -saldo})
                total_aset_tidak_lancar -= saldo
            elif saldo > 0:  # Aset harus positif
                aset_tidak_lancar_data.append({"Keterangan": akun, "Nilai (Rp)": saldo})
                total_aset_tidak_lancar += saldo
        
        # ========== KUMPULKAN DATA LIABILITAS ==========
        liabilitas_jangka_pendek_data = []
        liabilitas_jangka_panjang_data = []
        total_liabilitas_jangka_pendek = 0
        total_liabilitas_jangka_panjang = 0
        
        # Liabilitas Jangka Pendek
        for akun in akun_liabilitas_jangka_pendek:
            saldo = get_saldo_akun(akun)
            if saldo != 0:
                # Liabilitas biasanya saldo kredit (negatif), tampilkan sebagai positif
                nilai_liabilitas = abs(saldo) if saldo < 0 else saldo
                liabilitas_jangka_pendek_data.append({"Keterangan": akun, "Nilai (Rp)": nilai_liabilitas})
                total_liabilitas_jangka_pendek += nilai_liabilitas
        
        # Liabilitas Jangka Panjang
        for akun in akun_liabilitas_jangka_panjang:
            saldo = get_saldo_akun(akun)
            if saldo != 0:
                nilai_liabilitas = abs(saldo) if saldo < 0 else saldo
                liabilitas_jangka_panjang_data.append({"Keterangan": akun, "Nilai (Rp)": nilai_liabilitas})
                total_liabilitas_jangka_panjang += nilai_liabilitas
        
        total_liabilitas = total_liabilitas_jangka_pendek + total_liabilitas_jangka_panjang
        
        # ========== KUMPULKAN DATA EKUITAS ==========
        ekuitas_data = []
        total_ekuitas = 0
        
        # Ekuitas - gunakan data dari berbagai sumber
        modal_akhir = getattr(st.session_state, 'modal_akhir', 0)
        laba_bersih = getattr(st.session_state, 'laba_bersih', 0)
        
        # Jika modal_akhir belum ada, hitung dari saldo akun Modal
        if modal_akhir == 0:
            # Coba semua variasi akun modal
            for akun_modal in ["Modal", "Modal Saham", "Modal Pemilik", "Modal Disetor"]:
                modal_saldo = get_saldo_akun(akun_modal)
                if modal_saldo != 0:
                    modal_akhir = abs(modal_saldo) if modal_saldo < 0 else modal_saldo
                    break
        
        # Tambahkan modal ke ekuitas
        if modal_akhir > 0:
            ekuitas_data.append({"Keterangan": "Modal", "Nilai (Rp)": modal_akhir})
            total_ekuitas += modal_akhir
        
        # Tambahkan laba bersih ke ekuitas (sebagai Laba Ditahan)
        if laba_bersih != 0:
            ekuitas_data.append({"Keterangan": "Laba (Rugi) Ditahan", "Nilai (Rp)": laba_bersih})
            total_ekuitas += laba_bersih
        
        # Tambahkan akun ekuitas lainnya yang ada saldonya
        for akun in akun_ekuitas:
            if akun not in ["Modal", "Modal Saham", "Modal Pemilik", "Modal Disetor"]:
                saldo = get_saldo_akun(akun)
                if saldo != 0:
                    nilai_ekuitas = abs(saldo) if saldo < 0 else saldo
                    ekuitas_data.append({"Keterangan": akun, "Nilai (Rp)": nilai_ekuitas})
                    total_ekuitas += nilai_ekuitas
        
        # ========== HITUNG TOTAL DAN VALIDASI KESEIMBANGAN ==========
        total_aset = total_aset_lancar + total_aset_tidak_lancar
        total_liabilitas_ekuitas = total_liabilitas + total_ekuitas
        
        # VALIDASI KESEIMBANGAN - METODE OTOMATIS
        selisih = total_aset - total_liabilitas_ekuitas
        
        if abs(selisih) > 1:  # Toleransi 1 rupiah untuk rounding error
            st.warning(f"⚠️ Ditemukan ketidakseimbangan: Rp {selisih:,.0f}")
            
            # PENYESUAIAN OTOMATIS: Tambahkan ke Laba Ditahan
            if abs(selisih) > 1:
                # Cari apakah sudah ada Laba Ditahan
                laba_ditahan_index = None
                for i, item in enumerate(ekuitas_data):
                    if item["Keterangan"] == "Laba (Rugi) Ditahan":
                        laba_ditahan_index = i
                        break
                
                if laba_ditahan_index is not None:
                    # Update existing Laba Ditahan
                    ekuitas_data[laba_ditahan_index]["Nilai (Rp)"] += selisih
                else:
                    # Tambahkan baru Laba Ditahan
                    ekuitas_data.append({"Keterangan": "Laba (Rugi) Ditahan", "Nilai (Rp)": selisih})
                
                total_ekuitas += selisih
                total_liabilitas_ekuitas += selisih
                
                st.info(f"✅ Dilakukan penyesuaian otomatis: Laba Ditahan {'ditambah' if selisih > 0 else 'dikurangi'} Rp {abs(selisih):,.0f}")
        
        # ========== BUAT LAPORAN POSISI KEUANGAN ==========
        posisi_keuangan_data = []
        
        # Bagian Aset
        posisi_keuangan_data.append({"Keterangan": "**ASET**", "Nilai (Rp)": ""})
        
        # Aset Lancar
        if aset_lancar_data:
            posisi_keuangan_data.append({"Keterangan": "**Aset Lancar**", "Nilai (Rp)": ""})
            for item in aset_lancar_data:
                posisi_keuangan_data.append(item)
            posisi_keuangan_data.append({"Keterangan": "**Total Aset Lancar**", "Nilai (Rp)": total_aset_lancar})
        else:
            posisi_keuangan_data.append({"Keterangan": "**Aset Lancar**", "Nilai (Rp)": ""})
            posisi_keuangan_data.append({"Keterangan": "Tidak ada aset lancar", "Nilai (Rp)": ""})
            posisi_keuangan_data.append({"Keterangan": "**Total Aset Lancar**", "Nilai (Rp)": 0})
        
        # Aset Tidak Lancar
        if aset_tidak_lancar_data:
            posisi_keuangan_data.append({"Keterangan": "**Aset Tidak Lancar**", "Nilai (Rp)": ""})
            for item in aset_tidak_lancar_data:
                posisi_keuangan_data.append(item)
            posisi_keuangan_data.append({"Keterangan": "**Total Aset Tidak Lancar**", "Nilai (Rp)": total_aset_tidak_lancar})
        else:
            posisi_keuangan_data.append({"Keterangan": "**Aset Tidak Lancar**", "Nilai (Rp)": ""})
            posisi_keuangan_data.append({"Keterangan": "Tidak ada aset tidak lancar", "Nilai (Rp)": ""})
            posisi_keuangan_data.append({"Keterangan": "**Total Aset Tidak Lancar**", "Nilai (Rp)": 0})
        
        posisi_keuangan_data.append({"Keterangan": "**TOTAL ASET**", "Nilai (Rp)": total_aset})
        posisi_keuangan_data.append({"Keterangan": "", "Nilai (Rp)": ""})
        
        # Bagian Liabilitas dan Ekuitas
        posisi_keuangan_data.append({"Keterangan": "**LIABILITAS & EKUITAS**", "Nilai (Rp)": ""})
        
        # Liabilitas Jangka Pendek
        if liabilitas_jangka_pendek_data:
            posisi_keuangan_data.append({"Keterangan": "**Liabilitas Jangka Pendek**", "Nilai (Rp)": ""})
            for item in liabilitas_jangka_pendek_data:
                posisi_keuangan_data.append(item)
            posisi_keuangan_data.append({"Keterangan": "**Total Liabilitas Jangka Pendek**", "Nilai (Rp)": total_liabilitas_jangka_pendek})
        else:
            posisi_keuangan_data.append({"Keterangan": "**Liabilitas Jangka Pendek**", "Nilai (Rp)": ""})
            posisi_keuangan_data.append({"Keterangan": "Tidak ada liabilitas jangka pendek", "Nilai (Rp)": ""})
            posisi_keuangan_data.append({"Keterangan": "**Total Liabilitas Jangka Pendek**", "Nilai (Rp)": 0})
        
        # Liabilitas Jangka Panjang
        if liabilitas_jangka_panjang_data:
            posisi_keuangan_data.append({"Keterangan": "**Liabilitas Jangka Panjang**", "Nilai (Rp)": ""})
            for item in liabilitas_jangka_panjang_data:
                posisi_keuangan_data.append(item)
            posisi_keuangan_data.append({"Keterangan": "**Total Liabilitas Jangka Panjang**", "Nilai (Rp)": total_liabilitas_jangka_panjang})
        else:
            posisi_keuangan_data.append({"Keterangan": "**Liabilitas Jangka Panjang**", "Nilai (Rp)": ""})
            posisi_keuangan_data.append({"Keterangan": "Tidak ada liabilitas jangka panjang", "Nilai (Rp)": ""})
            posisi_keuangan_data.append({"Keterangan": "**Total Liabilitas Jangka Panjang**", "Nilai (Rp)": 0})
        
        posisi_keuangan_data.append({"Keterangan": "**TOTAL LIABILITAS**", "Nilai (Rp)": total_liabilitas})
        posisi_keuangan_data.append({"Keterangan": "", "Nilai (Rp)": ""})
        
        # Ekuitas
        if ekuitas_data:
            posisi_keuangan_data.append({"Keterangan": "**Ekuitas**", "Nilai (Rp)": ""})
            for item in ekuitas_data:
                posisi_keuangan_data.append(item)
            posisi_keuangan_data.append({"Keterangan": "**Total Ekuitas**", "Nilai (Rp)": total_ekuitas})
        else:
            posisi_keuangan_data.append({"Keterangan": "**Ekuitas**", "Nilai (Rp)": ""})
            posisi_keuangan_data.append({"Keterangan": "Tidak ada ekuitas", "Nilai (Rp)": ""})
            posisi_keuangan_data.append({"Keterangan": "**Total Ekuitas**", "Nilai (Rp)": 0})
        
        total_liabilitas_ekuitas = total_liabilitas + total_ekuitas
        posisi_keuangan_data.append({"Keterangan": "**TOTAL LIABILITAS & EKUITAS**", "Nilai (Rp)": total_liabilitas_ekuitas})
        
        # Final validation
        final_selisih = abs(total_aset - total_liabilitas_ekuitas)
        if final_selisih <= 1:
            st.success("✅ Laporan Posisi Keuangan SEIMBANG")
        else:
            st.error(f"❌ Laporan Posisi Keuangan TIDAK SEIMBANG - Selisih: Rp {final_selisih:,.0f}")
        
        df_posisi_keuangan = pd.DataFrame(posisi_keuangan_data)
        st.session_state.df_laporan_posisi_keuangan = df_posisi_keuangan
        
        return df_posisi_keuangan
        
    except Exception as e:
        st.error(f"Error dalam hitung_posisi_keuangan_selalu_seimbang: {str(e)}")
        import traceback
        st.error(f"Detail error: {traceback.format_exc()}")
        return buat_posisi_keuangan_kosong()

def buat_posisi_keuangan_kosong():
    """Membuat laporan posisi keuangan kosong dengan struktur yang benar"""
    posisi_keuangan_data = [
        {"Keterangan": "**ASET**", "Nilai (Rp)": ""},
        {"Keterangan": "**Aset Lancar**", "Nilai (Rp)": ""},
        {"Keterangan": "Kas", "Nilai (Rp)": 0},
        {"Keterangan": "Persediaan", "Nilai (Rp)": 0},
        {"Keterangan": "Piutang", "Nilai (Rp)": 0},
        {"Keterangan": "**Total Aset Lancar**", "Nilai (Rp)": 0},
        {"Keterangan": "**Aset Tidak Lancar**", "Nilai (Rp)": ""},
        {"Keterangan": "Peralatan", "Nilai (Rp)": 0},
        {"Keterangan": "Kendaraan", "Nilai (Rp)": 0},
        {"Keterangan": "Tanah", "Nilai (Rp)": 0},
        {"Keterangan": "**Total Aset Tidak Lancar**", "Nilai (Rp)": 0},
        {"Keterangan": "**TOTAL ASET**", "Nilai (Rp)": 0},
        {"Keterangan": "", "Nilai (Rp)": ""},
        {"Keterangan": "**LIABILITAS & EKUITAS**", "Nilai (Rp)": ""},
        {"Keterangan": "**Liabilitas**", "Nilai (Rp)": ""},
        {"Keterangan": "Utang Usaha", "Nilai (Rp)": 0},
        {"Keterangan": "Utang Bank", "Nilai (Rp)": 0},
        {"Keterangan": "**Total Liabilitas**", "Nilai (Rp)": 0},
        {"Keterangan": "**Ekuitas**", "Nilai (Rp)": ""},
        {"Keterangan": "Modal", "Nilai (Rp)": 0},
        {"Keterangan": "Laba Ditahan", "Nilai (Rp)": 0},
        {"Keterangan": "**Total Ekuitas**", "Nilai (Rp)": 0},
        {"Keterangan": "**TOTAL LIABILITAS & EKUITAS**", "Nilai (Rp)": 0}
    ]
    return pd.DataFrame(posisi_keuangan_data)

def init_sistem_periode():
    """Inisialisasi sistem periode dengan data contoh"""
    # Pastikan neraca saldo periode sebelumnya ada data
    if st.session_state.df_neraca_saldo_periode_sebelumnya.empty:
        # Data contoh untuk periode pertama
        contoh_data = [
            {"No": 1, "Nama Akun": "Kas", "Debit (Rp)": 100000000, "Kredit (Rp)": 0},
            {"No": 2, "Nama Akun": "Persediaan", "Debit (Rp)": 50000000, "Kredit (Rp)": 0},
            {"No": 3, "Nama Akun": "Peralatan", "Debit (Rp)": 75000000, "Kredit (Rp)": 0},
            {"No": 4, "Nama Akun": "Utang Usaha", "Debit (Rp)": 0, "Kredit (Rp)": 45000000},
            {"No": 5, "Nama Akun": "Modal", "Debit (Rp)": 0, "Kredit (Rp)": 180000000},
        ]
        st.session_state.df_neraca_saldo_periode_sebelumnya = pd.DataFrame(contoh_data)
        print("✅ Data contoh neraca saldo periode sebelumnya berhasil diinisialisasi")


def hitung_posisi_keuangan_diperbaiki():
    """Menghitung laporan posisi keuangan (neraca) dengan validasi keseimbangan - VERSI DIPERBAIKI"""
    try:
        # Dapatkan data dari buku besar
        if "df_buku_besar" not in st.session_state or st.session_state.df_buku_besar.empty:
            st.info("📊 Data buku besar kosong. Pastikan sudah ada transaksi di Jurnal Umum.")
            return buat_posisi_keuangan_kosong()
        
        df_buku_besar = st.session_state.df_buku_besar
        
        # KLASIFIKASI AKUN - DIPERBARUI
        akun_aset_lancar = [
            "Kas", "Persediaan", "Perlengkapan", "Piutang Usaha", 
            "Asuransi Dibayar Dimuka", "Sewa Dibayar Dimuka", "Piutang"
        ]
        
        akun_aset_tidak_lancar = [
            "Peralatan", "Aset Biologis", "Kendaraan", "Tanah", "Gedung", "Aset biologis"
        ]
        
        akun_liabilitas = [
            "Utang Usaha", "Utang Bank", "Utang Gaji", "Pendapatan Diterima Dimuka"
        ]
        
        akun_ekuitas = ["Modal"]
        
        # Fungsi untuk mendapatkan saldo akun dari buku besar per akun (lebih akurat)
        def get_saldo_akun(nama_akun):
            # Coba dari buku besar per akun terlebih dahulu
            if "buku_besar_per_akun" in st.session_state and nama_akun in st.session_state.buku_besar_per_akun:
                df_akun = st.session_state.buku_besar_per_akun[nama_akun]
                if not df_akun.empty:
                    return safe_float_convert(df_akun["Saldo (Rp)"].iloc[-1])
            
            # Fallback ke buku besar flat
            akun_data = df_buku_besar[df_buku_besar["Nama Akun"] == nama_akun]
            if not akun_data.empty:
                return safe_float_convert(akun_data["Saldo (Rp)"].iloc[-1])
            return 0
        
        # Kumpulkan semua akun yang ada saldonya
        semua_akun_aktif = []
        for akun in akun_aset_lancar + akun_aset_tidak_lancar + akun_liabilitas + akun_ekuitas:
            saldo = get_saldo_akun(akun)
            if saldo != 0:
                semua_akun_aktif.append((akun, saldo))
        
        # Kumpulkan data aset
        aset_lancar_data = []
        aset_tidak_lancar_data = []
        total_aset_lancar = 0
        total_aset_tidak_lancar = 0
        
        # Aset Lancar - hanya tampilkan yang ada saldonya
        for akun in akun_aset_lancar:
            saldo = get_saldo_akun(akun)
            if saldo > 0:  # Aset harus positif
                aset_lancar_data.append({"Keterangan": akun, "Nilai (Rp)": saldo})
                total_aset_lancar += saldo
        
        # Aset Tidak Lancar - hanya tampilkan yang ada saldonya
        for akun in akun_aset_tidak_lancar:
            saldo = get_saldo_akun(akun)
            if saldo > 0:  # Aset harus positif
                aset_tidak_lancar_data.append({"Keterangan": akun, "Nilai (Rp)": saldo})
                total_aset_tidak_lancar += saldo
        
        # Kumpulkan data liabilitas dan ekuitas
        liabilitas_data = []
        ekuitas_data = []
        total_liabilitas = 0
        total_ekuitas = 0
        
        # Liabilitas - bisa positif atau negatif
        for akun in akun_liabilitas:
            saldo = get_saldo_akun(akun)
            if saldo != 0:
                # Liabilitas biasanya saldo kredit (negatif), tapi kita tampilkan sebagai positif
                nilai_liabilitas = abs(saldo) if saldo < 0 else saldo
                liabilitas_data.append({"Keterangan": akun, "Nilai (Rp)": nilai_liabilitas})
                total_liabilitas += nilai_liabilitas
        
        # Ekuitas - gunakan modal akhir dari laporan perubahan modal
        modal_akhir = getattr(st.session_state, 'modal_akhir', 0)
        laba_bersih = getattr(st.session_state, 'laba_bersih', 0)
        
        # Jika modal_akhir belum ada, hitung dari saldo akun Modal
        if modal_akhir == 0:
            modal_saldo = get_saldo_akun("Modal")
            # Modal biasanya kredit (negatif), jadi kita absolutkan
            modal_akhir = abs(modal_saldo) if modal_saldo < 0 else modal_saldo
        
        # Tambahkan modal ke ekuitas
        if modal_akhir != 0:
            ekuitas_data.append({"Keterangan": "Modal", "Nilai (Rp)": modal_akhir})
            total_ekuitas += modal_akhir
        
        # Tambahkan laba bersih ke ekuitas (sebagai Laba Ditahan)
        if laba_bersih != 0:
            ekuitas_data.append({"Keterangan": "Laba (Rugi) Ditahan", "Nilai (Rp)": laba_bersih})
            total_ekuitas += laba_bersih
        
        # Hitung total aset dan liabilitas + ekuitas
        total_aset = total_aset_lancar + total_aset_tidak_lancar
        total_liabilitas_ekuitas = total_liabilitas + total_ekuitas
        
        # VALIDASI KESEIMBANGAN - PERBAIKAN PENTING
        selisih = total_aset - total_liabilitas_ekuitas
        
        # Jika tidak balance, buat penyesuaian otomatis
        if abs(selisih) > 1:  # Toleransi 1 rupiah untuk rounding error
            st.warning(f"⚠️ Ditemukan ketidakseimbangan: Rp {selisih:,.0f}")
            
            # Buat akun penyesuaian otomatis
            if selisih > 0:
                # Aset > Liabilitas+Ekuitas, tambahkan ke Ekuitas (Laba Ditahan)
                ekuitas_data.append({"Keterangan": "Penyesuaian Modal", "Nilai (Rp)": selisih})
                total_ekuitas += selisih
                st.info(f"✅ Penyesuaian: Menambah Ekuitas sebesar Rp {selisih:,.0f}")
            else:
                # Aset < Liabilitas+Ekuitas, kurangi dari Ekuitas atau tambah ke Liabilitas
                ekuitas_data.append({"Keterangan": "Penyesuaian Modal", "Nilai (Rp)": selisih})
                total_ekuitas += selisih  # selisih negatif akan mengurangi
                st.info(f"✅ Penyesuaian: Mengurangi Ekuitas sebesar Rp {abs(selisih):,.0f}")
            
            # Recalculate total setelah penyesuaian
            total_liabilitas_ekuitas = total_liabilitas + total_ekuitas
        
        # Buat laporan posisi keuangan
        posisi_keuangan_data = []
        
        # Bagian Aset
        posisi_keuangan_data.append({"Keterangan": "**ASET**", "Nilai (Rp)": ""})
        
        # Aset Lancar
        if aset_lancar_data:
            posisi_keuangan_data.append({"Keterangan": "**Aset Lancar**", "Nilai (Rp)": ""})
            for item in aset_lancar_data:
                posisi_keuangan_data.append(item)
            posisi_keuangan_data.append({"Keterangan": "**Total Aset Lancar**", "Nilai (Rp)": total_aset_lancar})
        else:
            posisi_keuangan_data.append({"Keterangan": "**Aset Lancar**", "Nilai (Rp)": ""})
            posisi_keuangan_data.append({"Keterangan": "Tidak ada aset lancar", "Nilai (Rp)": ""})
            posisi_keuangan_data.append({"Keterangan": "**Total Aset Lancar**", "Nilai (Rp)": 0})
        
        # Aset Tidak Lancar
        if aset_tidak_lancar_data:
            posisi_keuangan_data.append({"Keterangan": "**Aset Tidak Lancar**", "Nilai (Rp)": ""})
            for item in aset_tidak_lancar_data:
                posisi_keuangan_data.append(item)
            posisi_keuangan_data.append({"Keterangan": "**Total Aset Tidak Lancar**", "Nilai (Rp)": total_aset_tidak_lancar})
        else:
            posisi_keuangan_data.append({"Keterangan": "**Aset Tidak Lancar**", "Nilai (Rp)": ""})
            posisi_keuangan_data.append({"Keterangan": "Tidak ada aset tidak lancar", "Nilai (Rp)": ""})
            posisi_keuangan_data.append({"Keterangan": "**Total Aset Tidak Lancar**", "Nilai (Rp)": 0})
        
        posisi_keuangan_data.append({"Keterangan": "**TOTAL ASET**", "Nilai (Rp)": total_aset})
        
        posisi_keuangan_data.append({"Keterangan": "", "Nilai (Rp)": ""})
        
        # Bagian Liabilitas dan Ekuitas
        posisi_keuangan_data.append({"Keterangan": "**LIABILITAS & EKUITAS**", "Nilai (Rp)": ""})
        
        # Liabilitas
        if liabilitas_data:
            posisi_keuangan_data.append({"Keterangan": "**Liabilitas**", "Nilai (Rp)": ""})
            for item in liabilitas_data:
                posisi_keuangan_data.append(item)
            posisi_keuangan_data.append({"Keterangan": "**Total Liabilitas**", "Nilai (Rp)": total_liabilitas})
        else:
            posisi_keuangan_data.append({"Keterangan": "**Liabilitas**", "Nilai (Rp)": ""})
            posisi_keuangan_data.append({"Keterangan": "Tidak ada liabilitas", "Nilai (Rp)": ""})
            posisi_keuangan_data.append({"Keterangan": "**Total Liabilitas**", "Nilai (Rp)": 0})
        
        # Ekuitas
        if ekuitas_data:
            posisi_keuangan_data.append({"Keterangan": "**Ekuitas**", "Nilai (Rp)": ""})
            for item in ekuitas_data:
                posisi_keuangan_data.append(item)
            posisi_keuangan_data.append({"Keterangan": "**Total Ekuitas**", "Nilai (Rp)": total_ekuitas})
        else:
            posisi_keuangan_data.append({"Keterangan": "**Ekuitas**", "Nilai (Rp)": ""})
            posisi_keuangan_data.append({"Keterangan": "Tidak ada ekuitas", "Nilai (Rp)": ""})
            posisi_keuangan_data.append({"Keterangan": "**Total Ekuitas**", "Nilai (Rp)": 0})
        
        total_liabilitas_ekuitas = total_liabilitas + total_ekuitas
        posisi_keuangan_data.append({"Keterangan": "**TOTAL LIABILITAS & EKUITAS**", "Nilai (Rp)": total_liabilitas_ekuitas})
        
        # Final validation
        final_selisih = abs(total_aset - total_liabilitas_ekuitas)
        if final_selisih <= 1:
            st.success("✅ Laporan Posisi Keuangan SEIMBANG")
        else:
            st.error(f"❌ Laporan Posisi Keuangan TIDAK SEIMBANG - Selisih: Rp {final_selisih:,.0f}")
        
        df_posisi_keuangan = pd.DataFrame(posisi_keuangan_data)
        st.session_state.df_laporan_posisi_keuangan = df_posisi_keuangan
        
        return df_posisi_keuangan
        
    except Exception as e:
        st.error(f"Error dalam hitung_posisi_keuangan_diperbaiki: {str(e)}")
        import traceback
        st.error(f"Detail error: {traceback.format_exc()}")
        return buat_posisi_keuangan_kosong()
    
def hitung_laba_rugi_diperbaiki():
    """Menghitung laba rugi dengan benar dan menyimpan hasilnya - VERSI DIPERBAIKI"""
    try:
        # Kumpulkan semua data transaksi dari berbagai sumber
        semua_transaksi = []
        
        # 1. Data dari jurnal umum format lama
        if "df_jurnal_umum_old_format" in st.session_state and not st.session_state.df_jurnal_umum_old_format.empty:
            semua_transaksi.append(st.session_state.df_jurnal_umum_old_format)
        
        # 2. Data dari jurnal penyesuaian (konversi ke format lama)
        if "df_jurnal_penyesuaian" in st.session_state and not st.session_state.df_jurnal_penyesuaian.empty:
            rows_penyesuaian = []
            for _, row in st.session_state.df_jurnal_penyesuaian.iterrows():
                # Entri debit dari penyesuaian
                if safe_float_convert(row["Debit (Rp)"]) > 0:
                    rows_penyesuaian.append({
                        "Tanggal": row["Tanggal"],
                        "Nama Akun": row["Akun Debit"],
                        "Debit (Rp)": safe_float_convert(row["Debit (Rp)"]),
                        "Kredit (Rp)": 0
                    })
                # Entri kredit dari penyesuaian
                if safe_float_convert(row["Kredit (Rp)"]) > 0:
                    rows_penyesuaian.append({
                        "Tanggal": row["Tanggal"],
                        "Nama Akun": row["Akun Kredit"],
                        "Debit (Rp)": 0,
                        "Kredit (Rp)": safe_float_convert(row["Kredit (Rp)"])
                    })
            if rows_penyesuaian:
                semua_transaksi.append(pd.DataFrame(rows_penyesuaian))
        
        # 3. Data dari jurnal penutup (konversi ke format lama)
        if "df_jurnal_penutup" in st.session_state and not st.session_state.df_jurnal_penutup.empty:
            rows_penutup = []
            for _, row in st.session_state.df_jurnal_penutup.iterrows():
                # Entri debit dari penutup
                if safe_float_convert(row["Debit (Rp)"]) > 0:
                    rows_penutup.append({
                        "Tanggal": row["Tanggal"],
                        "Nama Akun": row["Akun Debit"],
                        "Debit (Rp)": safe_float_convert(row["Debit (Rp)"]),
                        "Kredit (Rp)": 0
                    })
                # Entri kredit dari penutup
                if safe_float_convert(row["Kredit (Rp)"]) > 0:
                    rows_penutup.append({
                        "Tanggal": row["Tanggal"],
                        "Nama Akun": row["Akun Kredit"],
                        "Debit (Rp)": 0,
                        "Kredit (Rp)": safe_float_convert(row["Kredit (Rp)"])
                    })
            if rows_penutup:
                semua_transaksi.append(pd.DataFrame(rows_penutup))

        if not semua_transaksi:
            # Buat laporan laba rugi kosong
            laba_rugi_data = [
                {"Keterangan": "**PENDAPATAN**", "Nilai (Rp)": ""},
                {"Keterangan": "**Total Pendapatan**", "Nilai (Rp)": 0},
                {"Keterangan": "", "Nilai (Rp)": ""},
                {"Keterangan": "**BEBAN**", "Nilai (Rp)": ""},
                {"Keterangan": "**Total Beban**", "Nilai (Rp)": 0},
                {"Keterangan": "", "Nilai (Rp)": ""},
                {"Keterangan": "**LABA BERSIH**", "Nilai (Rp)": 0}
            ]
            df_laba_rugi = pd.DataFrame(laba_rugi_data)
            
            st.session_state.total_pendapatan = 0
            st.session_state.total_beban = 0
            st.session_state.laba_bersih = 0
            st.session_state.df_laporan_laba_rugi = df_laba_rugi
            
            return 0, 0, 0, df_laba_rugi

        # Gabungkan semua transaksi
        df_semua = pd.concat(semua_transaksi, ignore_index=True)
        
        # Pastikan kolom numerik bertipe float
        df_semua["Debit (Rp)"] = df_semua["Debit (Rp)"].apply(safe_float_convert)
        df_semua["Kredit (Rp)"] = df_semua["Kredit (Rp)"].apply(safe_float_convert)
        
        # KATEGORI AKUN UNTUK LABA RUGI - DIPERBARUI
        akun_pendapatan = [
            "Penjualan", 
            "Pendapatan Jasa", 
            "Pendapatan Lain",
            "Pendapatan"
        ]
        
        akun_beban = [
            "Beban Gaji", 
            "Beban Sewa", 
            "Beban Listrik dan Air", 
            "Beban Transportasi", 
            "Beban Lain-lain", 
            "Beban Asuransi",
            "Beban Penyusutan",
            "Harga Pokok Penjualan",
            "Beban listrik dan air",
            "Beban transportasi", 
            "Beban gaji",
            "Beban Lain"
        ]
        
        # Hitung total pendapatan (akun pendapatan di Kredit)
        pendapatan_data = df_semua[df_semua["Nama Akun"].isin(akun_pendapatan)]
        total_pendapatan = pendapatan_data["Kredit (Rp)"].sum() - pendapatan_data["Debit (Rp)"].sum()
        
        # Hitung total beban (akun beban di Debit)
        beban_data = df_semua[df_semua["Nama Akun"].isin(akun_beban)]
        total_beban = beban_data["Debit (Rp)"].sum() - beban_data["Kredit (Rp)"].sum()
        
        # Hitung laba bersih
        laba_bersih = total_pendapatan - total_beban
        
        # Buat laporan laba rugi dalam format yang rapi
        laba_rugi_data = []
        
        # Pendapatan
        laba_rugi_data.append({"Keterangan": "**PENDAPATAN**", "Nilai (Rp)": ""})
        for akun in akun_pendapatan:
            akun_data = df_semua[df_semua["Nama Akun"] == akun]
            if not akun_data.empty:
                total_akun = akun_data["Kredit (Rp)"].sum() - akun_data["Debit (Rp)"].sum()
                if total_akun != 0:
                    laba_rugi_data.append({"Keterangan": f"  {akun}", "Nilai (Rp)": total_akun})
        laba_rugi_data.append({"Keterangan": "**Total Pendapatan**", "Nilai (Rp)": total_pendapatan})
        
        laba_rugi_data.append({"Keterangan": "", "Nilai (Rp)": ""})
        
        # Beban
        laba_rugi_data.append({"Keterangan": "**BEBAN**", "Nilai (Rp)": ""})
        for akun in akun_beban:
            akun_data = df_semua[df_semua["Nama Akun"] == akun]
            if not akun_data.empty:
                total_akun = akun_data["Debit (Rp)"].sum() - akun_data["Kredit (Rp)"].sum()
                if total_akun != 0:
                    laba_rugi_data.append({"Keterangan": f"  {akun}", "Nilai (Rp)": total_akun})
        laba_rugi_data.append({"Keterangan": "**Total Beban**", "Nilai (Rp)": total_beban})
        
        laba_rugi_data.append({"Keterangan": "", "Nilai (Rp)": ""})
        laba_rugi_data.append({"Keterangan": "**LABA BERSIH**", "Nilai (Rp)": laba_bersih})
        
        df_laba_rugi = pd.DataFrame(laba_rugi_data)
        
        # Simpan ke session state
        st.session_state.total_pendapatan = total_pendapatan
        st.session_state.total_beban = total_beban
        st.session_state.laba_bersih = laba_bersih
        st.session_state.df_laporan_laba_rugi = df_laba_rugi
        
        return total_pendapatan, total_beban, laba_bersih, df_laba_rugi
        
    except Exception as e:
        st.error(f"Error dalam hitung_laba_rugi_diperbaiki: {str(e)}")
        import traceback
        st.error(f"Detail error: {traceback.format_exc()}")
        
        # Return default values in case of error
        laba_rugi_data = [
            {"Keterangan": "**PENDAPATAN**", "Nilai (Rp)": ""},
            {"Keterangan": "**Total Pendapatan**", "Nilai (Rp)": 0},
            {"Keterangan": "", "Nilai (Rp)": ""},
            {"Keterangan": "**BEBAN**", "Nilai (Rp)": ""},
            {"Keterangan": "**Total Beban**", "Nilai (Rp)": 0},
            {"Keterangan": "", "Nilai (Rp)": ""},
            {"Keterangan": "**LABA BERSIH**", "Nilai (Rp)": 0}
        ]
        df_laba_rugi = pd.DataFrame(laba_rugi_data)
        return 0, 0, 0, df_laba_rugi
    
    
# Tambahkan fungsi ini untuk mengintegrasikan semua laporan
def update_semua_laporan():
    """Memperbarui semua laporan keuangan secara berurutan"""
    try:
        # 1. Hitung Laba Rugi
        pendapatan, beban, laba_bersih, df_laba_rugi = hitung_laba_rugi_diperbaiki()
        
        # 2. Hitung modal awal (dari neraca saldo periode sebelumnya)
        modal_awal = 0
        if "df_neraca_saldo_periode_sebelumnya" in st.session_state and not st.session_state.df_neraca_saldo_periode_sebelumnya.empty:
            modal_data = st.session_state.df_neraca_saldo_periode_sebelumnya[
                st.session_state.df_neraca_saldo_periode_sebelumnya["Nama Akun"] == "Modal"
            ]
            if not modal_data.empty:
                modal_awal = modal_data["Debit (Rp)"].sum() - modal_data["Kredit (Rp)"].sum()
        
        # 3. Hitung Perubahan Modal
        df_perubahan_modal = hitung_perubahan_modal(laba_bersih, modal_awal)
        
        # 4. Hitung Posisi Keuangan
        if "df_buku_besar" in st.session_state and not st.session_state.df_buku_besar.empty:
            df_posisi_keuangan = hitung_posisi_keuangan_diperbaiki(st.session_state.df_buku_besar)
            st.session_state.df_laporan_posisi_keuangan = df_posisi_keuangan
        
        return True
        
    except Exception as e:
        st.error(f"Error dalam update_semua_laporan: {str(e)}")
        return False

def hitung_posisi_keuangan(df_buku_besar):
    """
    Fungsi untuk menghitung posisi keuangan - VERSI DIPERBAIKI
    """
    try:
        # PERBARUI KLASIFIKASI AKUN DENGAN AKUN BARU
        akun_aset_lancar = ["Kas", "Persediaan", "Perlengkapan", "Piutang"]
        akun_aset_tidak_lancar = ["Peralatan", "Aset biologis", "Kendaraan", "Tanah"]
        akun_liabilitas = ["Utang Gaji", "Utang Bank", "Utang Usaha"]
        akun_ekuitas = ["Modal"]
        
        # Validasi DataFrame
        if df_buku_besar.empty or "Nama Akun" not in df_buku_besar.columns:
            return pd.DataFrame(columns=["Nama Akun", "Kategori", "Saldo (Rp)"])
        
        def total_akun(akun_list, kategori):
            df_filtered = df_buku_besar[df_buku_besar["Nama Akun"].isin(akun_list)]
            if df_filtered.empty:
                return pd.DataFrame(columns=["Nama Akun", "Kategori", "Saldo (Rp)"])
            
            # Group by akun dan ambil saldo terakhir
            result = df_filtered.groupby("Nama Akun").agg({
                "Saldo (Rp)": "last"
            }).reset_index()
            result["Kategori"] = kategori
            return result
        
        # Hitung setiap kategori
        aset_lancar = total_akun(akun_aset_lancar, "Aset Lancar")
        aset_tidak_lancar = total_akun(akun_aset_tidak_lancar, "Aset Tidak Lancar")
        liabilitas = total_akun(akun_liabilitas, "Liabilitas")
        ekuitas = total_akun(akun_ekuitas, "Ekuitas")
        
        # Gabungkan semua kategori
        posisi = pd.concat([aset_lancar, aset_tidak_lancar, liabilitas, ekuitas], ignore_index=True)
        
        # Hitung total untuk setiap kategori
        kategori_totals = []
        for kategori in ["Aset Lancar", "Aset Tidak Lancar", "Liabilitas", "Ekuitas"]:
            total_kategori = posisi[posisi["Kategori"] == kategori]["Saldo (Rp)"].sum()
            kategori_totals.append({
                "Nama Akun": f"Total {kategori}",
                "Kategori": kategori,
                "Saldo (Rp)": total_kategori
            })
        
        # Tambahkan baris total
        posisi_dengan_total = pd.concat([posisi, pd.DataFrame(kategori_totals)], ignore_index=True)
        
        # Hitung total aset dan total liabilitas + ekuitas
        total_aset = posisi_dengan_total[
            posisi_dengan_total["Kategori"].isin(["Aset Lancar", "Aset Tidak Lancar"])
        ]["Saldo (Rp)"].sum()
        
        total_liabilitas_ekuitas = posisi_dengan_total[
            posisi_dengan_total["Kategori"].isin(["Liabilitas", "Ekuitas"])
        ]["Saldo (Rp)"].sum()
        
        # Tambahkan baris grand total
        grand_totals = [
            {
                "Nama Akun": "TOTAL ASET",
                "Kategori": "Total",
                "Saldo (Rp)": total_aset
            },
            {
                "Nama Akun": "TOTAL LIABILITAS & EKUITAS", 
                "Kategori": "Total",
                "Saldo (Rp)": total_liabilitas_ekuitas
            }
        ]
        
        posisi_final = pd.concat([posisi_dengan_total, pd.DataFrame(grand_totals)], ignore_index=True)
        return posisi_final
        
    except Exception as e:
        st.error(f"Error dalam hitung_posisi_keuangan: {str(e)}")
        return pd.DataFrame(columns=["Nama Akun", "Kategori", "Saldo (Rp)"])
    
    
# Ganti fungsi yang lama dengan yang baru di aplikasi utama
def update_semua_laporan_keuangan():
    """Memperbarui semua laporan keuangan secara berurutan - VERSI DIPERBAIKI"""
    try:
        with st.spinner("Memperbarui laporan keuangan..."):
            # 1. Update buku besar dengan saldo awal
            update_buku_besar_per_akun_dengan_saldo_awal()
            
            # 2. Hitung Laba Rugi
            pendapatan, beban, laba_bersih, df_laba_rugi = hitung_laba_rugi_diperbaiki()
            
            # 3. Hitung Perubahan Modal
            df_perubahan_modal = hitung_perubahan_modal_diperbaiki(laba_bersih)
            
            # 4. Hitung Posisi Keuangan (yang selalu seimbang)
            df_posisi_keuangan = hitung_posisi_keuangan_selalu_seimbang()
            
            # Simpan timestamp update
            st.session_state.last_report_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return True
            
    except Exception as e:
        st.error(f"Error dalam update_semua_laporan_keuangan: {str(e)}")
        return False

# Panggil inisialisasi di awal
init_sistem_periode()
    
def tampilkan_laporan_laba_rugi():
    """Menampilkan laporan laba rugi dengan format yang rapi"""
    st.subheader('📊 Laporan Laba Rugi')
    st.markdown(f"**Periode:** {st.session_state.periode_sekarang}")
    
    # Tombol untuk memperbarui laporan
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Perbarui Laporan", key="update_laba_rugi"):
            update_semua_laporan_keuangan()
            st.rerun()
    
    # Hitung dan tampilkan laporan laba rugi
    pendapatan, beban, laba_bersih, df_laba_rugi = hitung_laba_rugi_diperbaiki()
    
    if not df_laba_rugi.empty:
        # Tampilkan dalam format yang rapi
        st.write("### Laporan Laba Rugi")
        
        # Buat container untuk tampilan yang lebih baik
        with st.container():
            for _, row in df_laba_rugi.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    keterangan = row["Keterangan"]
                    if "**" in keterangan:
                        st.markdown(f"**{keterangan.replace('**', '')}**")
                    else:
                        st.write(keterangan)
                with col2:
                    nilai = row["Nilai (Rp)"]
                    if pd.notna(nilai) and nilai != "":
                        if "**" in row["Keterangan"]:
                            if isinstance(nilai, (int, float)):
                                st.markdown(f"**Rp {nilai:,.0f}**")
                            else:
                                st.markdown(f"**{nilai}**")
                        else:
                            if isinstance(nilai, (int, float)):
                                st.write(f"Rp {nilai:,.0f}")
                            else:
                                st.write(nilai)
                    else:
                        st.write("")
        
        # Tampilkan summary metrics
        st.write("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Pendapatan", f"Rp {pendapatan:,.0f}")
        with col2:
            st.metric("Total Beban", f"Rp {beban:,.0f}")
        with col3:
            warna = "normal" if laba_bersih >= 0 else "inverse"
            st.metric("Laba (Rugi) Bersih", f"Rp {laba_bersih:,.0f}", delta=None, delta_color=warna)
        
        # Tampilkan status
        if laba_bersih > 0:
            st.success(f"✅ Perusahaan mengalami **LABA** sebesar Rp {laba_bersih:,.0f}")
        elif laba_bersih < 0:
            st.error(f"❌ Perusahaan mengalami **RUGI** sebesar Rp {abs(laba_bersih):,.0f}")
        else:
            st.info("ℹ️ Perusahaan **BREAK EVEN** (Tidak laba tidak rugi)")
    
    else:
        st.info("""
        **Belum ada data untuk laporan laba rugi.**
        
        **Untuk membuat laporan laba rugi:**
        1. Pastikan sudah ada transaksi di **Jurnal Umum**
        2. Jika diperlukan, buat penyesuaian di **Jurnal Penyesuaian**
        3. Pastikan ada transaksi yang mempengaruhi akun pendapatan dan beban
        4. Klik tombol **'Perbarui Laporan'** di atas
        """)
        
        with st.expander("🔍 Daftar Akun Pendapatan dan Beban yang Diakui"):
            st.write("""
            **Akun Pendapatan:**
            - Penjualan
            - Pendapatan Jasa  
            - Pendapatan Lain
            - Pendapatan
            
            **Akun Beban:**
            - Beban Gaji
            - Beban Sewa
            - Beban Listrik dan Air
            - Beban Transportasi
            - Beban Lain-lain
            - Beban Asuransi
            - Beban Penyusutan
            - Harga Pokok Penjualan
            - Beban listrik dan air
            - Beban transportasi
            - Beban gaji
            - Beban Lain
            """)
            
            
def tampilkan_laporan_perubahan_modal():
    """Menampilkan laporan perubahan modal dengan format yang rapi"""
    st.subheader('📈 Laporan Perubahan Modal')
    st.markdown(f"**Periode:** {st.session_state.periode_sekarang}")
    
    # Pastikan laba rugi sudah dihitung
    if "laba_bersih" not in st.session_state:
        hitung_laba_rugi_diperbaiki()
    
    # Tombol perbarui
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Perbarui Laporan", key="update_perubahan_modal"):
            update_semua_laporan_keuangan()
            st.rerun()
    
    # Hitung dan tampilkan laporan perubahan modal
    df_perubahan_modal = hitung_perubahan_modal_diperbaiki(st.session_state.get("laba_bersih", 0))
    
    if not df_perubahan_modal.empty:
        st.write("### Laporan Perubahan Modal")
        
        # Tampilkan dalam format yang rapi
        with st.container():
            for _, row in df_perubahan_modal.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    keterangan = row["Keterangan"]
                    if "**" in keterangan:
                        st.markdown(f"**{keterangan.replace('**', '')}**")
                    else:
                        st.write(keterangan)
                with col2:
                    nilai = row["Nilai (Rp)"]
                    if "**" in row["Keterangan"]:
                        st.markdown(f"**Rp {nilai:,.0f}**")
                    else:
                        st.write(f"Rp {nilai:,.0f}")
        
        # Informasi tambahan
        st.write("---")
        st.info(f"""
        **Ringkasan Perubahan Modal:**
        - **Modal Awal:** Rp {st.session_state.get('modal_awal', 0):,.0f}
        - **Laba/Rugi Bersih:** Rp {st.session_state.get('laba_bersih', 0):,.0f}
        - **Modal Akhir:** Rp {st.session_state.get('modal_akhir', 0):,.0f}
        
        **Kenaikan/penurunan modal:** {((st.session_state.get('modal_akhir', 0) / max(1, st.session_state.get('modal_awal', 1)) - 1) * 100):.1f}%
        """)
    
    else:
        st.info("""
        **Belum ada data untuk laporan perubahan modal.**
        
        **Pastikan:**
        1. Sudah ada data **Laporan Laba Rugi**
        2. Ada data **Modal Awal** dari neraca saldo periode sebelumnya
        3. Jika ini periode pertama, isi neraca saldo periode sebelumnya terlebih dahulu
        """)
        
        
def tampilkan_laporan_posisi_keuangan():
    """Menampilkan laporan posisi keuangan dengan format yang rapi"""
    st.subheader('🏦 Laporan Posisi Keuangan (Neraca)')
    st.markdown(f"**Periode:** {st.session_state.periode_sekarang}")
    
    # Tombol perbarui
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Perbarui Laporan", key="update_posisi_keuangan"):
            update_semua_laporan_keuangan()
            st.rerun()
    
    # Perbarui semua laporan terlebih dahulu
    update_semua_laporan_keuangan()
    
    # Tampilkan laporan posisi keuangan
    df_posisi_keuangan = hitung_posisi_keuangan_diperbaiki()
    
    if not df_posisi_keuangan.empty:
        st.write("### Laporan Posisi Keuangan")
        
        # Tampilkan dalam format yang rapi
        with st.container():
            for _, row in df_posisi_keuangan.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    keterangan = row["Keterangan"]
                    if "**" in keterangan:
                        st.markdown(f"**{keterangan.replace('**', '')}**")
                    else:
                        st.write(keterangan)
                with col2:
                    if pd.notna(row["Nilai (Rp)"]) and row["Nilai (Rp)"] != "":
                        nilai = row["Nilai (Rp)"]
                        if "**" in row["Keterangan"]:
                            if isinstance(nilai, (int, float)):
                                st.markdown(f"**Rp {nilai:,.0f}**")
                            else:
                                st.markdown(f"**{nilai}**")
                        else:
                            if isinstance(nilai, (int, float)):
                                st.write(f"Rp {nilai:,.0f}")
                            else:
                                st.write(nilai)
                    else:
                        st.write("")
        
        # Validasi keseimbangan
        total_aset = 0
        total_liabilitas_ekuitas = 0
        
        # Hitung total dari data
        for _, row in df_posisi_keuangan.iterrows():
            if row["Keterangan"] == "**TOTAL ASET**" and pd.notna(row["Nilai (Rp)"]):
                total_aset = safe_float_convert(row["Nilai (Rp)"])
            elif row["Keterangan"] == "**TOTAL LIABILITAS & EKUITAS**" and pd.notna(row["Nilai (Rp)"]):
                total_liabilitas_ekuitas = safe_float_convert(row["Nilai (Rp)"])
        
        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Aset", f"Rp {total_aset:,.0f}")
        with col2:
            st.metric("Total Liabilitas & Ekuitas", f"Rp {total_liabilitas_ekuitas:,.0f}")
        
        # Cek keseimbangan
        selisih = abs(total_aset - total_liabilitas_ekuitas)
        if selisih < 1:
            st.success("✅ Neraca SEIMBANG - Aset = Liabilitas + Ekuitas")
        else:
            st.error(f"❌ Neraca TIDAK SEIMBANG - Selisih: Rp {selisih:,.0f}")
            
            # Saran perbaikan
            with st.expander("💡 Saran Perbaikan Keseimbangan Neraca"):
                st.write(f"""
                **Analisis Ketidakseimbangan:**
                - Total Aset: Rp {total_aset:,.0f}
                - Total Liabilitas & Ekuitas: Rp {total_liabilitas_ekuitas:,.0f}
                - **Selisih: Rp {selisih:,.0f}**
                
                **Kemungkinan penyebab:**
                1. Transaksi yang tidak seimbang di Jurnal Umum
                2. Penyesuaian yang belum dilakukan
                3. Kesalahan input data
                4. Akun yang belum terklasifikasi dengan benar
                
                **Tindakan perbaikan:**
                - Periksa kembali transaksi di **Jurnal Umum**
                - Pastikan semua penyesuaian sudah dicatat di **Jurnal Penyesuaian**
                - Validasi data di **Buku Besar**
                """)
    
    else:
        st.info("""
        **Belum ada data untuk laporan posisi keuangan.**
        
        **Untuk membuat laporan posisi keuangan:**
        1. Pastikan sudah ada transaksi yang mempengaruhi aset, liabilitas, dan ekuitas
        2. Pastikan **Buku Besar** sudah terisi
        3. Pastikan **Laporan Laba Rugi** sudah ada
        4. Klik tombol **'Perbarui Laporan'** di atas
        """)
    
    
def cek_stok_barang(barang):
    """Mengecek stok barang yang tersedia"""
    try:
        if "df_persediaan" in st.session_state and not st.session_state.df_persediaan.empty:
            barang_data = st.session_state.df_persediaan[st.session_state.df_persediaan["Barang"] == barang]
            if not barang_data.empty:
                return barang_data["Stok Akhir"].iloc[0]
        return 0
    except:
        return 0
    
def tambah_penjualan_ke_jurnal_umum(tanggal, keterangan, akun_debit, total_penjualan, total_hpp):
    """Menambahkan penjualan ke jurnal umum dengan 4 entri"""
    try:
        if "df_jurnal_umum" not in st.session_state:
            st.session_state.df_jurnal_umum = pd.DataFrame(
                columns=["No", "Tanggal", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"]
            )
        
        # Gunakan nomor transaksi yang sama untuk keempat entri
        nomor_transaksi = st.session_state.transaction_counter
        
        # Entri 1: Debit Kas/Piutang
        entri1 = {
            "No": nomor_transaksi,
            "Tanggal": tanggal,
            "Akun Debit": akun_debit,
            "Debit (Rp)": total_penjualan,
            "Akun Kredit": "",
            "Kredit (Rp)": 0
        }
        
        # Entri 2: Kredit Penjualan
        entri2 = {
            "No": nomor_transaksi,
            "Tanggal": tanggal,
            "Akun Debit": "",
            "Debit (Rp)": 0,
            "Akun Kredit": "Penjualan",
            "Kredit (Rp)": total_penjualan
        }
        
        # Entri 3: Debit Harga Pokok Penjualan
        entri3 = {
            "No": nomor_transaksi,
            "Tanggal": tanggal,
            "Akun Debit": "Harga Pokok Penjualan",
            "Debit (Rp)": total_hpp,
            "Akun Kredit": "",
            "Kredit (Rp)": 0
        }
        
        # Entri 4: Kredit Persediaan
        entri4 = {
            "No": nomor_transaksi,
            "Tanggal": tanggal,
            "Akun Debit": "",
            "Debit (Rp)": 0,
            "Akun Kredit": "Persediaan Barang Dagang",
            "Kredit (Rp)": total_hpp
        }
        
        # Tambahkan semua entri
        new_entries = pd.DataFrame([entri1, entri2, entri3, entri4])
        st.session_state.df_jurnal_umum = pd.concat([
            st.session_state.df_jurnal_umum,
            new_entries
        ], ignore_index=True)
        
        # Increment transaction counter
        st.session_state.transaction_counter += 1
        
        # Update sistem
        update_sistem_dengan_struktur_baru()
        auto_save()
        
        return True
        
    except Exception as e:
        st.error(f"Error tambah penjualan ke jurnal: {str(e)}")
        return False


def tambah_pembelian_ke_jurnal_umum_diperbaiki(tanggal, barang, total_pembelian, akun_kredit="Kas"):
    """Menambahkan pembelian ke jurnal umum - VERSI DIPERBAIKI"""
    try:
        if "df_jurnal_umum" not in st.session_state:
            st.session_state.df_jurnal_umum = pd.DataFrame(
                columns=["No", "Tanggal", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"]
            )
        
        # Gunakan nomor transaksi yang sama untuk kedua entri
        nomor_transaksi = st.session_state.transaction_counter
        
        # Validasi input - PERBAIKAN: Pastikan total_pembelian tidak 0
        total_pembelian_float = safe_float_convert(total_pembelian)
        if total_pembelian_float <= 0:
            st.error(f"Total pembelian harus lebih dari 0. Nilai: {total_pembelian}")
            return False
        
        # PERBAIKAN: Gunakan akun "Persediaan" bukan "Persediaan Barang Dagang"
        # Entri 1: Debit Persediaan
        entri1 = {
            "No": nomor_transaksi,
            "Tanggal": tanggal,
            "Akun Debit": "Persediaan",  # PERBAIKAN: Ganti nama akun
            "Debit (Rp)": total_pembelian_float,
            "Akun Kredit": "",
            "Kredit (Rp)": 0.0
        }
        
        # Entri 2: Kredit Kas/Utang
        entri2 = {
            "No": nomor_transaksi,
            "Tanggal": tanggal,
            "Akun Debit": "",
            "Debit (Rp)": 0.0,
            "Akun Kredit": akun_kredit,
            "Kredit (Rp)": total_pembelian_float
        }
        
        # Tambahkan kedua entri dengan NOMOR YANG SAMA
        new_entries = pd.DataFrame([entri1, entri2])
        st.session_state.df_jurnal_umum = pd.concat([
            st.session_state.df_jurnal_umum,
            new_entries
        ], ignore_index=True)
        
        # Increment transaction counter HANYA SEKALI
        st.session_state.transaction_counter += 1
        
        # Update sistem
        update_sistem_dengan_struktur_baru()
        auto_save()
        
        st.success(f"✅ Pembelian berhasil dicatat! (No Transaksi: {nomor_transaksi})")
        return True
        
    except Exception as e:
        st.error(f"Error tambah pembelian ke jurnal: {str(e)}")
        return False
    
def proses_pembelian_diperbaiki(tanggal_pembelian, barang_pembelian, jumlah_pembelian, harga_beli, akun_kredit_pembelian, keterangan_pembelian):
    """Memproses pembelian dengan integrasi yang lebih baik - VERSI DIPERBAIKI"""
    try:
        total_pembelian = jumlah_pembelian * harga_beli
        
        # Validasi total pembelian
        if total_pembelian <= 0:
            st.error("Total pembelian harus lebih dari 0")
            return False
        
        # 1. Tambahkan ke jurnal umum - gunakan fungsi yang diperbaiki
        success_jurnal = tambah_pembelian_ke_jurnal_umum_diperbaiki(
            tanggal_pembelian, 
            barang_pembelian, 
            total_pembelian,
            akun_kredit_pembelian
        )
        
        if success_jurnal:
            # 2. Update persediaan
            success_persediaan = update_persediaan_setelah_pembelian_diperbaiki(
                barang_pembelian, 
                jumlah_pembelian, 
                harga_beli, 
                tanggal_pembelian, 
                keterangan_pembelian
            )
            
            if success_persediaan:
                # 3. Tambahkan ke dataframe pembelian
                new_entry = {
                    "No": len(st.session_state.df_pembelian) + 1,
                    "Tanggal": tanggal_pembelian,
                    "Keterangan": keterangan_pembelian,
                    "Barang": barang_pembelian,
                    "Jumlah": jumlah_pembelian,
                    "Harga Beli": harga_beli,
                    "Total Pembelian": total_pembelian
                }
                
                st.session_state.df_pembelian = pd.concat([
                    st.session_state.df_pembelian,
                    pd.DataFrame([new_entry])
                ], ignore_index=True)
                
                st.success("✅ Pembelian berhasil dicatat dan persediaan diperbarui!")
                return True
            else:
                st.error("Gagal update persediaan")
                return False
        else:
            st.error("Gagal mencatat jurnal pembelian")
            return False
            
    except Exception as e:
        st.error(f"Error dalam proses pembelian: {str(e)}")
        return False

def update_persediaan_setelah_penjualan(barang, jumlah, hpp_per_unit, tanggal, keterangan):
    """Update persediaan setelah penjualan dengan metode average"""
    try:
        if "df_persediaan" not in st.session_state or st.session_state.df_persediaan.empty:
            return False
        
        # Cari index barang
        barang_index = st.session_state.df_persediaan[st.session_state.df_persediaan["Barang"] == barang].index
        
        if len(barang_index) > 0:
            idx = barang_index[0]
            
            # Update penjualan
            st.session_state.df_persediaan.at[idx, "Penjualan"] += jumlah
            
            # Update stok akhir
            stok_awal = st.session_state.df_persediaan.at[idx, "Stok Awal"]
            pembelian = st.session_state.df_persediaan.at[idx, "Pembelian"]
            penjualan = st.session_state.df_persediaan.at[idx, "Penjualan"]
            st.session_state.df_persediaan.at[idx, "Stok Akhir"] = stok_awal + pembelian - penjualan
            
            # Update total nilai (stok akhir * harga rata-rata)
            stok_akhir = st.session_state.df_persediaan.at[idx, "Stok Akhir"]
            harga_rata = st.session_state.df_persediaan.at[idx, "Harga Rata-rata"]
            st.session_state.df_persediaan.at[idx, "Total Nilai"] = stok_akhir * harga_rata
            
            # Tambahkan ke riwayat persediaan
            tambah_riwayat_persediaan(
                tanggal, "Penjualan", barang, -jumlah, hpp_per_unit, 
                -jumlah * hpp_per_unit, stok_akhir, keterangan
            )
            
            auto_save()
            return True
        return False
        
    except Exception as e:
        st.error(f"Error update persediaan penjualan: {str(e)}")
        return False

def update_persediaan_setelah_pembelian(barang, jumlah, harga_beli, tanggal, keterangan):
    """Update persediaan setelah pembelian dengan metode average - VERSI DIPERBAIKI"""
    try:
        if "df_persediaan" not in st.session_state or st.session_state.df_persediaan.empty:
            # Jika belum ada data persediaan, inisialisasi
            st.session_state.df_persediaan = pd.DataFrame({
                "Barang": ["Ayam Jago", "Ayam Broiler", "Telur Ayam"],
                "Stok Awal": [0, 0, 0],
                "Pembelian": [0, 0, 0],
                "Penjualan": [0, 0, 0],
                "Stok Akhir": [0, 0, 0],
                "Harga Rata-rata": [0, 0, 0],
                "Total Nilai": [0, 0, 0]
            })
        
        # Cari index barang
        barang_index = st.session_state.df_persediaan[st.session_state.df_persediaan["Barang"] == barang].index
        
        if len(barang_index) > 0:
            idx = barang_index[0]
            
            # Data lama
            stok_awal = st.session_state.df_persediaan.at[idx, "Stok Awal"]
            pembelian_lama = st.session_state.df_persediaan.at[idx, "Pembelian"]
            penjualan_lama = st.session_state.df_persediaan.at[idx, "Penjualan"]
            harga_rata_lama = st.session_state.df_persediaan.at[idx, "Harga Rata-rata"]
            total_nilai_lama = st.session_state.df_persediaan.at[idx, "Total Nilai"]
            
            # Hitung harga rata-rata baru
            total_unit_baru = (stok_awal + pembelian_lama - penjualan_lama) + jumlah
            total_nilai_baru = total_nilai_lama + (jumlah * harga_beli)
            harga_rata_baru = total_nilai_baru / total_unit_baru if total_unit_baru > 0 else harga_beli
            
            # Update nilai
            st.session_state.df_persediaan.at[idx, "Pembelian"] += jumlah
            st.session_state.df_persediaan.at[idx, "Stok Akhir"] = total_unit_baru
            st.session_state.df_persediaan.at[idx, "Harga Rata-rata"] = harga_rata_baru
            st.session_state.df_persediaan.at[idx, "Total Nilai"] = total_nilai_baru
            
            # Tambahkan ke riwayat persediaan
            tambah_riwayat_persediaan(
                tanggal, "Pembelian", barang, jumlah, harga_beli, 
                jumlah * harga_beli, total_unit_baru, keterangan
            )
            
            auto_save()
            return True
        return False
        
    except Exception as e:
        st.error(f"Error update persediaan pembelian: {str(e)}")
        return False
    
    
def tambah_riwayat_persediaan_diperbaiki(tanggal, jenis, barang, jumlah, harga, total, stok, keterangan):
    """Menambah riwayat pergerakan persediaan - VERSI DIPERBAIKI"""
    try:
        if "df_riwayat_persediaan" not in st.session_state:
            st.session_state.df_riwayat_persediaan = pd.DataFrame(
                columns=["Tanggal", "Jenis", "Barang", "Jumlah", "Harga", "Total", "Stok", "Keterangan"]
            )
        
        new_row = {
            "Tanggal": tanggal,
            "Jenis": jenis,
            "Barang": barang,
            "Jumlah": jumlah,
            "Harga": harga,
            "Total": total,
            "Stok": stok,
            "Keterangan": keterangan
        }
        
        st.session_state.df_riwayat_persediaan = pd.concat([
            st.session_state.df_riwayat_persediaan,
            pd.DataFrame([new_row])
        ], ignore_index=True)
        
        return True
    except Exception as e:
        print(f"Error tambah riwayat persediaan: {str(e)}")
        return False
    
    
def update_persediaan_setelah_pembelian_diperbaiki(barang, jumlah, harga_beli, tanggal, keterangan):
    """Update persediaan setelah pembelian dengan metode average - VERSI DIPERBAIKI"""
    try:
        if "df_persediaan" not in st.session_state or st.session_state.df_persediaan.empty:
            # Jika belum ada data persediaan, inisialisasi
            st.session_state.df_persediaan = pd.DataFrame({
                "Barang": ["Ayam Jago", "Ayam Broiler", "Telur Ayam"],
                "Stok Awal": [0, 0, 0],
                "Pembelian": [0, 0, 0],
                "Penjualan": [0, 0, 0],
                "Stok Akhir": [0, 0, 0],
                "Harga Rata-rata": [0, 0, 0],
                "Total Nilai": [0, 0, 0]
            })
        
        # Cari index barang
        barang_index = st.session_state.df_persediaan[st.session_state.df_persediaan["Barang"] == barang].index
        
        if len(barang_index) > 0:
            idx = barang_index[0]
            
            # Data lama
            stok_awal = safe_float_convert(st.session_state.df_persediaan.at[idx, "Stok Awal"])
            pembelian_lama = safe_float_convert(st.session_state.df_persediaan.at[idx, "Pembelian"])
            penjualan_lama = safe_float_convert(st.session_state.df_persediaan.at[idx, "Penjualan"])
            harga_rata_lama = safe_float_convert(st.session_state.df_persediaan.at[idx, "Harga Rata-rata"])
            total_nilai_lama = safe_float_convert(st.session_state.df_persediaan.at[idx, "Total Nilai"])
            
            # Hitung stok sebelum pembelian
            stok_sebelum = stok_awal + pembelian_lama - penjualan_lama
            
            # Hitung harga rata-rata baru
            total_unit_baru = stok_sebelum + jumlah
            total_nilai_baru = total_nilai_lama + (jumlah * harga_beli)
            harga_rata_baru = total_nilai_baru / total_unit_baru if total_unit_baru > 0 else harga_beli
            
            # Update nilai
            st.session_state.df_persediaan.at[idx, "Pembelian"] = pembelian_lama + jumlah
            st.session_state.df_persediaan.at[idx, "Stok Akhir"] = total_unit_baru
            st.session_state.df_persediaan.at[idx, "Harga Rata-rata"] = harga_rata_baru
            st.session_state.df_persediaan.at[idx, "Total Nilai"] = total_nilai_baru
            
            # Tambahkan ke riwayat persediaan
            tambah_riwayat_persediaan_diperbaiki(
                tanggal, "Pembelian", barang, jumlah, harga_beli, 
                jumlah * harga_beli, total_unit_baru, keterangan
            )
            
            auto_save()
            return True
        return False
        
    except Exception as e:
        st.error(f"Error update persediaan pembelian: {str(e)}")
        return False
    
    
def display_kartu_persediaan_single_barang(barang):
    """Menampilkan kartu persediaan untuk satu barang tertentu"""
    
    # Data persediaan barang
    barang_data = st.session_state.df_persediaan[st.session_state.df_persediaan["Barang"] == barang]
    
    if not barang_data.empty:
        stok_akhir = barang_data["Stok Akhir"].iloc[0]
        harga_rata = barang_data["Harga Rata-rata"].iloc[0]
        total_nilai = barang_data["Total Nilai"].iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Stok Akhir", f"{stok_akhir:,.0f} unit")
        with col2:
            st.metric("Harga Rata-rata", f"Rp {harga_rata:,.0f}")
        with col3:
            st.metric("Total Nilai", f"Rp {total_nilai:,.0f}")
        with col4:
            status = "Tersedia" if stok_akhir > 0 else "Habis"
            st.metric("Status", status)
    
    # Riwayat pembelian untuk barang ini
    st.write("#### 🛒 Riwayat Pembelian")
    if "df_pembelian" in st.session_state and not st.session_state.df_pembelian.empty:
        pembelian_barang = st.session_state.df_pembelian[st.session_state.df_pembelian["Barang"] == barang]
        if not pembelian_barang.empty:
            # Format untuk tampilan
            df_tampil = pembelian_barang.copy()
            df_tampil["Harga Beli"] = df_tampil["Harga Beli"].apply(lambda x: f"Rp {x:,.0f}")
            df_tampil["Total Pembelian"] = df_tampil["Total Pembelian"].apply(lambda x: f"Rp {x:,.0f}")
            
            st.dataframe(df_tampil[["Tanggal", "Keterangan", "Jumlah", "Harga Beli", "Total Pembelian"]], 
                        use_container_width=True, hide_index=True)
            
            # Total pembelian
            total_pembelian = pembelian_barang["Total Pembelian"].sum()
            st.metric("Total Pembelian", f"Rp {total_pembelian:,.0f}")
        else:
            st.info("Belum ada data pembelian untuk barang ini.")
    else:
        st.info("Belum ada data pembelian.")
    
    # Riwayat penjualan untuk barang ini
    st.write("#### 📦 Riwayat Penjualan")
    if "df_penjualan" in st.session_state and not st.session_state.df_penjualan.empty:
        penjualan_barang = st.session_state.df_penjualan[st.session_state.df_penjualan["Barang"] == barang]
        if not penjualan_barang.empty:
            # Format untuk tampilan
            df_tampil = penjualan_barang.copy()
            df_tampil["Harga Jual"] = df_tampil["Harga Jual"].apply(lambda x: f"Rp {x:,.0f}")
            df_tampil["Total Penjualan"] = df_tampil["Total Penjualan"].apply(lambda x: f"Rp {x:,.0f}")
            df_tampil["HPP"] = df_tampil["HPP"].apply(lambda x: f"Rp {x:,.0f}")
            df_tampil["Total HPP"] = df_tampil["Total HPP"].apply(lambda x: f"Rp {x:,.0f}")
            
            st.dataframe(df_tampil[["Tanggal", "Keterangan", "Jumlah", "Harga Jual", "Total Penjualan", "HPP", "Total HPP"]], 
                        use_container_width=True, hide_index=True)
            
            # Total penjualan dan laba
            total_penjualan = penjualan_barang["Total Penjualan"].sum()
            total_hpp = penjualan_barang["Total HPP"].sum()
            laba_kotor = total_penjualan - total_hpp
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Penjualan", f"Rp {total_penjualan:,.0f}")
            with col2:
                st.metric("Total HPP", f"Rp {total_hpp:,.0f}")
            with col3:
                st.metric("Laba Kotor", f"Rp {laba_kotor:,.0f}")
        else:
            st.info("Belum ada data penjualan untuk barang ini.")
    else:
        st.info("Belum ada data penjualan.")
    
    # Riwayat persediaan untuk barang ini
    st.write("#### 📊 Riwayat Pergerakan Persediaan")
    if "df_riwayat_persediaan" in st.session_state and not st.session_state.df_riwayat_persediaan.empty:
        riwayat_barang = st.session_state.df_riwayat_persediaan[st.session_state.df_riwayat_persediaan["Barang"] == barang]
        if not riwayat_barang.empty:
            # Format untuk tampilan
            df_tampil = riwayat_barang.copy()
            df_tampil["Harga"] = df_tampil["Harga"].apply(lambda x: f"Rp {x:,.0f}")
            df_tampil["Total"] = df_tampil["Total"].apply(lambda x: f"Rp {x:,.0f}")
            
            # Urutkan berdasarkan tanggal
            df_tampil = df_tampil.sort_values("Tanggal", ascending=False)
            
            st.dataframe(df_tampil[["Tanggal", "Jenis", "Jumlah", "Harga", "Total", "Stok", "Keterangan"]], 
                        use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada riwayat pergerakan persediaan untuk barang ini.")
    else:
        st.info("Belum ada riwayat persediaan.")
        
        
    
def display_kartu_persediaan_per_barang():
    """Menampilkan kartu persediaan dengan tabel terpisah untuk setiap barang"""
    st.subheader("📦 Kartu Persediaan - Per Barang")
    
    # Inisialisasi jika belum ada
    if "df_persediaan" not in st.session_state:
        st.session_state.df_persediaan = pd.DataFrame({
            "Barang": ["Ayam Jago", "Ayam Broiler", "Telur Ayam"],
            "Stok Awal": [0, 0, 0],
            "Pembelian": [0, 0, 0],
            "Penjualan": [0, 0, 0],
            "Stok Akhir": [0, 0, 0],
            "Harga Rata-rata": [0, 0, 0],
            "Total Nilai": [0, 0, 0]
        })
    
    # Tampilkan ringkasan persediaan
    st.write("### 📊 Ringkasan Persediaan")
    if not st.session_state.df_persediaan.empty:
        total_nilai = st.session_state.df_persediaan["Total Nilai"].sum()
        total_stok = st.session_state.df_persediaan["Stok Akhir"].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Nilai Persediaan", f"Rp {total_nilai:,.0f}")
        with col2:
            st.metric("Total Stok Semua Barang", f"{total_stok:,.0f} unit")
        
        st.dataframe(st.session_state.df_persediaan, use_container_width=True)
    
    # Tampilkan detail per barang
    st.write("### 📋 Detail Per Barang")
    
    # Daftar barang yang tersedia
    barang_list = st.session_state.df_persediaan["Barang"].tolist() if not st.session_state.df_persediaan.empty else []
    
    for barang in barang_list:
        with st.expander(f"**{barang}** - Kartu Persediaan", expanded=False):
            display_kartu_persediaan_single_barang(barang)
    
def display_kartu_persediaan_detail_per_barang():
    """Menampilkan kartu persediaan detail dengan struktur tabel yang diminta"""
    st.subheader("📦 Kartu Persediaan - Detail Per Barang")
    
    # Inisialisasi jika belum ada
    if "df_persediaan" not in st.session_state:
        st.session_state.df_persediaan = pd.DataFrame({
            "Barang": ["Ayam Jago", "Ayam Broiler", "Telur Ayam"],
            "Stok Awal": [0, 0, 0],
            "Pembelian": [0, 0, 0],
            "Penjualan": [0, 0, 0],
            "Stok Akhir": [0, 0, 0],
            "Harga Rata-rata": [0, 0, 0],
            "Total Nilai": [0, 0, 0]
        })
    
    # Daftar barang yang tersedia
    barang_list = st.session_state.df_persediaan["Barang"].tolist() if not st.session_state.df_persediaan.empty else []
    
    for barang in barang_list:
        with st.expander(f"**{barang}** - Kartu Persediaan Detail", expanded=False):
            display_kartu_persediaan_single_barang_detail(barang)

def display_kartu_persediaan_single_barang_detail(barang):
    """Menampilkan kartu persediaan detail untuk satu barang dengan struktur tabel yang diminta"""
    
    # Data persediaan barang
    barang_data = st.session_state.df_persediaan[st.session_state.df_persediaan["Barang"] == barang]
    
    if not barang_data.empty:
        stok_akhir = barang_data["Stok Akhir"].iloc[0]
        harga_rata = barang_data["Harga Rata-rata"].iloc[0]
        total_nilai = barang_data["Total Nilai"].iloc[0]
        
        # Header informasi
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Stok Akhir", f"{stok_akhir:,.0f} unit")
        with col2:
            st.metric("Harga Rata-rata", f"Rp {harga_rata:,.0f}")
        with col3:
            st.metric("Total Nilai", f"Rp {total_nilai:,.0f}")
        with col4:
            status = "Tersedia" if stok_akhir > 0 else "Habis"
            st.metric("Status", status)
    
    # Buat tabel kartu persediaan detail
    st.write("### 📊 Kartu Persediaan Detail")
    
    # Dapatkan semua transaksi untuk barang ini
    riwayat_barang = pd.DataFrame()
    if "df_riwayat_persediaan" in st.session_state and not st.session_state.df_riwayat_persediaan.empty:
        riwayat_barang = st.session_state.df_riwayat_persediaan[
            st.session_state.df_riwayat_persediaan["Barang"] == barang
        ].sort_values("Tanggal")
    
    if not riwayat_barang.empty:
        # Siapkan data untuk tabel
        tabel_data = []
        saldo_kuantitas = 0
        saldo_nilai = 0
        harga_rata_rata = 0
        
        for _, transaksi in riwayat_barang.iterrows():
            if transaksi["Jenis"] == "Pembelian":
                # Baris untuk unit masuk
                saldo_kuantitas += transaksi["Jumlah"]
                saldo_nilai += transaksi["Total"]
                harga_rata_rata = saldo_nilai / saldo_kuantitas if saldo_kuantitas > 0 else 0
                
                tabel_data.append({
                    "Tanggal": transaksi["Tanggal"],
                    "Keterangan": transaksi["Keterangan"],
                    # Unit Masuk
                    "Kuantitas_Masuk": transaksi["Jumlah"],
                    "Harga_Unit_Masuk": transaksi["Harga"],
                    "Jumlah_Masuk": transaksi["Total"],
                    # Unit Keluar
                    "Kuantitas_Keluar": 0,
                    "Harga_Unit_Keluar": 0,
                    "Jumlah_Keluar": 0,
                    # Balance
                    "Kuantitas_Balance": saldo_kuantitas,
                    "Harga_Rata_Balance": harga_rata_rata,
                    "Jumlah_Balance": saldo_nilai
                })
                
            elif transaksi["Jenis"] == "Penjualan":
                # Baris untuk unit keluar
                kuantitas_keluar = abs(transaksi["Jumlah"])
                saldo_kuantitas -= kuantitas_keluar
                nilai_keluar = kuantitas_keluar * harga_rata_rata
                saldo_nilai -= nilai_keluar
                
                tabel_data.append({
                    "Tanggal": transaksi["Tanggal"],
                    "Keterangan": transaksi["Keterangan"],
                    # Unit Masuk
                    "Kuantitas_Masuk": 0,
                    "Harga_Unit_Masuk": 0,
                    "Jumlah_Masuk": 0,
                    # Unit Keluar
                    "Kuantitas_Keluar": kuantitas_keluar,
                    "Harga_Unit_Keluar": transaksi["Harga"],  # Harga jual
                    "Jumlah_Keluar": abs(transaksi["Total"]),  # Total penjualan
                    # Balance
                    "Kuantitas_Balance": saldo_kuantitas,
                    "Harga_Rata_Balance": harga_rata_rata,
                    "Jumlah_Balance": saldo_nilai
                })
        
        # Buat DataFrame untuk tabel
        if tabel_data:
            df_tabel = pd.DataFrame(tabel_data)
            
            # Tampilkan dengan multi-level columns
            st.write("**Tabel Kartu Persediaan:**")
            
            # Buat header yang complex
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
            
            with col1:
                st.write("**Tanggal**")
            with col2:
                st.write("**Keterangan**")
            with col3:
                st.write("**Unit Masuk**")
            with col4:
                st.write("**Unit Keluar**")
            with col5:
                st.write("**Balance**")
            
            # Tampilkan data
            for _, row in df_tabel.iterrows():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
                
                with col1:
                    st.write(str(row["Tanggal"]))
                with col2:
                    st.write(row["Keterangan"])
                with col3:
                    if row["Kuantitas_Masuk"] > 0:
                        st.write(f"Qty: {row['Kuantitas_Masuk']:,.0f}")
                        st.write(f"Harga: Rp {row['Harga_Unit_Masuk']:,.0f}")
                        st.write(f"Total: Rp {row['Jumlah_Masuk']:,.0f}")
                    else:
                        st.write("-")
                with col4:
                    if row["Kuantitas_Keluar"] > 0:
                        st.write(f"Qty: {row['Kuantitas_Keluar']:,.0f}")
                        st.write(f"Harga: Rp {row['Harga_Unit_Keluar']:,.0f}")
                        st.write(f"Total: Rp {row['Jumlah_Keluar']:,.0f}")
                    else:
                        st.write("-")
                with col5:
                    st.write(f"Qty: {row['Kuantitas_Balance']:,.0f}")
                    st.write(f"Harga: Rp {row['Harga_Rata_Balance']:,.0f}")
                    st.write(f"Total: Rp {row['Jumlah_Balance']:,.0f}")
                
                st.markdown("---")
    else:
        st.info("Belum ada transaksi untuk barang ini.")
    
    # Tampilkan ringkasan transaksi (opsional)
    st.write("### 📋 Ringkasan Transaksi")
    
    # Pembelian
    st.write("#### 🛒 Pembelian")
    if "df_pembelian" in st.session_state and not st.session_state.df_pembelian.empty:
        pembelian_barang = st.session_state.df_pembelian[st.session_state.df_pembelian["Barang"] == barang]
        if not pembelian_barang.empty:
            st.dataframe(pembelian_barang[["Tanggal", "Keterangan", "Jumlah", "Harga Beli", "Total Pembelian"]], 
                        use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada data pembelian.")
    else:
        st.info("Belum ada data pembelian.")
    
    # Penjualan
    st.write("#### 📦 Penjualan")
    if "df_penjualan" in st.session_state and not st.session_state.df_penjualan.empty:
        penjualan_barang = st.session_state.df_penjualan[st.session_state.df_penjualan["Barang"] == barang]
        if not penjualan_barang.empty:
            st.dataframe(penjualan_barang[["Tanggal", "Keterangan", "Jumlah", "Harga Jual", "Total Penjualan"]], 
                        use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada data penjualan.")
    else:
        st.info("Belum ada data penjualan.")
        
def display_kartu_persediaan_detail_per_barang():
    """Menampilkan kartu persediaan detail dengan struktur tabel yang diminta"""
    st.subheader("📦 Kartu Persediaan - Detail Per Barang")
    
    # Inisialisasi jika belum ada
    if "df_persediaan" not in st.session_state:
        st.session_state.df_persediaan = pd.DataFrame({
            "Barang": ["Ayam Jago", "Ayam Broiler", "Telur Ayam"],
            "Stok Awal": [0, 0, 0],
            "Pembelian": [0, 0, 0],
            "Penjualan": [0, 0, 0],
            "Stok Akhir": [0, 0, 0],
            "Harga Rata-rata": [0, 0, 0],
            "Total Nilai": [0, 0, 0]
        })
    
    # Daftar barang yang tersedia
    barang_list = st.session_state.df_persediaan["Barang"].tolist() if not st.session_state.df_persediaan.empty else []
    
    for barang in barang_list:
        with st.expander(f"**{barang}** - Kartu Persediaan Detail", expanded=False):
            display_kartu_persediaan_single_barang_detail(barang)


    
def tambah_riwayat_persediaan(tanggal, jenis, barang, jumlah, harga, total, stok, keterangan):
    """Menambah riwayat pergerakan persediaan - VERSI DIPERBAIKI"""
    try:
        if "df_riwayat_persediaan" not in st.session_state:
            st.session_state.df_riwayat_persediaan = pd.DataFrame(
                columns=["Tanggal", "Jenis", "Barang", "Jumlah", "Harga", "Total", "Stok", "Keterangan"]
            )
        
        new_row = {
            "Tanggal": tanggal,
            "Jenis": jenis,
            "Barang": barang,
            "Jumlah": jumlah,
            "Harga": harga,
            "Total": total,
            "Stok": stok,
            "Keterangan": keterangan
        }
        
        st.session_state.df_riwayat_persediaan = pd.concat([
            st.session_state.df_riwayat_persediaan,
            pd.DataFrame([new_row])
        ], ignore_index=True)
        
        return True
    except Exception as e:
        print(f"Error tambah riwayat persediaan: {str(e)}")
        return False


    
    
def update_persediaan(barang, jumlah, harga, jenis):
    """Fungsi sederhana untuk update persediaan"""
    try:
        # Cari index barang
        idx = st.session_state.df_persediaan[st.session_state.df_persediaan["Barang"] == barang].index
        
        if len(idx) > 0:
            idx = idx[0]
            
            if jenis == "pembelian":
                # Update pembelian
                st.session_state.df_persediaan.at[idx, "Pembelian"] += jumlah
                # Update harga rata-rata
                total_nilai_lama = st.session_state.df_persediaan.at[idx, "Total Nilai"]
                total_unit_lama = st.session_state.df_persediaan.at[idx, "Stok Akhir"]
                total_nilai_baru = total_nilai_lama + (jumlah * harga)
                total_unit_baru = total_unit_lama + jumlah
                
                if total_unit_baru > 0:
                    harga_rata_rata = total_nilai_baru / total_unit_baru
                else:
                    harga_rata_rata = harga
                
                st.session_state.df_persediaan.at[idx, "Harga Rata-rata"] = harga_rata_rata
                st.session_state.df_persediaan.at[idx, "Total Nilai"] = total_nilai_baru
                
            elif jenis == "penjualan":
                # Update penjualan
                st.session_state.df_persediaan.at[idx, "Penjualan"] += jumlah
            
            # Update stok akhir
            stok_awal = st.session_state.df_persediaan.at[idx, "Stok Awal"]
            pembelian = st.session_state.df_persediaan.at[idx, "Pembelian"]
            penjualan = st.session_state.df_persediaan.at[idx, "Penjualan"]
            st.session_state.df_persediaan.at[idx, "Stok Akhir"] = stok_awal + pembelian - penjualan
            
            # Update total nilai
            stok_akhir = st.session_state.df_persediaan.at[idx, "Stok Akhir"]
            harga_rata = st.session_state.df_persediaan.at[idx, "Harga Rata-rata"]
            st.session_state.df_persediaan.at[idx, "Total Nilai"] = stok_akhir * harga_rata
            
        return True
    except Exception as e:
        st.error(f"Error update persediaan: {str(e)}")
        return False

def tambah_pembelian_ke_jurnal_umum(tanggal, keterangan, barang, total_pembelian):
    """Menambahkan pembelian ke jurnal umum"""
    try:
        if "df_jurnal_umum" not in st.session_state:
            st.session_state.df_jurnal_umum = pd.DataFrame(
                columns=["No", "Tanggal", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"]
            )
        
        nomor_terakhir = len(st.session_state.df_jurnal_umum)
        
        # Entri pembelian: Debit Persediaan, Kredit Kas/Utang
        entri1 = {
            "No": nomor_terakhir + 1,
            "Tanggal": tanggal,
            "Akun Debit": "Persediaan Barang Dagang",
            "Debit (Rp)": total_pembelian,
            "Akun Kredit": "",
            "Kredit (Rp)": 0
        }
        
        entri2 = {
            "No": nomor_terakhir + 2,
            "Tanggal": tanggal,
            "Akun Debit": "",
            "Debit (Rp)": 0,
            "Akun Kredit": "Kas",
            "Kredit (Rp)": total_pembelian
        }
        
        new_entries = pd.DataFrame([entri1, entri2])
        st.session_state.df_jurnal_umum = pd.concat([
            st.session_state.df_jurnal_umum,
            new_entries
        ], ignore_index=True)
        
        update_sistem_dengan_struktur_baru()
        return True
        
    except Exception as e:
        st.error(f"Error tambah pembelian ke jurnal: {str(e)}")
        return False

def hitung_ulang_persediaan():
    """Menghitung ulang semua persediaan berdasarkan riwayat"""
    try:
        if "df_riwayat_persediaan" not in st.session_state or st.session_state.df_riwayat_persediaan.empty:
            return False
        
        # Reset persediaan
        st.session_state.df_persediaan = pd.DataFrame(
            columns=["Barang", "Stok Awal", "Pembelian", "Penjualan", "Stok Akhir", "Harga Rata-rata", "Total Nilai"]
        )
        
        # Proses semua barang unik
        semua_barang = st.session_state.df_riwayat_persediaan["Barang"].unique()
        
        for barang in semua_barang:
            riwayat_barang = st.session_state.df_riwayat_persediaan[
                st.session_state.df_riwayat_persediaan["Barang"] == barang
            ].sort_values("Tanggal")
            
            stok_awal = 0
            total_pembelian = 0
            total_penjualan = 0
            total_nilai = 0
            
            for _, transaksi in riwayat_barang.iterrows():
                if transaksi["Jenis"] == "Pembelian":
                    total_pembelian += transaksi["Jumlah"]
                    total_nilai += transaksi["Total"]
                elif transaksi["Jenis"] == "Penjualan":
                    total_penjualan += abs(transaksi["Jumlah"])
                    # Untuk penjualan, kurangi nilai berdasarkan metode yang dipilih
                    if st.session_state.metode_persediaan == "Average":
                        harga_rata2 = total_nilai / (stok_awal + total_pembelian - total_penjualan + abs(transaksi["Jumlah"])) if (stok_awal + total_pembelian - total_penjualan + abs(transaksi["Jumlah"])) > 0 else 0
                        total_nilai -= abs(transaksi["Jumlah"]) * harga_rata2
            
            stok_akhir = stok_awal + total_pembelian - total_penjualan
            harga_rata2 = total_nilai / stok_akhir if stok_akhir > 0 else 0
            
            # Update persediaan
            new_row = {
                "Barang": barang,
                "Stok Awal": stok_awal,
                "Pembelian": total_pembelian,
                "Penjualan": total_penjualan,
                "Stok Akhir": stok_akhir,
                "Harga Rata-rata": harga_rata2,
                "Total Nilai": total_nilai
            }
            
            st.session_state.df_persediaan = pd.concat([
                st.session_state.df_persediaan,
                pd.DataFrame([new_row])
            ], ignore_index=True)
        
        auto_save()
        return True
        
    except Exception as e:
        st.error(f"Error hitung ulang persediaan: {str(e)}")
        return False
    
    
def update_setelah_penutupan():
    """Memproses data setelah penutupan periode"""
    try:
        # Update buku besar dengan semua transaksi termasuk penutupan
        update_buku_besar_per_akun()
        
        # Buat neraca saldo setelah penutup
        if "buku_besar_per_akun" in st.session_state and st.session_state.buku_besar_per_akun:
            # Filter hanya akun riil (bukan nominal)
            akun_nominal = ["Pendapatan Jasa", "Pendapatan Lain", "Beban Gaji", "Beban Sewa", 
                           "Beban Listrik dan Air", "Beban Transportasi", "Beban Lain-lain", "Ikhtisar Laba Rugi"]
            
            neraca_data = []
            for akun, df_akun in st.session_state.buku_besar_per_akun.items():
                if akun not in akun_nominal and not df_akun.empty:
                    saldo_akhir = df_akun["Saldo (Rp)"].iloc[-1]
                    total_debit = df_akun["Debit (Rp)"].sum()
                    total_kredit = df_akun["Kredit (Rp)"].sum()
                    
                    neraca_data.append({
                        "Nama Akun": akun,
                        "Debit (Rp)": total_debit,
                        "Kredit (Rp)": total_kredit,
                        "Saldo (Rp)": saldo_akhir
                    })
            
            if neraca_data:
                neraca_saldo = pd.DataFrame(neraca_data)
                neraca_saldo = neraca_saldo.sort_values("Nama Akun").reset_index(drop=True)
                neraca_saldo.insert(0, "No", range(1, len(neraca_saldo) + 1))
                
                st.session_state.df_neraca_saldo_setelah_penutup = neraca_saldo
            
            auto_save()
            return True
        
        return False
        
    except Exception as e:
        st.error(f"Error dalam update_setelah_penutupan: {str(e)}")
        return False

def akhiri_periode():
    """Mengakhiri periode saat ini dan mempersiapkan periode baru - VERSI DIPERBAIKI"""
    try:
        # Pastikan sudah ada jurnal penutup
        if "df_jurnal_penutup" in st.session_state and not st.session_state.df_jurnal_penutup.empty:
            
            # Update semua sistem terlebih dahulu
            update_buku_besar_per_akun()
            update_semua_laporan_keuangan()
            
            # Buat neraca saldo setelah penutup dari buku besar terkini
            if "buku_besar_per_akun" in st.session_state and st.session_state.buku_besar_per_akun:
                neraca_data = []
                nomor = 1
                
                for akun, df_akun in st.session_state.buku_besar_per_akun.items():
                    if not df_akun.empty:
                        saldo_akhir = safe_float_convert(df_akun["Saldo (Rp)"].iloc[-1])
                        total_debit = df_akun["Debit (Rp)"].apply(safe_float_convert).sum()
                        total_kredit = df_akun["Kredit (Rp)"].apply(safe_float_convert).sum()
                        
                        # Tentukan posisi debit/kredit untuk neraca saldo
                        if saldo_akhir >= 0:
                            neraca_data.append({
                                "No": nomor,
                                "Nama Akun": akun,
                                "Debit (Rp)": abs(saldo_akhir),
                                "Kredit (Rp)": 0
                            })
                        else:
                            neraca_data.append({
                                "No": nomor, 
                                "Nama Akun": akun,
                                "Debit (Rp)": 0,
                                "Kredit (Rp)": abs(saldo_akhir)
                            })
                        nomor += 1
                
                if neraca_data:
                    st.session_state.df_neraca_saldo_setelah_penutup = pd.DataFrame(neraca_data)
            
            # Simpan neraca saldo setelah penutup sebagai periode sebelumnya
            if "df_neraca_saldo_setelah_penutup" in st.session_state and not st.session_state.df_neraca_saldo_setelah_penutup.empty:
                # Simpan ke riwayat periode
                simpan_ke_riwayat_periode(st.session_state.periode_sekarang, st.session_state.df_neraca_saldo_setelah_penutup)
                
                # Set sebagai neraca saldo periode sebelumnya untuk periode baru
                st.session_state.df_neraca_saldo_periode_sebelumnya = st.session_state.df_neraca_saldo_setelah_penutup.copy()
                st.success(f"✅ Neraca saldo periode {st.session_state.periode_sekarang} berhasil disimpan")
            
            # Buat periode baru
            from datetime import datetime
            bulan_sekarang = datetime.now().month
            tahun_sekarang = datetime.now().year
            
            # Hitung periode berikutnya
            if bulan_sekarang == 12:
                bulan_berikutnya = 1
                tahun_berikutnya = tahun_sekarang + 1
            else:
                bulan_berikutnya = bulan_sekarang + 1
                tahun_berikutnya = tahun_sekarang
            
            periode_baru = f"{datetime(1900, bulan_berikutnya, 1).strftime('%B')} {tahun_berikutnya}"
            
            # Update periode dan reset data
            st.session_state.periode_sekarang = periode_baru
            reset_data_periode_baru()
            
            # Update tanggal awal periode
            st.session_state.tanggal_awal_periode = datetime(tahun_berikutnya, bulan_berikutnya, 1).date()
            
            # Tambah ke daftar periode jika belum ada
            if periode_baru not in st.session_state.daftar_periode:
                st.session_state.daftar_periode.append(periode_baru)
            
            auto_save()
            st.success(f"✅ Periode berhasil diakhiri. Periode baru: {periode_baru}")
            return True
        else:
            st.error("Belum ada jurnal penutup. Silakan buat jurnal penutup terlebih dahulu.")
            return False
            
    except Exception as e:
        st.error(f"Error mengakhiri periode: {str(e)}")
        return False
    
def update_periode_semua_halaman():
    """Update periode di semua halaman berdasarkan periode aktif"""
    st.session_state.periode_display = st.session_state.periode_sekarang

def ganti_periode(periode_baru):
    """Mengganti periode saat ini dengan reset data transaksi - VERSI DIPERBAIKI"""
    try:
        # Simpan data periode sebelumnya (neraca saldo setelah penutup)
        if "df_neraca_saldo_setelah_penutup" in st.session_state and not st.session_state.df_neraca_saldo_setelah_penutup.empty:
            simpan_ke_riwayat_periode(st.session_state.periode_sekarang, st.session_state.df_neraca_saldo_setelah_penutup)
            
            # Set sebagai neraca saldo periode sebelumnya untuk periode baru
            st.session_state.df_neraca_saldo_periode_sebelumnya = st.session_state.df_neraca_saldo_setelah_penutup.copy()
        
        # Update periode
        st.session_state.periode_sekarang = periode_baru
        
        # Reset semua data transaksi untuk periode baru
        reset_data_periode_baru()
        
        # Load data untuk periode baru (jika ada)
        load_data_periode(periode_baru)
        
        # Tambah ke daftar periode jika belum ada
        if periode_baru not in st.session_state.daftar_periode:
            st.session_state.daftar_periode.append(periode_baru)
        
        print(f"✅ Berhasil ganti ke periode: {periode_baru}")
        return True
    except Exception as e:
        print(f"❌ Error ganti periode: {str(e)}")
        return False
    
def safe_dataframe_display(df, numeric_columns=None):
    """Menampilkan DataFrame dengan format yang aman - VERSI DIPERBAIKI"""
    try:
        if df.empty:
            return df
            
        df_display = df.copy()
        
        if numeric_columns is None:
            numeric_columns = [col for col in df.columns if '(Rp)' in col]
        
        # Format kolom numerik dengan handle error
        for col in numeric_columns:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(lambda x: format_angka(x) if pd.notna(x) and str(x).strip() != '' else "0")
        
        return df_display
    except Exception as e:
        print(f"Error dalam safe_dataframe_display: {e}")
        return df

def clean_numeric_data(df, numeric_columns):
    """Membersihkan data numerik dalam DataFrame - VERSI DIPERBAIKI"""
    try:
        df_clean = df.copy()
        for col in numeric_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].apply(safe_float_convert)
        return df_clean
    except Exception as e:
        print(f"Error dalam clean_numeric_data: {e}")
        return df

def validate_transaction_data(df):
    """Validasi data transaksi sebelum processing - VERSI DIPERBAIKI"""
    try:
        if df.empty:
            return df
            
        df_valid = df.copy()
        
        # Validasi kolom numerik
        numeric_columns = [col for col in df.columns if '(Rp)' in col]
        for col in numeric_columns:
            if col in df_valid.columns:
                df_valid[col] = df_valid[col].apply(safe_float_convert)
        
        # Validasi kolom teks
        text_columns = ['Akun Debit', 'Akun Kredit', 'Keterangan']
        for col in text_columns:
            if col in df_valid.columns:
                df_valid[col] = df_valid[col].fillna('').astype(str)
        
        return df_valid
    except Exception as e:
        print(f"Error dalam validate_transaction_data: {e}")
        return df
    
def cleanup_numeric_data():
    """Membersihkan data numerik di semua session state - VERSI DIPERBAIKI"""
    try:
        numeric_dataframes = [
            "df_jurnal_umum", "df_jurnal_penyesuaian", "df_buku_besar", 
            "df_neraca_saldo", "df_neraca_saldo_setelah_penutup"
        ]
        
        for df_key in numeric_dataframes:
            if df_key in st.session_state and not st.session_state[df_key].empty:
                df = st.session_state[df_key].copy()
                numeric_columns = [col for col in df.columns if '(Rp)' in col]
                
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = df[col].apply(safe_float_convert)
                
                st.session_state[df_key] = df
                
        return True
    except Exception as e:
        print(f"Error dalam cleanup_numeric_data: {e}")
        return False
    
if "system_initialized" not in st.session_state:
    initialize_fixed_session_state()
    cleanup_numeric_data()
    st.session_state.system_initialized = True

print("✅ Sistem perbaikan error telah diinisialisasi!")  
    
def safe_float_convert(value, default=0.0):
    """Mengonversi value ke float dengan aman - VERSI DIPERBAIKI"""
    try:
        if pd.isna(value) or value == '' or value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Bersihkan string dari format Rupiah dan karakter non-numerik
            cleaned = str(value).replace('Rp', '').replace('.', '').replace(',', '.').replace(' ', '').strip()
            # Hapus karakter non-digit kecuali titik dan minus
            cleaned = ''.join(ch for ch in cleaned if ch.isdigit() or ch in ['.', '-'])
            if cleaned == '' or cleaned == '-' or cleaned == '.':
                return default
            return float(cleaned)
        return float(value)
    except (ValueError, TypeError):
        return default

def auto_save():
    """Fungsi auto-save yang dipanggil setelah setiap perubahan penting - VERSI AMAN"""
    try:
        # Validasi data sebelum menyimpan
        dataframes_to_validate = [
            "df_jurnal_umum", "df_buku_besar", "df_neraca_saldo", 
            "df_penjualan", "df_pembelian", "df_persediaan"
        ]
        
        for df_key in dataframes_to_validate:
            if df_key in st.session_state and not st.session_state[df_key].empty:
                # Pastikan tipe data numerik konsisten
                df = st.session_state[df_key].copy()
                numeric_columns = [col for col in df.columns if '(Rp)' in col]
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
                st.session_state[df_key] = df
        
        save_to_database()
        return True
    except Exception as e:
        print(f"❌ Auto-save failed: {str(e)}")
        return False
    
    
    # user data
if "users" not in st.session_state:
    # Data default untuk user yang sudah terdaftar
    st.session_state.users = {
        "admin": "admin123",
       
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

    # LOGIN & REGIST
if not st.session_state.logged_in:
    st.title("🔐 Autentikasi SIMAYA")

    tab_login, tab_register = st.tabs(["Login", "Registrasi"])

    with tab_login:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Selamat datang, {username}!")
                st.session_state.logged_in = True  
                st.session_state.username = username
                st.stop()  
            else:
                st.error("Username atau password salah.")

    with tab_register:
        new_user = st.text_input("Username Baru", key="reg_user")
        new_pass = st.text_input("Password Baru", type="password", key="reg_pass")
        confirm_pass = st.text_input("Konfirmasi Password", type="password", key="reg_confirm")

        if st.button("Daftar"):
            if new_user.strip() == "" or new_pass.strip() == "":
                st.warning("Username dan password tidak boleh kosong.")
            elif new_user in st.session_state.users:
                st.error("Username sudah terdaftar.")
            elif new_pass != confirm_pass:
                st.error("Password dan konfirmasi tidak cocok.")
            else:
                # Daftarkan user baru
                st.session_state.users[new_user] = new_pass
                st.success("Registrasi berhasil! Silakan login.")

    # regist login berhasil
    st.stop()

if "transaction_counter" not in st.session_state:
    if "df_jurnal_umum" in st.session_state and not st.session_state.df_jurnal_umum.empty:
        # Cari nomor tertinggi yang ada
        max_no = st.session_state.df_jurnal_umum["No"].max()
        if pd.isna(max_no):
            st.session_state.transaction_counter = 1
        else:
            st.session_state.transaction_counter = int(max_no) + 1
    else:
        st.session_state.transaction_counter = 1
        
        
# Backup manual
if st.button("📥 Backup ke Excel"):
    try:
        with st.spinner("Membuat backup..."):
            buffer = export_to_excel()
            
            # Validasi buffer
            if buffer is None:
                st.error("❌ Gagal membuat backup: buffer tidak terbentuk")
            else:
                # Cek ukuran buffer
                buffer_size = buffer.getbuffer().nbytes
                if buffer_size == 0:
                    st.error("❌ File backup kosong")
                else:
                    st.download_button(
                        label="📥 Download Backup",
                        data=buffer,
                        file_name=f"backup_keuangan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_backup"
                    )
                    st.success(f"✅ Backup berhasil dibuat ({buffer_size} bytes)")
    except Exception as e:
        st.error(f"❌ Error dalam proses backup: {str(e)}")
        
# menu login regist
with st.sidebar:
    if "username" in st.session_state:
        st.markdown(f"👤 Login sebagai {st.session_state.username}")
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.pop("username", None)
        st.stop()
    
    # ==================== MANAJEMEN DATABASE ====================
    st.markdown("---")
    st.subheader("💾 Manajemen Database")
    
    # Status database
    if os.path.exists("database_keuangan.xlsx"):
        file_size = os.path.getsize("database_keuangan.xlsx") / 1024  # KB
        st.success(f"✅ Database aktif ({file_size:.1f} KB)")
    else:
        st.error("❌ Database tidak ditemukan")
    
    col_db1, col_db2 = st.columns(2)
    
    with col_db1:
        if st.button("🔄 Load Ulang"):
            load_from_database()
            st.success("Data berhasil dimuat ulang!")
            st.rerun()
    
    with col_db2:
        if st.button("💾 Simpan Sekarang"):
            if save_to_database():
                st.success("Data berhasil disimpan!")
            else:
                st.error("Gagal menyimpan data!")
    
    # Backup manual
    if st.button("📥 Backup ke Excel"):
        buffer = export_to_excel()
        st.download_button(
            label="📥 Download Backup",
            data=buffer,
            file_name=f"backup_keuangan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # Reset data dengan konfirmasi
    st.markdown("---")
    st.subheader("⚠️ Administrasi")
    
    with st.expander("Reset Data", expanded=False):
        st.warning("**PERHATIAN:** Tindakan ini akan menghapus semua data!")
        password_reset = st.text_input("Password Admin", type="password", key="reset_pass")
        
        if st.button("🗑️ Reset Semua Data", type="secondary"):
            if password_reset == "admin123":
                keys_to_delete = [key for key in st.session_state.keys() if key.startswith('df_')]
                for key in keys_to_delete:
                    del st.session_state[key]
                
                # Inisialisasi ulang
                for df_key, columns in default_dataframes.items():
                    st.session_state[df_key] = pd.DataFrame(columns=columns)
                
                # Hapus file database
                if os.path.exists("database_keuangan.xlsx"):
                    os.remove("database_keuangan.xlsx")
                
                init_database()
                st.success("✅ Semua data berhasil direset!")
                st.rerun()
            else:
                st.error("Password salah!")
                
                
    with st.expander("🔧 Tools Perbaikan Data"):
     if st.button("🔄 Reset Penomoran Jurnal Umum"):
        if reset_dan_renumber_jurnal_umum():
            st.success("Penomoran berhasil direset!")
            st.rerun()
        else:
            st.error("Gagal reset penomoran")
            
    # Inisialisasi sistem yang diperbaiki
if "system_initialized_fixed" not in st.session_state:
    print("🔄 Initializing fixed system...")
    init_session_state_fixed()
    load_from_database()  # Jika fungsi ini sudah ada
    st.session_state.system_initialized_fixed = True
    print("✅ Fixed system initialization completed")

# Navigasi sidebar
with st.sidebar:
    selected = st.sidebar.radio("🐓SIMAYA🐓", 
                           ['Profile', 'Neraca Saldo Periode Sebelumnya', 'Jurnal Umum','Penjualan & Pembelian', 'Buku Besar', 'Neraca Saldo', 'Jurnal Penyesuaian', 'Laporan Laba Rugi', 'Laporan Perubahan Modal', 'Laporan Posisi Keuangan', 'Jurnal Penutup', 'Neraca Saldo Setelah Penutup', 'Kartu persediaan', 'Kartu Persediaan Detail', 'Unduh Laporan Keuangan'],  # Pilihan menu
                            )

    st.markdown("---")
    st.subheader("📅 Manajemen Periode")
    
    st.info(f"**Periode Saat Ini:** {st.session_state.periode_sekarang}")
    st.success(f"**🟢 Periode Aktif:** {st.session_state.periode_sekarang}")
    
    # Pilih periode
    with st.expander("Ganti Periode"):
        periode_options = st.session_state.daftar_periode
        periode_pilihan = st.selectbox("Pilih Periode", periode_options)
        
        if st.button("🔄 Ganti ke Periode Ini"):
            if periode_pilihan != st.session_state.periode_sekarang:
                if ganti_periode(periode_pilihan):
                    st.success(f"Berhasil ganti ke periode {periode_pilihan}")
                    st.rerun()
                else:
                    st.error("Gagal ganti periode")
    
    # Buat periode baru
    with st.expander("Buat Periode Baru"):
        bulan = st.selectbox("Bulan", [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ])
        tahun = st.number_input("Tahun", min_value=2020, max_value=2030, value=datetime.now().year)
        
        if st.button("🆕 Buat Periode Baru"):
            periode_baru = f"{bulan} {tahun}"
            if periode_baru not in st.session_state.daftar_periode:
                st.session_state.daftar_periode.append(periode_baru)
                st.success(f"Periode {periode_baru} berhasil dibuat!")
            else:
                st.warning("Periode sudah ada!")
    
    
    # Inisialisasi untuk sistem penjualan dan persediaan
if "df_penjualan" not in st.session_state:
    st.session_state.df_penjualan = pd.DataFrame(
        columns=["No", "Tanggal", "Keterangan", "Akun Debit 1", "Debit 1 (Rp)", "Akun Debit 2", "Debit 2 (Rp)", 
                "Akun Kredit 1", "Kredit 1 (Rp)", "Akun Kredit 2", "Kredit 2 (Rp)", "Barang", "Jumlah", "Harga Jual", "HPP"]
    )

if "df_pembelian" not in st.session_state:
    st.session_state.df_pembelian = pd.DataFrame(
        columns=["No", "Tanggal", "Keterangan", "Barang", "Jumlah", "Harga Beli", "Total Pembelian"]
    )

if "df_persediaan" not in st.session_state:
    st.session_state.df_persediaan = pd.DataFrame(
        columns=["Barang", "Stok Awal", "Pembelian", "Penjualan", "Stok Akhir", "Harga Rata-rata", "Total Nilai"]
    )

if "metode_persediaan" not in st.session_state:
    st.session_state.metode_persediaan = "Average"  # Default metode

if "riwayat_persediaan" not in st.session_state:
    st.session_state.riwayat_persediaan = pd.DataFrame(
        columns=["Tanggal", "Jenis", "Barang", "Jumlah", "Harga", "Total", "Stok", "Keterangan"]
    )
    
    
    st.markdown("---")
    if st.button("🔄 Reset Session State (Debug)"):
        keys_to_keep = ['users', 'logged_in', 'username']
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]
        st.success("Session state direset!")
        st.rerun()
        
        with st.expander("🔍 Status Sistem dan Database"):
         st.write("### Status Penyimpanan Data")
        
        if os.path.exists("database_keuangan.xlsx"):
            file_size = os.path.getsize("database_keuangan.xlsx") / 1024
            st.success(f"✅ **Database File:** database_keuangan.xlsx")
            st.info(f"📊 **Ukuran File:** {file_size:.1f} KB")
            st.info(f"🕒 **Terakhir Dimodifikasi:** {datetime.fromtimestamp(os.path.getmtime('database_keuangan.xlsx')).strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.error("❌ **Database File:** Tidak ditemukan")
        
        st.write("### Statistik Data")
        data_stats = {
            "Jenis Data": ["Jurnal Umum", "Jurnal Penyesuaian", "Buku Besar", "Neraca Saldo"],
            "Jumlah Record": [
                len(st.session_state.get("df_jurnal_umum", pd.DataFrame())),
                len(st.session_state.get("df_jurnal_penyesuaian", pd.DataFrame())),
                len(st.session_state.get("df_buku_besar", pd.DataFrame())),
                len(st.session_state.get("df_neraca_saldo", pd.DataFrame()))
            ]
        }
        st.dataframe(pd.DataFrame(data_stats))
        
        # Test save/load
        col_test1, col_test2 = st.columns(2)
        with col_test1:
            if st.button("🧪 Test Simpan"):
                if save_to_database():
                    st.success("✅ Test penyimpanan berhasil!")
                else:
                    st.error("❌ Test penyimpanan gagal!")
        
        with col_test2:
            if st.button("🧪 Test Muat Ulang"):
                if load_from_database():
                    st.success("✅ Test pemuatan berhasil!")
                else:
                    st.error("❌ Test pemuatan gagal!")
        
                
                
if selected == 'Profile':
        st.subheader('Profile 🐓')
        st.write("""Peternakan Pak Muji adalah Peternakan ayam yang bermitra dengan pabrik penyedia daging segar dan bahan baku sosis, untuk itu kualitas ayam petrnakan pak muji tentunya terjamin kualitasnya. Disini ada tiga macam jenis ayam, Ayam jago, Ayam Petelur dan Ayam Broiler. Setiap ayam mempunya kandangnya tersendiri dan mempunyai perlakuan khusus tiap jenisnya. KArna ditangani oleh ahli setiap kebutuuhan ayam baik pangan, antiiotik, tempat kandang baik kebersihan, cahaya ataupun yang lain terjamin sempurna""")
        st.write('Jl Mendak,Desa Ngijo, Kec Gunungpati, Kota Semarang, Jawa Tengah 50192')
        
       
        
        

    # Halaman Neraca Saldo Periode Sebelumnya
elif selected == 'Neraca Saldo Periode Sebelumnya':
    st.subheader('Neraca Saldo Periode Sebelumnya 🧾')
    
    st.info(f"**Periode Saat Ini:** {st.session_state.periode_sekarang}")
    
    # Tombol untuk memuat ulang data
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Muat Ulang Data", key="reload_neraca_sebelumnya"):
            # Coba muat dari riwayat periode sebelumnya
            periode_sebelumnya = st.session_state.periode_sekarang  # Bisa disesuaikan logika untuk mendapatkan periode sebelumnya
            neraca_sebelumnya = muat_dari_riwayat_periode(periode_sebelumnya)
            if not neraca_sebelumnya.empty:
                st.session_state.df_neraca_saldo_periode_sebelumnya = neraca_sebelumnya
                st.success("Data berhasil dimuat dari riwayat!")
                st.rerun()
            else:
                st.info("Tidak ada data periode sebelumnya di riwayat.")
    
    # Tampilkan informasi
    st.info("""
    **Fungsi Neraca Saldo Periode Sebelumnya:**
    - Menampilkan saldo akhir dari periode sebelumnya
    - Digunakan sebagai saldo awal untuk periode berjalan
    - Diambil secara otomatis dari Neraca Saldo Setelah Penutup periode sebelumnya
    """)
    
    # Debug information
    with st.expander("🔧 Informasi Debug"):
        st.write(f"Jumlah data: {len(st.session_state.df_neraca_saldo_periode_sebelumnya)}")
        st.write("Columns:", st.session_state.df_neraca_saldo_periode_sebelumnya.columns.tolist())
    
    # Tampilkan data neraca saldo periode sebelumnya
    if not st.session_state.df_neraca_saldo_periode_sebelumnya.empty:
        st.write("### 📊 Neraca Saldo Periode Sebelumnya")
        
        # Format tampilan
        df_tampil = st.session_state.df_neraca_saldo_periode_sebelumnya.copy()
        
        # Format kolom numerik
        if 'Debit (Rp)' in df_tampil.columns:
            df_tampil['Debit (Rp)'] = df_tampil['Debit (Rp)'].apply(lambda x: f"Rp {x:,.0f}" if pd.notna(x) and x != 0 else "0")
        if 'Kredit (Rp)' in df_tampil.columns:
            df_tampil['Kredit (Rp)'] = df_tampil['Kredit (Rp)'].apply(lambda x: f"Rp {x:,.0f}" if pd.notna(x) and x != 0 else "0")
        
        st.dataframe(df_tampil, use_container_width=True, hide_index=True)
        
        # Hitung total dari data asli
        df_asli = st.session_state.df_neraca_saldo_periode_sebelumnya
        total_debit = df_asli["Debit (Rp)"].apply(safe_float_convert).sum()
        total_kredit = df_asli["Kredit (Rp)"].apply(safe_float_convert).sum()
        
        st.write("### 💰 Total Neraca Saldo Periode Sebelumnya")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Debit", f"Rp {total_debit:,.0f}")
        with col2:
            st.metric("Total Kredit", f"Rp {total_kredit:,.0f}")
        
        # Validasi keseimbangan
        selisih = abs(total_debit - total_kredit)
        if selisih < 1:
            st.success("✅ Neraca saldo periode sebelumnya SEIMBANG")
        else:
            st.error(f"❌ Neraca saldo periode sebelumnya TIDAK SEIMBANG - Selisih: Rp {selisih:,.0f}")
            
    else:
        st.info("""
        **Belum ada data neraca saldo periode sebelumnya.**
        
        **Cara mendapatkan data:**
        1. Selesaikan periode sebelumnya dengan membuat **Jurnal Penutup**
        2. Pastikan **Neraca Saldo Setelah Penutup** sudah terbentuk
        3. Data akan otomatis tersimpan sebagai neraca saldo periode sebelumnya
        4. Klik tombol **'Muat Ulang Data'** di atas
        
        **Untuk testing, sistem telah menyediakan data contoh.**
        """)
        
        # Opsi manual untuk testing
        with st.expander("🔧 Opsi Manual (Testing & Development)"):
            st.warning("Ini hanya untuk testing. Pada penggunaan normal, data harus berasal dari penutupan periode.")
            
            if st.button("📝 Set Contoh Data Neraca Saldo Awal", key="set_contoh_neraca"):
                contoh_data = [
                    {"No": 1, "Nama Akun": "Kas", "Debit (Rp)": 100000000, "Kredit (Rp)": 0},
                    {"No": 2, "Nama Akun": "Persediaan", "Debit (Rp)": 50000000, "Kredit (Rp)": 0},
                    {"No": 3, "Nama Akun": "Peralatan", "Debit (Rp)": 75000000, "Kredit (Rp)": 0},
                    {"No": 4, "Nama Akun": "Utang Usaha", "Debit (Rp)": 0, "Kredit (Rp)": 45000000},
                    {"No": 5, "Nama Akun": "Modal", "Debit (Rp)": 0, "Kredit (Rp)": 180000000},
                ]
                st.session_state.df_neraca_saldo_periode_sebelumnya = pd.DataFrame(contoh_data)
                st.success("Contoh data berhasil ditambahkan!")
                st.rerun()
                
                
    # Halaman Jurnal Umum
elif selected == "Jurnal Umum":
    st.subheader("Jurnal Umum 📓")
    st.markdown(f"**Periode:** {st.session_state.periode_sekarang}")
    
    # Inisialisasi dataframe jika belum ada
    if "df_jurnal_umum" not in st.session_state:
        st.session_state.df_jurnal_umum = pd.DataFrame(
            columns=["No", "Tanggal", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"]
        )
    
    # Inisialisasi transaction counter jika belum ada
    if "transaction_counter" not in st.session_state:
        if "df_jurnal_umum" in st.session_state and not st.session_state.df_jurnal_umum.empty:
            max_no = st.session_state.df_jurnal_umum["No"].max()
            st.session_state.transaction_counter = int(max_no) + 1 if not pd.isna(max_no) else 1
        else:
            st.session_state.transaction_counter = 1
    
    # Reset state untuk double entry setiap kali halaman dimuat
    if 'double_entries_simple' not in st.session_state:
        st.session_state.double_entries_simple = []
    
    # DAFTAR AKUN YANG DIPERBARUI
    daftar_akun = [
        "Kas", "Bank", "Deposito", "Investasi Jangka Pendek", 
    "Piutang Usaha", "Piutang Dagang", "Piutang Lainnya",
    "Persediaan", "Persediaan Barang Dagang", "Persediaan Bahan Baku",
    "Persediaan Barang Dalam Proses", "Persediaan Barang Jadi",
    "Perlengkapan", "Asuransi Dibayar Dimuka", "Sewa Dibayar Dimuka",
    "Pajak Dibayar Dimuka", "Biaya Dibayar Dimuka", "Pendapatan Ditangguhkan",
    
    # Aset Tidak Lancar
    "Tanah", "Gedung", "Bangunan", "Kendaraan", "Peralatan", "Mesin",
    "Inventaris", "Akumulasi Penyusutan", "Aset Tetap Lainnya",
    "Investasi Jangka Panjang", "Aset Tidak Berwujud", "Goodwill",
    "Paten", "Merek Dagang", "Hak Cipta", "Aset Sewa Guna Usaha",
    "Aset Biologis",
    
    # Liabilitas Jangka Pendek
    "Utang Usaha", "Utang Dagang", "Utang Bank Jangka Pendek",
    "Utang Wesel", "Utang Gaji", "Utang Pajak", "Utang Bunga",
    "Utang Dividen", "Pendapatan Diterima Dimuka", "Biaya Akrual",
    "Utang Jangka Pendek Lainnya", "Bagian Lancar Utang Jangka Panjang",
    
    # Liabilitas Jangka Panjang
    "Utang Bank Jangka Panjang", "Utang Obligasi", "Utang Hipotek",
    "Utang Sewa Guna Usaha", "Utang Pensiun", "Utang Jangka Panjang Lainnya",
    
    # Ekuitas
    "Modal Saham", "Modal Disetor", "Agio Saham",
    "Laba Ditahan", "Saldo Laba", "Deviden",
    "Prive", "Modal Pemilik", "Modal",
    "Ekuitas Lainnya", "Cadangan",
    
    # Pendapatan
    "Penjualan", "Pendapatan Jasa", "Pendapatan Lain-lain",
    "Pendapatan Bunga", "Pendapatan Sewa",
    
    # Beban
    "Harga Pokok Penjualan", "Beban Gaji", "Beban Sewa",
    "Beban Listrik dan Air", "Beban Transportasi", "Beban Lain-lain",
    "Beban Asuransi", "Beban Penyusutan", "Beban Bunga",
    "Beban Pajak", "Beban Administrasi", "Beban Pemeliharaan",
    "Beban Perlengkapan", "Beban Iklan", "Beban Research dan Development"
    ]
    
    # TAB UNTUK SINGLE ENTRY DAN DOUBLE ENTRY
    tab1, tab2 = st.tabs(["🔹 Single Entry", "🔸 Double Entry"])
    
    with tab1:
        # FORM SINGLE ENTRY
        with st.form("form_tambah_jurnal_single", clear_on_submit=True):
            st.write("### 🔹 Transaksi Single Entry")
            
            tanggal_single = st.date_input("Tanggal", key="tanggal_single")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Entri Debit")
                akun_debit_single = st.selectbox("Akun Debit", daftar_akun, key="debit_single")
                jumlah_debit_str_single = st.text_input("Jumlah Debit (Rp)", value="", placeholder="Contoh: 50.000.000", key="debit_input_single")
                jumlah_debit_single = parse_rupiah(jumlah_debit_str_single) if jumlah_debit_str_single else 0
            
            with col2:
                st.subheader("Entri Kredit") 
                akun_kredit_single = st.selectbox("Akun Kredit", daftar_akun, key="kredit_single")
                jumlah_kredit_str_single = st.text_input("Jumlah Kredit (Rp)", value="", placeholder="Contoh: 50.000.000", key="kredit_input_single")
                jumlah_kredit_single = parse_rupiah(jumlah_kredit_str_single) if jumlah_kredit_str_single else 0
            
            # VALIDASI
            validation_errors = []
            
            if akun_debit_single == akun_kredit_single:
                validation_errors.append("❌ Akun debit dan kredit tidak boleh sama")
            
            if jumlah_debit_single == 0 and jumlah_kredit_single == 0:
                validation_errors.append("❌ Salah satu jumlah debit atau kredit harus lebih dari 0")
            
            if jumlah_debit_single > 0 and jumlah_kredit_single > 0 and jumlah_debit_single != jumlah_kredit_single:
                validation_errors.append("❌ Jumlah debit dan kredit harus sama")
            
            for error in validation_errors:
                st.error(error)
            
            # TAMPILKAN TOTAL
            st.write("---")
            col_total1, col_total2 = st.columns(2)
            with col_total1:
                st.metric("Total Debit", f"Rp {format_rupiah(jumlah_debit_single)}")
            with col_total2:
                st.metric("Total Kredit", f"Rp {format_rupiah(jumlah_kredit_single)}")
            
            # STATUS KESEIMBANGAN
            if jumlah_debit_single == jumlah_kredit_single and jumlah_debit_single > 0:
                st.success("✅ Transaksi seimbang")
            elif jumlah_debit_single > 0 or jumlah_kredit_single > 0:
                if jumlah_debit_single != jumlah_kredit_single:
                    st.warning("⚠️ Jumlah debit dan kredit belum sama")
            
            tambah_single_submit = st.form_submit_button("Tambah Transaksi Single Entry")
        
        # LOGIKA SINGLE ENTRY
        if tambah_single_submit:
            # Auto-balance jika diperlukan
            if jumlah_debit_single > 0 and jumlah_kredit_single == 0:
                jumlah_kredit_single = jumlah_debit_single
                st.info(f"✅ Jumlah kredit disetarakan dengan debit: Rp {format_rupiah(jumlah_kredit_single)}")
            elif jumlah_kredit_single > 0 and jumlah_debit_single == 0:
                jumlah_debit_single = jumlah_kredit_single
                st.info(f"✅ Jumlah debit disetarakan dengan kredit: Rp {format_rupiah(jumlah_debit_single)}")
            
            # Validasi final
            if akun_debit_single == akun_kredit_single:
                st.error("Transaksi gagal: Akun debit dan kredit tidak boleh sama")
            elif jumlah_debit_single != jumlah_kredit_single:
                st.error(f"Transaksi gagal: Debit (Rp {format_rupiah(jumlah_debit_single)}) dan Kredit (Rp {format_rupiah(jumlah_kredit_single)}) tidak sama")
            elif jumlah_debit_single == 0 and jumlah_kredit_single == 0:
                st.error("Transaksi gagal: Jumlah tidak boleh 0")
            else:
                # Gunakan nomor transaksi yang sama untuk satu transaksi
                nomor = st.session_state.transaction_counter
                
                # Tambahkan transaksi
                row = {
                    "No": nomor, 
                    "Tanggal": tanggal_single, 
                    "Akun Debit": akun_debit_single,
                    "Debit (Rp)": jumlah_debit_single, 
                    "Akun Kredit": akun_kredit_single,
                    "Kredit (Rp)": jumlah_kredit_single
                }
                
                st.session_state.df_jurnal_umum = pd.concat([
                    st.session_state.df_jurnal_umum, 
                    pd.DataFrame([row])
                ], ignore_index=True)
                
                # Increment transaction counter
                st.session_state.transaction_counter += 1
                
                auto_save()
                update_sistem_dengan_struktur_baru()
                st.success("✅ Transaksi berhasil ditambahkan!")
                st.rerun()
    
    with tab2:
        st.write("### 🔸 Transaksi Double Entry - Manual Mode")
        st.info("Input setiap entry secara manual, sistem akan validasi keseimbangan")
        
        # Input dasar double entry
        tanggal_double = st.date_input("Tanggal Transaksi", key="tanggal_double")
        keterangan_double = st.text_input("Keterangan Transaksi", placeholder="Contoh: Pembelian kendaraan dengan uang muka dan utang bank", key="keterangan_double")
        
        # Form untuk tambah satu entry double
        with st.form("form_single_entry_double"):
            st.write("**Tambah Entry Baru:**")
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                akun_double = st.selectbox("Pilih Akun", daftar_akun, key="akun_double_new")
            
            with col2:
                tipe_double = st.selectbox("Tipe", ["Debit", "Kredit"], key="tipe_double_new")
            
            with col3:
                jumlah_str_double = st.text_input("Jumlah", placeholder="1.000.000", key="jumlah_double_new")
            
            tambah_entry_double = st.form_submit_button("➕ Tambah Entry")
        
        # Proses tambah entry double
        if tambah_entry_double:
            if jumlah_str_double:
                jumlah_double = parse_rupiah(jumlah_str_double)
                if jumlah_double > 0:
                    new_entry = {
                        "akun": akun_double,
                        "tipe": tipe_double,
                        "jumlah": jumlah_double,
                        "jumlah_str": jumlah_str_double
                    }
                    st.session_state.double_entries_simple.append(new_entry)
                    st.success(f"Entry {tipe_double} {akun_double} sebesar Rp {format_rupiah(jumlah_double)} ditambahkan!")
                    st.rerun()
                else:
                    st.error("Jumlah harus lebih dari 0")
            else:
                st.error("Harap isi jumlah")
        
        # Tampilkan entries yang sudah ditambahkan
        if st.session_state.double_entries_simple:
            st.write("### 📋 Entri yang Sudah Ditambahkan:")
            
            total_debit_double = 0
            total_kredit_double = 0
            
            for i, entry in enumerate(st.session_state.double_entries_simple):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{entry['akun']}**")
                
                with col2:
                    if entry['tipe'] == 'Debit':
                        st.write(f"💳 Debit: Rp {format_rupiah(entry['jumlah'])}")
                        total_debit_double += entry['jumlah']
                    else:
                        st.write(f"🏦 Kredit: Rp {format_rupiah(entry['jumlah'])}")
                        total_kredit_double += entry['jumlah']
                
                with col3:
                    st.write(f"`{entry['tipe']}`")
                
                with col4:
                    if st.button("🗑️", key=f"hapus_simple_{i}"):
                        st.session_state.double_entries_simple.pop(i)
                        st.rerun()
            
            # Validasi keseimbangan
            st.write("---")
            col_total1, col_total2 = st.columns(2)
            with col_total1:
                st.metric("Total Debit", f"Rp {format_rupiah(total_debit_double)}")
            with col_total2:
                st.metric("Total Kredit", f"Rp {format_rupiah(total_kredit_double)}")
            
            if abs(total_debit_double - total_kredit_double) <= 1:
                st.success("✅ Transaksi seimbang!")
                
                # Tombol simpan final double entry
                if st.button("💾 Simpan Semua Entri sebagai Satu Transaksi Double", type="primary", key="simpan_double"):
                    # Konversi ke format yang compatible
                    entries_for_system = []
                    for entry in st.session_state.double_entries_simple:
                        if entry['tipe'] == 'Debit':
                            entries_for_system.append({
                                "akun": entry['akun'],
                                "debit": entry['jumlah'],
                                "kredit": 0
                            })
                        else:
                            entries_for_system.append({
                                "akun": entry['akun'], 
                                "debit": 0,
                                "kredit": entry['jumlah']
                            })
                    
                    # Gunakan fungsi yang sudah diperbaiki
                    success, message = tambah_transaksi_double_entry(
                        tanggal_double, 
                        keterangan_double, 
                        entries_for_system
                    )
                    
                    if success:
                        st.success(message)
                        st.session_state.double_entries_simple = []
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.error(f"❌ Transaksi tidak seimbang! Selisih: Rp {format_rupiah(abs(total_debit_double - total_kredit_double))}")
        
        else:
            st.info("Belum ada entri. Tambah entri di atas.")
    
    # Tampilkan dataframe jurnal umum dengan format yang diperbaiki
    st.write("### 📋 Daftar Jurnal Umum")
    
    if not st.session_state.df_jurnal_umum.empty:
        # Format tampilan dengan nomor yang konsisten
        df_tampil = st.session_state.df_jurnal_umum.copy()
        
        # Format angka sebagai Rupiah
        def format_angka(x):
            if pd.isna(x) or x == 0:
                return "0"
            return f"Rp {x:,.0f}".replace(",", ".")
        
        if 'Debit (Rp)' in df_tampil.columns:
            df_tampil['Debit (Rp)'] = df_tampil['Debit (Rp)'].apply(format_angka)
        if 'Kredit (Rp)' in df_tampil.columns:
            df_tampil['Kredit (Rp)'] = df_tampil['Kredit (Rp)'].apply(format_angka)
        
        # Tampilkan tabel tanpa index
        st.dataframe(df_tampil, use_container_width=True, hide_index=True)
        
        # Hitung total - gunakan data asli (bukan yang sudah diformat)
        total_debit = st.session_state.df_jurnal_umum["Debit (Rp)"].sum()
        total_kredit = st.session_state.df_jurnal_umum["Kredit (Rp)"].sum()
        
        st.write("### 💰 Total Jurnal Umum")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Debit", f"Rp {total_debit:,.0f}")
        with col2:
            st.metric("Total Kredit", f"Rp {total_kredit:,.0f}")
        
        # Validasi keseimbangan
        if abs(total_debit - total_kredit) < 1:
            st.success("✅ Semua transaksi SEIMBANG")
        else:
            st.error(f"❌ Transaksi TIDAK SEIMBANG - Selisih: Rp {abs(total_debit - total_kredit):,.0f}")
        
        # Opsi hapus transaksi
        with st.expander("🗑️ Hapus Transaksi"):
            st.warning("Hati-hati! Tindakan ini tidak dapat dibatalkan.")
            
            # Buat pilihan transaksi berdasarkan nomor unik
            transaksi_unik = st.session_state.df_jurnal_umum["No"].unique()
            transaksi_options = []
            
            for no in transaksi_unik:
                transaksi_data = st.session_state.df_jurnal_umum[st.session_state.df_jurnal_umum["No"] == no]
                if len(transaksi_data) == 1:
                    # Single entry
                    row = transaksi_data.iloc[0]
                    desc = f"No {no} - {row['Akun Debit']} vs {row['Akun Kredit']} - Rp {row['Debit (Rp)']:,.0f}"
                else:
                    # Double entry - ambil deskripsi dari entri pertama
                    first_row = transaksi_data.iloc[0]
                    desc = f"No {no} - Double Entry ({len(transaksi_data)} entri) - Rp {transaksi_data['Debit (Rp)'].sum():,.0f}"
                transaksi_options.append(desc)
            
            if transaksi_options:
                transaksi_hapus = st.selectbox("Pilih transaksi untuk dihapus:", transaksi_options, key="hapus_select")
                password_hapus = st.text_input("Password Admin", type="password", key="hapus_pass")
                
                if st.button("Hapus Transaksi Terpilih", type="secondary", key="hapus_btn"):
                    # Extract transaction number
                    transaction_no = int(transaksi_hapus.split("No ")[1].split(" -")[0])
                    success, message = delete_transaction(transaction_no, password_hapus)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.info("Tidak ada transaksi untuk dihapus")
    
    else:
        st.info("Belum ada transaksi jurnal umum. Silakan tambah transaksi di atas.")
   
    

elif selected == "Penjualan & Pembelian":
    st.subheader("💰 Sistem Penjualan & Pembelian")
    st.markdown(f"**Periode:** {st.session_state.periode_sekarang}")
    
    # Inisialisasi session state jika belum ada
    if "df_penjualan" not in st.session_state:
        st.session_state.df_penjualan = pd.DataFrame(
            columns=["No", "Tanggal", "Keterangan", "Barang", "Jumlah", "Harga Jual", "Total Penjualan", "HPP", "Total HPP"]
        )
    
    if "df_pembelian" not in st.session_state:
        st.session_state.df_pembelian = pd.DataFrame(
            columns=["No", "Tanggal", "Keterangan", "Barang", "Jumlah", "Harga Beli", "Total Pembelian"]
        )
    
    if "df_persediaan" not in st.session_state:
        st.session_state.df_persediaan = pd.DataFrame({
            "Barang": ["Ayam Jago", "Ayam Broiler", "Telur Ayam"],
            "Stok Awal": [0, 0, 0],
            "Pembelian": [0, 0, 0],
            "Penjualan": [0, 0, 0],
            "Stok Akhir": [0, 0, 0],
            "Harga Rata-rata": [0, 0, 0],
            "Total Nilai": [0, 0, 0]
        })
    
    # Tab untuk Penjualan dan Pembelian
    tab1, tab2 = st.tabs(["📦 Penjualan", "🛒 Pembelian"])
    
    with tab1:
        st.write("### 📦 Form Penjualan")
        
        with st.form("form_penjualan"):
            col1, col2 = st.columns(2)
            
            with col1:
                tanggal_penjualan = st.date_input("Tanggal Penjualan")
                barang_penjualan = st.selectbox("Barang", ["Ayam Jago", "Ayam Broiler", "Telur Ayam"])
                jumlah_penjualan = st.number_input("Jumlah Unit", min_value=1, value=1, key="jml_penjualan")
                
            with col2:
                harga_jual = st.number_input("Harga Jual per Unit (Rp)", min_value=0, value=10000, key="harga_jual")
                akun_debit_penjualan = st.selectbox("Akun Penerimaan", ["Kas", "Piutang Usaha"], key="akun_debit_jual")
                keterangan_penjualan = st.text_input("Keterangan Penjualan", "Penjualan kepada pelanggan")
            
            # Cek stok tersedia
            stok_tersedia = cek_stok_barang(barang_penjualan)
            st.info(f"Stok {barang_penjualan} yang tersedia: {stok_tersedia} unit")
            
            # Hitung total
            total_penjualan = jumlah_penjualan * harga_jual
            hpp_per_unit = st.session_state.df_persediaan[
                st.session_state.df_persediaan["Barang"] == barang_penjualan
            ]["Harga Rata-rata"].iloc[0] if not st.session_state.df_persediaan.empty else 0
            total_hpp = jumlah_penjualan * hpp_per_unit
            
            st.write(f"**Total Penjualan:** Rp {total_penjualan:,}")
            st.write(f"**HPP per Unit:** Rp {hpp_per_unit:,}")
            st.write(f"**Total HPP:** Rp {total_hpp:,}")
            st.write(f"**Laba Kotor:** Rp {total_penjualan - total_hpp:,}")
            
            submit_penjualan = st.form_submit_button("✅ Catat Penjualan")
        
        if submit_penjualan:
            if jumlah_penjualan > stok_tersedia:
                st.error(f"Stok tidak mencukupi! Stok tersedia: {stok_tersedia} unit")
            else:
                try:
                    # 1. Tambahkan ke jurnal umum (4 entri)
                    success_jurnal = tambah_penjualan_ke_jurnal_umum(
                        tanggal_penjualan, 
                        keterangan_penjualan, 
                        akun_debit_penjualan, 
                        total_penjualan, 
                        total_hpp
                    )
                    
                    if success_jurnal:
                        # 2. Update persediaan
                        success_persediaan = update_persediaan_setelah_penjualan(
                            barang_penjualan, 
                            jumlah_penjualan, 
                            hpp_per_unit, 
                            tanggal_penjualan, 
                            keterangan_penjualan
                        )
                        
                        if success_persediaan:
                            # 3. Tambahkan ke dataframe penjualan
                            new_entry = {
                                "No": len(st.session_state.df_penjualan) + 1,
                                "Tanggal": tanggal_penjualan,
                                "Keterangan": keterangan_penjualan,
                                "Barang": barang_penjualan,
                                "Jumlah": jumlah_penjualan,
                                "Harga Jual": harga_jual,
                                "Total Penjualan": total_penjualan,
                                "HPP": hpp_per_unit,
                                "Total HPP": total_hpp
                            }
                            
                            st.session_state.df_penjualan = pd.concat([
                                st.session_state.df_penjualan,
                                pd.DataFrame([new_entry])
                            ], ignore_index=True)
                            
                            st.success("✅ Penjualan berhasil dicatat dan persediaan diperbarui!")
                            st.rerun()
                        else:
                            st.error("Gagal update persediaan")
                    else:
                        st.error("Gagal mencatat jurnal penjualan")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab2:
     st.write("### 🛒 Form Pembelian")
    
    with st.form("form_pembelian", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            tanggal_pembelian = st.date_input("Tanggal Pembelian", key="tanggal_pembelian")
            barang_pembelian = st.selectbox("Barang", ["Ayam Jago", "Ayam Broiler", "Telur Ayam"], key="barang_beli")
            jumlah_pembelian = st.number_input("Jumlah Unit", min_value=1, value=1, key="jml_pembelian")
            
        with col2:
            harga_beli = st.number_input("Harga Beli per Unit (Rp)", min_value=0, value=8000, key="harga_beli")
            akun_kredit_pembelian = st.selectbox("Akun Pembayaran", ["Kas", "Utang Usaha"], key="akun_kredit_beli")
            keterangan_pembelian = st.text_input("Keterangan Pembelian", "Pembelian dari supplier", key="keterangan_beli")
        
        total_pembelian = jumlah_pembelian * harga_beli
        st.write(f"**Total Pembelian:** Rp {total_pembelian:,}")
        
        submit_pembelian = st.form_submit_button("✅ Catat Pembelian")
    
    if submit_pembelian:
        # Validasi input
        if jumlah_pembelian <= 0:
            st.error("Jumlah pembelian harus lebih dari 0")
        elif harga_beli <= 0:
            st.error("Harga beli harus lebih dari 0")
        else:
            success = proses_pembelian_diperbaiki(
                tanggal_pembelian,
                barang_pembelian,
                jumlah_pembelian,
                harga_beli,
                akun_kredit_pembelian,
                keterangan_pembelian
            )
            if success:
                st.rerun()
        
        
    # Halaman Buku Besar
# Di bagian tampilan Buku Besar, ganti dengan kode ini:
elif selected == "Buku Besar":
    st.subheader("Buku Besar 📚")
    st.markdown(f"**Periode:** {st.session_state.periode_sekarang}")
    
    # Update buku besar per akun dengan error handling
    try:
        with st.spinner("Memperbarui buku besar..."):
            update_buku_besar_per_akun()
    except Exception as e:
        st.error(f"Error saat memperbarui buku besar: {str(e)}")
        st.info("Silakan coba refresh halaman atau tambah transaksi di Jurnal Umum terlebih dahulu.")
    
    # Tampilkan informasi sumber data
    st.info("""
    **Buku Besar ini menggabungkan data dari:**
    - ✅ **Jurnal Umum** - Transaksi harian
    - ✅ **Jurnal Penyesuaian** - Penyesuaian periode  
    - ✅ **Jurnal Penutup** - Penutupan periode
    """)
    
    if "buku_besar_per_akun" not in st.session_state or not st.session_state.buku_besar_per_akun:
        st.info("Buku Besar masih kosong. Silakan tambah transaksi di Jurnal Umum terlebih dahulu.")
        
        # Debug information
        with st.expander("🔧 Debug Information"):
            st.write("Session State Keys:", [k for k in st.session_state.keys() if 'jurnal' in k or 'buku' in k])
            if "df_jurnal_umum" in st.session_state:
                st.write("Jurnal Umum data:", len(st.session_state.df_jurnal_umum))
            if "df_jurnal_penyesuaian" in st.session_state:
                st.write("Jurnal Penyesuaian data:", len(st.session_state.df_jurnal_penyesuaian))
        
        st.stop()
    
    buku_besar_per_akun = st.session_state.buku_besar_per_akun
    
    # Tampilkan setiap akun dalam expander
    for akun in sorted(buku_besar_per_akun.keys()):
        df_akun = buku_besar_per_akun[akun]
        
        with st.expander(f"**{akun}** - {len(df_akun)} transaksi", expanded=False):
            if not df_akun.empty:
                # Header informasi akun
                saldo_akhir = float(df_akun["Saldo (Rp)"].iloc[-1])
                total_debit = float(df_akun["Debit (Rp)"].sum())
                total_kredit = float(df_akun["Kredit (Rp)"].sum())
                
                col_info1, col_info2, col_info3, col_info4 = st.columns(4)
                with col_info1:
                    st.metric("Total Debit", f"Rp {total_debit:,.0f}")
                with col_info2:
                    st.metric("Total Kredit", f"Rp {total_kredit:,.0f}")
                with col_info3:
                    st.metric("Saldo Akhir", f"Rp {saldo_akhir:,.0f}")
                with col_info4:
                    status = "Debit" if saldo_akhir > 0 else "Kredit" if saldo_akhir < 0 else "Nol"
                    st.metric("Posisi", status)
                
                # Tampilkan tabel transaksi
                st.write("### 📋 Detail Transaksi")
                
                # Buat copy untuk tampilan dengan format yang aman
                df_tampil = df_akun.copy()
                
                # Format kolom numerik
                df_tampil["Debit (Rp)"] = df_tampil["Debit (Rp)"].apply(lambda x: f"Rp {x:,.0f}")
                df_tampil["Kredit (Rp)"] = df_tampil["Kredit (Rp)"].apply(lambda x: f"Rp {x:,.0f}")
                df_tampil["Saldo (Rp)"] = df_tampil["Saldo (Rp)"].apply(lambda x: f"Rp {x:,.0f}")
                
                # Tampilkan tabel
                st.dataframe(
                    df_tampil[["No", "Tanggal", "Sumber", "Keterangan", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)"]],
                    use_container_width=True,
                    hide_index=True
                )
                
                
elif selected == "Neraca Saldo":
    st.subheader("Neraca Saldo 📊")
    st.markdown(f"**Periode:** {st.session_state.periode_sekarang}")
    
    # Update neraca saldo terlebih dahulu
    try:
        update_buku_besar_per_akun()
    except Exception as e:
        st.error(f"Error saat memperbarui neraca saldo: {str(e)}")
    
    # Tampilkan neraca saldo
    if "df_neraca_saldo" in st.session_state and not st.session_state.df_neraca_saldo.empty:
        st.write("### 📋 Daftar Neraca Saldo")
        
        # Buat copy untuk tampilan dengan format yang aman
        df_tampil = st.session_state.df_neraca_saldo.copy()
        
        # Format kolom numerik sebagai Rupiah
        def format_rupiah_tampil(x):
            try:
                if pd.isna(x) or x == 0 or x == "":
                    return "0"
                if isinstance(x, (int, float)):
                    return f"Rp {x:,.0f}".replace(",", ".")
                return str(x)
            except:
                return str(x)
        
        # Terapkan format hanya pada kolom numerik
        if 'Debit (Rp)' in df_tampil.columns:
            df_tampil['Debit (Rp)'] = df_tampil['Debit (Rp)'].apply(format_rupiah_tampil)
        if 'Kredit (Rp)' in df_tampil.columns:
            df_tampil['Kredit (Rp)'] = df_tampil['Kredit (Rp)'].apply(format_rupiah_tampil)
        if 'Saldo (Rp)' in df_tampil.columns:
            df_tampil['Saldo (Rp)'] = df_tampil['Saldo (Rp)'].apply(format_rupiah_tampil)
        
        # Tampilkan tabel
        st.dataframe(df_tampil, use_container_width=True, hide_index=True)
        
        # Hitung total dari data asli (bukan yang sudah diformat)
        df_asli = st.session_state.df_neraca_saldo
        total_debit = 0
        total_kredit = 0
        
        # Hitung total hanya dari baris yang bukan TOTAL
        for _, row in df_asli.iterrows():
            if row["Nama Akun"] != "TOTAL":
                try:
                    total_debit += float(row["Debit (Rp)"]) if pd.notna(row["Debit (Rp)"]) else 0
                    total_kredit += float(row["Kredit (Rp)"]) if pd.notna(row["Kredit (Rp)"]) else 0
                except:
                    continue
        
        # Tampilkan total
        st.write("### 💰 Total Neraca Saldo")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Debit", f"Rp {total_debit:,.0f}")
        with col2:
            st.metric("Total Kredit", f"Rp {total_kredit:,.0f}")
        
        # Validasi keseimbangan
        selisih = abs(total_debit - total_kredit)
        if selisih < 1:
            st.success("✅ Neraca Saldo SEIMBANG")
        else:
            st.error(f"❌ Neraca Saldo TIDAK SEIMBANG - Selisih: Rp {selisih:,.0f}")
            
        # Informasi tambahan
        with st.expander("ℹ️ Informasi Neraca Saldo"):
            st.write("""
            **Neraca Saldo** adalah daftar yang memuat saldo-saldo dari semua akun dalam buku besar 
            pada suatu periode tertentu. Neraca saldo berfungsi untuk:
            
            - Memastikan keseimbangan antara total debit dan kredit
            - Sebagai dasar untuk menyusun laporan keuangan
            - Memverifikasi keakuratan pencatatan transaksi
            
            **Catatan:** Neraca saldo ini sudah termasuk penyesuaian jika ada.
            """)
            
    else:
        st.info("""
        **Belum ada data neraca saldo.**
        
        **Untuk membuat neraca saldo:**
        1. Tambahkan transaksi di menu **Jurnal Umum**
        2. Jika diperlukan, buat penyesuaian di menu **Jurnal Penyesuaian**
        3. Neraca saldo akan otomatis terbentuk dari data transaksi yang sudah dicatat
        
        **Pastikan:** 
        - Minimal sudah ada satu transaksi di Jurnal Umum
        - Semua transaksi sudah seimbang (debit = kredit)
        """)
        
        # Tombol untuk memaksa pembaruan
        if st.button("🔄 Refresh Neraca Saldo"):
            try:
                update_buku_besar_per_akun()
                st.rerun()
            except Exception as e:
                st.error(f"Gagal refresh: {str(e)}")
                
                
elif selected == "Jurnal Penyesuaian":
    st.subheader("Jurnal Penyesuaian 🔧")
    st.markdown(f"**Periode:** {st.session_state.periode_sekarang}")
    
    # Inisialisasi dataframe jika belum ada
    if "df_jurnal_penyesuaian" not in st.session_state:
        st.session_state.df_jurnal_penyesuaian = pd.DataFrame(
            columns=["No", "Tanggal", "Keterangan", "Akun Debit", "Debit (Rp)", "Akun Kredit", "Kredit (Rp)"]
        )
    
    # DAFTAR AKUN UNTUK PENYESUAIAN
    daftar_akun_penyesuaian = [
        "Kas", "Persediaan", "Perlengkapan", "Peralatan", "Kendaraan", "Tanah", 
        "Piutang", "Aset biologis", "Utang Usaha", "Utang Bank", "Utang Gaji",
        "Modal", "Penjualan", "Pendapatan", "Harga Pokok Penjualan",
        "Beban listrik dan air", "Beban transportasi", "Beban gaji", "Beban Lain",
        "Beban Penyusutan", "Beban Perlengkapan", "Pendapatan Diterima Dimuka",
        "Beban Dibayar Dimuka", "Piutang Pendapatan", "Utang Beban"
    ]
    
    # FORM TAMBAH JURNAL PENYESUAIAN
    with st.form("form_tambah_jurnal_penyesuaian", clear_on_submit=True):
        st.write("### 📝 Tambah Jurnal Penyesuaian")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tanggal_penyesuaian = st.date_input("Tanggal Penyesuaian", key="tanggal_penyesuaian")
            keterangan_penyesuaian = st.text_input("Keterangan Penyesuaian", 
                                                 placeholder="Contoh: Penyusutan peralatan, Pemakaian perlengkapan, dll",
                                                 key="keterangan_penyesuaian")
            
        with col2:
            st.write("")  # Spacer
        
        st.write("---")
        st.write("**Entri Penyesuaian:**")
        
        col_debit, col_kredit = st.columns(2)
        
        with col_debit:
            st.subheader("🚹 Debit")
            akun_debit_penyesuaian = st.selectbox("Akun Debit", daftar_akun_penyesuaian, key="debit_penyesuaian")
            jumlah_debit_str_penyesuaian = st.text_input("Jumlah Debit (Rp)", value="", 
                                                       placeholder="Contoh: 1.000.000", 
                                                       key="debit_input_penyesuaian")
            jumlah_debit_penyesuaian = parse_rupiah(jumlah_debit_str_penyesuaian) if jumlah_debit_str_penyesuaian else 0
        
        with col_kredit:
            st.subheader("🚺 Kredit") 
            akun_kredit_penyesuaian = st.selectbox("Akun Kredit", daftar_akun_penyesuaian, key="kredit_penyesuaian")
            jumlah_kredit_str_penyesuaian = st.text_input("Jumlah Kredit (Rp)", value="", 
                                                        placeholder="Contoh: 1.000.000", 
                                                        key="kredit_input_penyesuaian")
            jumlah_kredit_penyesuaian = parse_rupiah(jumlah_kredit_str_penyesuaian) if jumlah_kredit_str_penyesuaian else 0
        
        # VALIDASI
        validation_errors = []
        
        if akun_debit_penyesuaian == akun_kredit_penyesuaian:
            validation_errors.append("❌ Akun debit dan kredit tidak boleh sama")
        
        if jumlah_debit_penyesuaian == 0 and jumlah_kredit_penyesuaian == 0:
            validation_errors.append("❌ Salah satu jumlah debit atau kredit harus lebih dari 0")
        
        if jumlah_debit_penyesuaian > 0 and jumlah_kredit_penyesuaian > 0 and jumlah_debit_penyesuaian != jumlah_kredit_penyesuaian:
            validation_errors.append("❌ Jumlah debit dan kredit harus sama")
        
        for error in validation_errors:
            st.error(error)
        
        # TAMPILKAN TOTAL
        st.write("---")
        col_total1, col_total2 = st.columns(2)
        with col_total1:
            st.metric("Total Debit", f"Rp {format_rupiah(jumlah_debit_penyesuaian)}")
        with col_total2:
            st.metric("Total Kredit", f"Rp {format_rupiah(jumlah_kredit_penyesuaian)}")
        
        # STATUS KESEIMBANGAN
        if jumlah_debit_penyesuaian == jumlah_kredit_penyesuaian and jumlah_debit_penyesuaian > 0:
            st.success("✅ Penyesuaian seimbang")
        elif jumlah_debit_penyesuaian > 0 or jumlah_kredit_penyesuaian > 0:
            if jumlah_debit_penyesuaian != jumlah_kredit_penyesuaian:
                st.warning("⚠️ Jumlah debit dan kredit belum sama")
        
        tambah_penyesuaian_submit = st.form_submit_button("Tambah Jurnal Penyesuaian")
    
    # PROSES TAMBAH JURNAL PENYESUAIAN
    if tambah_penyesuaian_submit:
        # Auto-balance jika diperlukan
        if jumlah_debit_penyesuaian > 0 and jumlah_kredit_penyesuaian == 0:
            jumlah_kredit_penyesuaian = jumlah_debit_penyesuaian
            st.info(f"✅ Jumlah kredit disetarakan dengan debit: Rp {format_rupiah(jumlah_kredit_penyesuaian)}")
        elif jumlah_kredit_penyesuaian > 0 and jumlah_debit_penyesuaian == 0:
            jumlah_debit_penyesuaian = jumlah_kredit_penyesuaian
            st.info(f"✅ Jumlah debit disetarakan dengan kredit: Rp {format_rupiah(jumlah_debit_penyesuaian)}")
        
        # Validasi final
        if akun_debit_penyesuaian == akun_kredit_penyesuaian:
            st.error("Penyesuaian gagal: Akun debit dan kredit tidak boleh sama")
        elif jumlah_debit_penyesuaian != jumlah_kredit_penyesuaian:
            st.error(f"Penyesuaian gagal: Debit (Rp {format_rupiah(jumlah_debit_penyesuaian)}) dan Kredit (Rp {format_rupiah(jumlah_kredit_penyesuaian)}) tidak sama")
        elif jumlah_debit_penyesuaian == 0 and jumlah_kredit_penyesuaian == 0:
            st.error("Penyesuaian gagal: Jumlah tidak boleh 0")
        else:
            # Tambahkan ke dataframe jurnal penyesuaian
            nomor = len(st.session_state.df_jurnal_penyesuaian) + 1
            row = {
                "No": nomor, 
                "Tanggal": tanggal_penyesuaian,
                "Keterangan": keterangan_penyesuaian,
                "Akun Debit": akun_debit_penyesuaian,
                "Debit (Rp)": jumlah_debit_penyesuaian, 
                "Akun Kredit": akun_kredit_penyesuaian,
                "Kredit (Rp)": jumlah_kredit_penyesuaian
            }
            
            st.session_state.df_jurnal_penyesuaian = pd.concat([
                st.session_state.df_jurnal_penyesuaian, 
                pd.DataFrame([row])
            ], ignore_index=True)
            
            # Update sistem setelah penyesuaian
            update_buku_besar_per_akun()
            auto_save()
            st.success("✅ Jurnal penyesuaian berhasil ditambahkan!")
            st.rerun()
    
    # TAMPILKAN TABEL JURNAL PENYESUAIAN
    st.write("### 📋 Daftar Jurnal Penyesuaian")
    
    if not st.session_state.df_jurnal_penyesuaian.empty:
        # Buat copy untuk tampilan dengan format yang aman
        df_tampil_penyesuaian = st.session_state.df_jurnal_penyesuaian.copy()
        
        # Format angka sebagai Rupiah
        if 'Debit (Rp)' in df_tampil_penyesuaian.columns:
            df_tampil_penyesuaian['Debit (Rp)'] = df_tampil_penyesuaian['Debit (Rp)'].apply(format_angka)
        if 'Kredit (Rp)' in df_tampil_penyesuaian.columns:
            df_tampil_penyesuaian['Kredit (Rp)'] = df_tampil_penyesuaian['Kredit (Rp)'].apply(format_angka)
        
        # Tampilkan tabel
        st.dataframe(df_tampil_penyesuaian, use_container_width=True, hide_index=True)
        
        # Hitung total - gunakan data asli (bukan yang sudah diformat)
        total_debit_penyesuaian = st.session_state.df_jurnal_penyesuaian["Debit (Rp)"].sum()
        total_kredit_penyesuaian = st.session_state.df_jurnal_penyesuaian["Kredit (Rp)"].sum()
        
        st.write("### 💰 Total Jurnal Penyesuaian")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Debit", f"Rp {total_debit_penyesuaian:,.0f}")
        with col2:
            st.metric("Total Kredit", f"Rp {total_kredit_penyesuaian:,.0f}")
        
        # Validasi keseimbangan
        if abs(total_debit_penyesuaian - total_kredit_penyesuaian) < 1:
            st.success("✅ Semua penyesuaian SEIMBANG")
        else:
            st.error(f"❌ Penyesuaian TIDAK SEIMBANG - Selisih: Rp {abs(total_debit_penyesuaian - total_kredit_penyesuaian):,.0f}")
        
        # Opsi hapus penyesuaian
        with st.expander("🗑️ Hapus Jurnal Penyesuaian"):
            st.warning("Hati-hati! Tindakan ini tidak dapat dibatalkan.")
            
            # Buat pilihan penyesuaian berdasarkan nomor
            penyesuaian_options = []
            for _, row in st.session_state.df_jurnal_penyesuaian.iterrows():
                desc = f"No {row['No']} - {row['Keterangan']} - Debit: {row['Akun Debit']} Kredit: {row['Akun Kredit']}"
                penyesuaian_options.append(desc)
            
            if penyesuaian_options:
                penyesuaian_hapus = st.selectbox("Pilih jurnal penyesuaian untuk dihapus:", penyesuaian_options, key="hapus_penyesuaian_select")
                password_hapus_penyesuaian = st.text_input("Password Admin", type="password", key="hapus_penyesuaian_pass")
                
                if st.button("Hapus Jurnal Penyesuaian Terpilih", type="secondary", key="hapus_penyesuaian_btn"):
                    # Extract transaction number
                    try:
                        transaction_no = int(penyesuaian_hapus.split("No ")[1].split(" -")[0])
                        
                        # Verifikasi password admin
                        if password_hapus_penyesuaian != "admin123":
                            st.error("Password salah!")
                        else:
                            # Hapus jurnal penyesuaian
                            df_awal = st.session_state.df_jurnal_penyesuaian
                            df_setelah_hapus = df_awal[df_awal["No"] != transaction_no].copy()
                            
                            # Reset nomor urut
                            df_setelah_hapus = df_setelah_hapus.reset_index(drop=True)
                            df_setelah_hapus["No"] = range(1, len(df_setelah_hapus) + 1)
                            
                            st.session_state.df_jurnal_penyesuaian = df_setelah_hapus
                            
                            # Update sistem
                            update_buku_besar_per_akun_fixed()
                            auto_save()
                            
                            st.success("Jurnal penyesuaian berhasil dihapus!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error menghapus penyesuaian: {str(e)}")
            else:
                st.info("Tidak ada jurnal penyesuaian untuk dihapus")
    
    else:
        st.info("Belum ada jurnal penyesuaian. Silakan tambah jurnal penyesuaian di atas.")
    
    # INFORMASI TENTANG JURNAL PENYESUAIAN
    with st.expander("ℹ️ Tentang Jurnal Penyesuaian"):
        st.write("""
        **Jurnal Penyesuaian** dibuat untuk:
        
        **1. Beban yang masih harus dibayar (Accrued Expenses)**
        - Beban yang sudah terjadi tetapi belum dicatat
        - Contoh: Beban gaji yang belum dibayar
        
        **2. Pendapatan yang masih harus diterima (Accrued Revenues)**
        - Pendapatan yang sudah earned tetapi belum dicatat
        - Contoh: Pendapatan jasa yang belum ditagih
        
        **3. Beban dibayar di muka (Prepaid Expenses)**
        - Beban yang sudah dibayar tetapi belum menjadi beban
        - Contoh: Asuransi dibayar di muka
        
        **4. Pendapatan diterima di muka (Unearned Revenues)**
        - Pendapatan yang sudah diterima tetapi belum earned
        - Contoh: Sewa diterima di muka
        
        **5. Penyusutan (Depreciation)**
        - Alokasi biaya aset tetap selama masa manfaat
        - Contoh: Penyusutan peralatan, kendaraan
        
        **6. Pemakaian perlengkapan (Supplies Used)**
        - Perlengkapan yang sudah terpakai selama periode
        """)
            
            
# Di bagian Laporan Laba Rugi
# Halaman Laporan Laba Rugi
elif selected == 'Laporan Laba Rugi':
    tampilkan_laporan_laba_rugi()

# Halaman Laporan Perubahan Modal
elif selected == 'Laporan Perubahan Modal':
    tampilkan_laporan_perubahan_modal()

# Halaman Laporan Posisi Keuangan
elif selected == 'Laporan Posisi Keuangan':
    tampilkan_laporan_posisi_keuangan()

        # Halaman Jurnal Penutup
elif selected == 'Jurnal Penutup':
    st.subheader('Jurnal Penutup 🛑')
    st.markdown(f"**Periode:** {st.session_state.periode_sekarang}")
    
    # Daftar akun untuk penutupan (fokus pada akun nominal)
    daftar_akun_penutup = [
        "Pendapatan Jasa", "Pendapatan Lain", "Beban Gaji", "Beban Sewa", 
        "Beban Listrik dan Air", "Beban Transportasi", "Beban Lain-lain",
        "Ikhtisar Laba Rugi", "Modal"
    ]
    
    # Form jurnal penutup dengan format debit-kredit
    with st.form("form_tambah_jurnal_penutup", clear_on_submit=True):
        st.write("### Tambah Jurnal Penutup")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tanggal = st.date_input("Tanggal Penutupan")
            keterangan = st.text_input("Keterangan Penutupan", placeholder="Contoh: Penutupan pendapatan jasa")
            
        with col2:
            st.write("")  # Spacer
        
        st.write("---")
        st.write("**Entri Penutupan:**")
        
        col_debit, col_kredit = st.columns(2)
        
        with col_debit:
            st.subheader("🚹 Debit")
            akun_debit = st.selectbox("Akun Debit", daftar_akun_penutup, key="debit_penutup")
            jumlah_debit = st.number_input("Jumlah Debit (Rp)", min_value=0, step=1000, key="jumlah_debit_penutup")
        
        with col_kredit:
            st.subheader("🚺 Kredit") 
            akun_kredit = st.selectbox("Akun Kredit", daftar_akun_penutup, key="kredit_penutup")
            jumlah_kredit = st.number_input("Jumlah Kredit (Rp)", min_value=0, step=1000, key="jumlah_kredit_penutup")
        
        # Validasi
        validation_errors = []
        
        if akun_debit == akun_kredit:
            validation_errors.append("❌ Akun debit dan kredit tidak boleh sama")
        
        if jumlah_debit == 0 and jumlah_kredit == 0:
            validation_errors.append("❌ Salah satu jumlah debit atau kredit harus lebih dari 0")
        
        if jumlah_debit > 0 and jumlah_kredit > 0 and jumlah_debit != jumlah_kredit:
            validation_errors.append("❌ Jumlah debit dan kredit harus sama")
        
        for error in validation_errors:
            st.error(error)
        
        # Tampilkan total
        st.write("---")
        col_total1, col_total2 = st.columns(2)
        with col_total1:
            st.metric("Total Debit Penutupan", f"Rp {jumlah_debit:,.0f}")
        with col_total2:
            st.metric("Total Kredit Penutupan", f"Rp {jumlah_kredit:,.0f}")
        
        # Status keseimbangan
        if jumlah_debit == jumlah_kredit and jumlah_debit > 0:
            st.success("✅ Penutupan seimbang")
        elif jumlah_debit > 0 or jumlah_kredit > 0:
            if jumlah_debit != jumlah_kredit:
                st.error("❌ Penutupan tidak seimbang")
        
        tambah_penutup = st.form_submit_button("Tambah Jurnal Penutup")
    
    # Proses tambah jurnal penutup
    if tambah_penutup:
        # Auto-balance jika diperlukan
        if jumlah_debit > 0 and jumlah_kredit == 0:
            jumlah_kredit = jumlah_debit
        elif jumlah_kredit > 0 and jumlah_debit == 0:
            jumlah_debit = jumlah_kredit
        
        # Validasi final
        if akun_debit == akun_kredit:
            st.error("Transaksi gagal: Akun debit dan kredit tidak boleh sama")
        elif jumlah_debit != jumlah_kredit:
            st.error(f"Transaksi gagal: Debit (Rp {jumlah_debit:,.0f}) dan Kredit (Rp {jumlah_kredit:,.0f}) tidak sama")
        elif jumlah_debit == 0 and jumlah_kredit == 0:
            st.error("Transaksi gagal: Jumlah tidak boleh 0")
        else:
            # Tambahkan ke dataframe
            nomor = len(st.session_state.df_jurnal_penutup) + 1
            row = {
                "No": nomor, 
                "Tanggal": tanggal,
                "Keterangan": keterangan,
                "Akun Debit": akun_debit,
                "Debit (Rp)": jumlah_debit, 
                "Akun Kredit": akun_kredit,
                "Kredit (Rp)": jumlah_kredit
            }
            
            st.session_state.df_jurnal_penutup = pd.concat([
                st.session_state.df_jurnal_penutup, 
                pd.DataFrame([row])
            ], ignore_index=True)
            
            # Update sistem setelah penutupan
            update_setelah_penutupan()
            st.success("✅ Jurnal penutup berhasil ditambahkan!")
            st.rerun()
    
    # Tampilkan tabel jurnal penutup
    st.write("### 📋 Daftar Jurnal Penutup")
    
    if not st.session_state.df_jurnal_penutup.empty:
        # Hitung total debit dan kredit penutupan
        total_debit_penutup = st.session_state.df_jurnal_penutup["Debit (Rp)"].sum()
        total_kredit_penutup = st.session_state.df_jurnal_penutup["Kredit (Rp)"].sum()
        
        # Tampilkan tabel
        st.dataframe(st.session_state.df_jurnal_penutup.style.format({
            "Debit (Rp)": "Rp {:,.0f}",
            "Kredit (Rp)": "Rp {:,.0f}"
        }), use_container_width=True)
        
        # Tampilkan total penutupan
        st.write("### 💰 Total Jurnal Penutup")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Debit Penutupan", f"Rp {total_debit_penutup:,.0f}")
        with col2:
            st.metric("Total Kredit Penutupan", f"Rp {total_kredit_penutup:,.0f}")
        
        # Validasi keseimbangan
        if abs(total_debit_penutup - total_kredit_penutup) < 1:
            st.success("✅ Semua jurnal penutup SEIMBANG")
        else:
            st.error(f"❌ Jurnal penutup TIDAK SEIMBANG - Selisih: Rp {abs(total_debit_penutup - total_kredit_penutup):,.0f}")
        
        # Tombol untuk menyelesaikan periode
        st.write("### 🎯 Akhiri Periode")
        st.warning("""
        **Peringatan:** Tindakan ini akan mengakhiri periode saat ini dan memulai periode baru.
        - Semua data jurnal penutup akan diproses
        - Neraca saldo setelah penutup akan disimpan sebagai neraca saldo periode sebelumnya
        - Data transaksi periode ini akan diarsipkan
        - Periode baru akan dimulai dengan saldo awal dari periode sebelumnya
        """)
        
        if st.button("✅ Akhiri Periode dan Mulai Periode Baru", type="primary"):
            if akhiri_periode():
                st.success("✅ Periode berhasil diakhiri! Silakan mulai periode baru.")
                st.rerun()
            
    else:
        st.info("Belum ada jurnal penutup. Silakan tambah jurnal penutup di atas.")

            # Halaman Neraca Saldo Setelah Penutup    
elif selected == 'Neraca Saldo Setelah Penutup':
    st.subheader('Neraca Saldo Setelah Penutup ✅')
    st.markdown(f"**Periode:** {st.session_state.periode_sekarang}")
    
    # Update data terlebih dahulu
    update_setelah_penutupan()
    
    if "df_neraca_saldo_setelah_penutup" in st.session_state and not st.session_state.df_neraca_saldo_setelah_penutup.empty:
        st.write("### 📊 Neraca Saldo Setelah Penutupan")
        st.info("""
        **Keterangan:** 
        - Neraca ini hanya menampilkan akun-akun riil (aset, kewajiban, modal)
        - Akun-akun nominal (pendapatan dan beban) telah dinolkan melalui jurnal penutup
        - Neraca ini akan menjadi neraca saldo periode sebelumnya untuk periode berikutnya
        """)
        
        # Tampilkan tabel
        st.dataframe(st.session_state.df_neraca_saldo_setelah_penutup.style.format({
            "Debit (Rp)": "Rp {:,.0f}",
            "Kredit (Rp)": "Rp {:,.0f}"
        }), use_container_width=True)
        
        # Hitung total
        total_debit = st.session_state.df_neraca_saldo_setelah_penutup["Debit (Rp)"].sum()
        total_kredit = st.session_state.df_neraca_saldo_setelah_penutup["Kredit (Rp)"].sum()
        
        st.metric("Total Debit", f"Rp {total_debit:,.0f}")
        st.metric("Total Kredit", f"Rp {total_kredit:,.0f}")
        
        if abs(total_debit - total_kredit) < 1:
            st.success("✅ Neraca saldo setelah penutup SEIMBANG")
        else:
            st.error(f"❌ Neraca saldo setelah penutup TIDAK SEIMBANG - Selisih: Rp {abs(total_debit - total_kredit):,.0f}")
            
        # Informasi untuk periode berikutnya
        st.write("### 🔄 Informasi untuk Periode Berikutnya")
        st.success(f"""
        **Neraca saldo ini akan menjadi saldo awal untuk periode berikutnya.**
        
        Saldo awal periode {st.session_state.periode_sekarang}:
        - **Total Debit:** Rp {total_debit:,.0f}
        - **Total Kredit:** Rp {total_kredit:,.0f}
        """)
        
    else:
        st.info("""
        **Belum ada neraca saldo setelah penutup.**
        
        **Untuk membuat neraca saldo setelah penutup:**
        1. Selesaikan semua transaksi di Jurnal Umum
        2. Buat penyesuaian di Jurnal Penyesuaian (jika diperlukan)
        3. Buat jurnal penutup di Jurnal Penutup
        4. Neraca saldo setelah penutup akan otomatis terisi
        """)
        
        

elif selected == "Kartu persediaan":
    st.subheader("📦 Kartu Persediaan")
    
    # HAPUS FORM PEMBELIAN DARI SINI
    # Hanya tampilkan data persediaan, tidak ada form input
    
    # Tampilkan data persediaan
    st.write("### 📊 Data Persediaan")
    
    if not st.session_state.df_persediaan.empty:
        total_nilai = st.session_state.df_persediaan["Total Nilai"].sum()
        st.metric("Total Nilai Persediaan", f"Rp {total_nilai:,}")
        
        st.dataframe(st.session_state.df_persediaan, use_container_width=True)
        
        # Grafik sederhana
        st.write("### 📈 Grafik Persediaan")
        if not st.session_state.df_persediaan.empty:
            chart_data = st.session_state.df_persediaan.set_index("Barang")["Stok Akhir"]
            st.bar_chart(chart_data)
    
    # Tampilkan riwayat pembelian (hanya tampilan, tidak ada form)
    st.write("### 📋 Riwayat Pembelian")
    
    if not st.session_state.df_pembelian.empty:
        st.dataframe(st.session_state.df_pembelian, use_container_width=True)
    else:
        st.info("Belum ada data pembelian.")
        
        
elif selected == "Kartu Persediaan Detail":
    display_kartu_persediaan_detail_per_barang()
        

        # Halaman Unduh Laporan Keuangan
elif selected == 'Unduh Laporan Keuangan':
    st.subheader('Unduh Laporan Keuangan 📥') 
    st.markdown("Pada halaman ini, Anda dapat mengunduh laporan keuangan dalam bentuk file Excel.")
    
    # Informasi data yang tersedia
    st.write("### 📊 Data yang Tersedia untuk Download")
    
    data_stats = []
    dataframes_to_check = [
        ("Jurnal Umum", "df_jurnal_umum"),
        ("Jurnal Penyesuaian", "df_jurnal_penyesuaian"),
        ("Buku Besar", "df_buku_besar"),
        ("Neraca Saldo", "df_neraca_saldo"),
        ("Laporan Laba Rugi", "df_laporan_laba_rugi"),
        ("Laporan Perubahan Modal", "df_laporan_perubahan_modal"),
        ("Laporan Posisi Keuangan", "df_laporan_posisi_keuangan"),
        ("Penjualan", "df_penjualan"),
        ("Pembelian", "df_pembelian"),
        ("Persediaan", "df_persediaan")
    ]
    
    for name, key in dataframes_to_check:
        if key in st.session_state and not st.session_state[key].empty:
            row_count = len(st.session_state[key])
            data_stats.append({"Jenis Laporan": name, "Jumlah Data": f"{row_count} baris", "Status": "✅ Tersedia"})
        else:
            data_stats.append({"Jenis Laporan": name, "Jumlah Data": "0 baris", "Status": "❌ Kosong"})
    
    st.dataframe(pd.DataFrame(data_stats), use_container_width=True)
    
    # Tombol download
    st.write("### 💾 Download Semua Data")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🔄 Generate File Excel", type="primary"):
            try:
                with st.spinner("Membuat file Excel..."):
                    buffer = export_to_excel()
                    
                    if buffer is None:
                        st.error("❌ Gagal membuat file: buffer tidak terbentuk")
                    else:
                        buffer_size = buffer.getbuffer().nbytes
                        if buffer_size == 0:
                            st.error("❌ File yang dihasilkan kosong")
                        else:
                            st.success(f"✅ File berhasil dibuat! Ukuran: {buffer_size} bytes")
                            
                            # Tombol download
                            st.download_button(
                                label="📥 Download Laporan Keuangan (Excel)",
                                data=buffer,
                                file_name=f"laporan_keuangan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key="download_main"
                            )
            except Exception as e:
                st.error(f"❌ Error saat generate file: {str(e)}")
    
    with col2:
        if st.button("🆕 Buat Template Kosong"):
            # Buat template Excel kosong
            try:
                buffer_template = BytesIO()
                with pd.ExcelWriter(buffer_template, engine='xlsxwriter') as writer:
                    template_data = {
                        "Keterangan": [
                            "File template laporan keuangan",
                            "Isi dengan data transaksi Anda",
                            f"Dibuat pada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        ]
                    }
                    pd.DataFrame(template_data).to_excel(writer, sheet_name="Panduan", index=False)
                    
                    # Buat sheet kosong untuk setiap jenis laporan
                    sheets = ["Jurnal Umum", "Buku Besar", "Neraca Saldo", "Laporan Laba Rugi"]
                    for sheet in sheets:
                        pd.DataFrame().to_excel(writer, sheet_name=sheet, index=False)
                
                buffer_template.seek(0)
                
                st.download_button(
                    label="📥 Download Template",
                    data=buffer_template,
                    file_name="template_laporan_keuangan.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_template"
                )
            except Exception as e:
                st.error(f"Error membuat template: {str(e)}")
    
    # Troubleshooting section
    with st.expander("🔧 Troubleshooting"):
        st.write("""
        **Jika mengalami masalah dalam download:**
        
        1. **Pastikan ada data** - Beberapa laporan memerlukan data transaksi terlebih dahulu
        2. **Cek koneksi internet** - Untuk download file yang besar
        3. **Clear cache browser** - Jika tombol download tidak berfungsi
        4. **Coba browser berbeda** - Untuk mengatasi masalah kompatibilitas
        
        **Format file yang didukung:**
        - Microsoft Excel (.xlsx)
        - Dapat dibuka dengan Excel, Google Sheets, atau LibreOffice
        """)
        
        # Test export functionality
        if st.button("🧪 Test Export Function"):
            try:
                test_buffer = export_to_excel()
                if test_buffer and test_buffer.getbuffer().nbytes > 0:
                    st.success(f"✅ Test berhasil! Buffer size: {test_buffer.getbuffer().nbytes} bytes")
                else:
                    st.error("❌ Test gagal: buffer kosong")
            except Exception as e:
                st.error(f"❌ Test error: {str(e)}")