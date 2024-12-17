import tkinter as tk
from tkinter import messagebox, simpledialog
import mysql.connector

# Fungsi untuk koneksi ke database
def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="AKUNaku12.",
            database="laboratorium"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")
        return None

# Fungsi untuk menambah peminjam
def daftar_peminjam():
    nama = entry_nama.get()
    nim = entry_nim.get()
    no_telepon = entry_no_telepon.get()
    email = entry_email.get()
    alamat = entry_alamat.get()
    
    if not (nama and nim and no_telepon and email and alamat):
        messagebox.showwarning("Input Kosong", "Semua kolom harus diisi.")
        return

    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO peminjam (nama, nim, no_telepon, email, alamat) VALUES (%s, %s, %s, %s, %s)", 
                (nama, nim, no_telepon, email, alamat)
            )
            conn.commit()
            messagebox.showinfo("Success", "Peminjam berhasil didaftarkan!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")
        finally:
            conn.close()

# Fungsi untuk meminjam barang
def pinjam_barang():
    barang_id = simpledialog.askinteger("Input", "Masukkan ID Barang yang ingin dipinjam:")
    nama_peminjam = entry_nama.get()
    nim_peminjam = entry_nim.get()
    tanggal_pinjam = simpledialog.askstring("Input", "Masukkan Tanggal Pinjam (YYYY-MM-DD):")

    if not (barang_id and nama_peminjam and nim_peminjam and tanggal_pinjam):
        messagebox.showwarning("Input Kosong", "Semua kolom harus diisi.")
        return

    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()

            # Cek apakah peminjam sudah terdaftar
            cursor.execute("SELECT * FROM peminjam WHERE nama = %s AND nim = %s", (nama_peminjam, nim_peminjam))
            peminjam = cursor.fetchone()
            if peminjam is None:
                messagebox.showerror("Error", "Peminjam belum terdaftar! Silakan daftar terlebih dahulu.")
                return

            # Cek dan kurangi jumlah barang
            cursor.execute("UPDATE barang SET jumlah = jumlah - 1 WHERE barang_id = %s AND jumlah > 0", (barang_id,))
            if cursor.rowcount == 0:
                messagebox.showerror("Error", "Barang tidak tersedia untuk dipinjam.")
                return

            # Tambahkan data peminjaman
            cursor.execute(
                "INSERT INTO peminjaman (peminjam_id, barang_id, tanggal_pinjam) VALUES (%s, %s, %s)", 
                (peminjam[0], barang_id, tanggal_pinjam)
            )
            conn.commit()
            messagebox.showinfo("Success", "Barang berhasil dipinjam!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")
        finally:
            conn.close()

# Fungsi untuk mengembalikan barang
def kembalikan_barang():
    peminjaman_id = simpledialog.askinteger("Input", "Masukkan ID Peminjaman yang ingin dikembalikan:")
    tanggal_kembali = simpledialog.askstring("Input", "Masukkan Tanggal Kembali (YYYY-MM-DD):")
    kondisi_barang = simpledialog.askstring("Input", "Masukkan Kondisi Barang saat Dikembalikan:")

    if not (peminjaman_id and tanggal_kembali and kondisi_barang):
        messagebox.showwarning("Input Kosong", "Semua kolom harus diisi.")
        return

    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()

            # Perbarui data peminjaman
            cursor.execute(
                "UPDATE peminjaman SET tanggal_kembali = %s, kondisi_barang = %s WHERE peminjaman_id = %s", 
                (tanggal_kembali, kondisi_barang, peminjaman_id)
            )
            if cursor.rowcount == 0:
                messagebox.showerror("Error", "ID Peminjaman tidak ditemukan.")
                return

            # Tambahkan kembali jumlah barang
            cursor.execute("""
                UPDATE barang SET jumlah = jumlah + 1 
                WHERE barang_id = (SELECT barang_id FROM peminjaman WHERE peminjaman_id = %s)
            """, (peminjaman_id,))
            
            conn.commit()
            messagebox.showinfo("Success", "Barang berhasil dikembalikan!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")
        finally:
            conn.close()

# Fungsi untuk melihat barang yang tersedia
def lihat_barang_tersedia():
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM barang WHERE jumlah > 0")
            barang = cursor.fetchall()
            if not barang:
                messagebox.showinfo("Info", "Tidak ada barang yang tersedia untuk dipinjam.")
            else:
                barang_list = "\n".join([f"ID: {b[0]}, Nama: {b[1]}, Jumlah: {b[3]}, Kondisi: {b[4]}" for b in barang])
                messagebox.showinfo("Barang Tersedia", barang_list)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")
        finally:
            conn.close()

# Menu utama aplikasi
def main_menu():
    root.title("Aplikasi Laboratorium Abal-Abal")
    tk.Label(root, text="Menu Utama", font=("Arial", 16)).pack()
    tk.Button(root, text="Daftar Peminjam", command=daftar_peminjam).pack()
    tk.Button(root, text="Pinjam Barang", command=pinjam_barang).pack()
    tk.Button(root, text="Kembalikan Barang", command=kembalikan_barang).pack()
    tk.Button(root, text="Lihat Barang Tersedia", command=lihat_barang_tersedia).pack()
    tk.Button(root, text="Exit", command=root.quit).pack()

# Inisialisasi Tkinter
root = tk.Tk()

# Kolom input untuk nama dan NIM peminjam
tk.Label(root, text="Nama:").pack()
entry_nama = tk.Entry(root)
entry_nama.pack()

tk.Label(root, text="NIM:").pack()
entry_nim = tk.Entry(root)
entry_nim.pack()

tk.Label(root, text="No Telepon:").pack()
entry_no_telepon = tk.Entry(root)
entry_no_telepon.pack()

tk.Label(root, text="Email:").pack()
entry_email = tk.Entry(root)
entry_email.pack()

tk.Label(root, text="Alamat:").pack()
entry_alamat = tk.Entry(root)
entry_alamat.pack()

main_menu()
root.mainloop()
