import mysql.connector
from colorama import Fore, Style
from tabulate import tabulate
import time
import pyfiglet
import pyttsx3  # Untuk suara pemberitahuan (opsional)

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
        print(f"{Fore.RED}Error: {err}{Fore.RESET}")
        return None

# Fungsi untuk menampilkan tabel dengan tabulate
def print_table(data, headers):
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))

# Fungsi untuk menampilkan banner
def show_banner(text):
    banner = pyfiglet.figlet_format(text, font="slant")
    print(Fore.CYAN + banner + Style.RESET_ALL)

# Fungsi untuk menampilkan pesan sukses
def success_message(message):
    print(f"{Fore.GREEN}{Style.BRIGHT}{message}{Fore.RESET}")

# Fungsi untuk menampilkan loading masuk aplikasi
def loading_message():
    print(f"{Fore.YELLOW}Loading, please wait...{Fore.RESET}")
    time.sleep(2)

# Fungsi untuk menampilkan header aplikasi
def show_header():
    show_banner("LABORATORIUM ABAL-ABAL")

# Fungsi untuk memberikan popup pemberitahuan
def popup_notification(message):
    print(f"{Fore.YELLOW}{Style.BRIGHT}{message}{Fore.RESET}")
    # Opsi: Berikan suara menggunakan pyttsx3 (jika diinginkan)
    engine = pyttsx3.init()
    engine.say(message)
    engine.runAndWait()

# Fungsi untuk login admin
def admin_login():
    print(f"{Fore.CYAN}{Style.BRIGHT}🔒 Admin Login{Style.RESET_ALL}")
    username = input(f"{Fore.MAGENTA}Enter Username: {Fore.RESET}")
    password = input(f"{Fore.MAGENTA}Enter Password: {Fore.RESET}")
    
    # Memeriksa kredensial admin (misalnya admin/password)
    if username == "admin" and password == "password":
        success_message("Login successful!")
        return True
    else:
        print(f"{Fore.RED}Invalid credentials! Please try again.{Fore.RESET}")
        return False

# Fungsi untuk menampilkan menu peminjam
def peminjam_menu():
    menu_data = [
        ["1", "Daftar Sebagai Peminjam"],
        ["2", "Pinjam Barang"],
        ["3", "Lihat Barang Tersedia"],
        ["4", "Kembalikan Barang"],
        ["5", "Back"]
    ]
    print_table(menu_data, ["No", "Option"])
    choice = input(f"{Fore.MAGENTA}Choose an option: {Fore.RESET}")
    return choice

# Fungsi untuk menambah peminjam
def daftar_peminjam():
    nama = input(f"{Fore.CYAN}Masukkan Nama: {Fore.RESET}")
    nim = input(f"{Fore.CYAN}Masukkan NIM: {Fore.RESET}")
    no_telepon = input(f"{Fore.CYAN}Masukkan Nomor Telepon: {Fore.RESET}")
    email = input(f"{Fore.CYAN}Masukkan Email: {Fore.RESET}")
    alamat = input(f"{Fore.CYAN}Masukkan Alamat: {Fore.RESET}")
    
    conn = connect_db()
    if conn is None:
        return  # Kembali jika koneksi gagal
    cursor = conn.cursor()
    cursor.execute("INSERT INTO peminjam (nama, nim, no_telepon, email, alamat) VALUES (%s, %s, %s, %s, %s)", 
                   (nama, nim, no_telepon, email, alamat))
    conn.commit()
    conn.close()
    
    success_message("Peminjam berhasil didaftarkan!")
    popup_notification("Peminjam berhasil didaftarkan!")

# Fungsi untuk meminjam barang
def pinjam_barang():
    print(f"{Fore.YELLOW}Daftar Barang Tersedia:{Fore.RESET}")
    conn = connect_db()
    if conn is None:
        return  # Kembali jika koneksi gagal
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM barang WHERE jumlah > 0")
    barang = cursor.fetchall()
    conn.close()
    print_table(barang, ["ID Barang", "Nama Barang", "Kategori", "Jumlah", "Kondisi"])

    try:
        barang_id = int(input(f"{Fore.CYAN}Masukkan ID Barang yang ingin dipinjam: {Fore.RESET}"))
    except ValueError:
        print(f"{Fore.RED}ID Barang harus berupa angka.{Fore.RESET}")
        return

    nama_peminjam = input(f"{Fore.CYAN}Masukkan Nama Peminjam: {Fore.RESET}")
    nim_peminjam = input(f"{Fore.CYAN}Masukkan NIM Peminjam: {Fore.RESET}")
    tanggal_pinjam = input(f"{Fore.CYAN}Masukkan Tanggal Pinjam (YYYY-MM-DD): {Fore.RESET}")
    kondisi_barang = input(f"{Fore.CYAN}Masukkan Kondisi Barang: {Fore.RESET}")  # New line to get kondisi_barang

    conn = connect_db()
    if conn is None:
        return  # Kembali jika koneksi gagal
    cursor = conn.cursor()

    # Cek apakah peminjam sudah terdaftar
    cursor.execute("SELECT * FROM peminjam WHERE nama = %s AND nim = %s", (nama_peminjam, nim_peminjam))
    peminjam = cursor.fetchone()
    if peminjam is None:
        print(f"{Fore.RED}Peminjam belum terdaftar! Silakan daftar terlebih dahulu.{Fore.RESET}")
        conn.close()
        return

    # Memperbarui jumlah barang
    cursor.execute("UPDATE barang SET jumlah = jumlah - 1 WHERE barang_id = %s AND jumlah > 0", (barang_id,))
    if cursor.rowcount == 0:
        print(f"{Fore.RED}Barang tidak tersedia untuk dipinjam.{Fore.RESET}")
        conn.close()
        return

    # Tambahkan data peminjaman, including kondisi_barang
    cursor.execute("INSERT INTO peminjaman (peminjam_id, barang_id, tanggal_pinjam, kondisi_barang) VALUES (%s, %s, %s, %s)", 
                   (peminjam[0], barang_id, tanggal_pinjam, kondisi_barang))
    conn.commit()
    conn.close()

    success_message("Barang berhasil dipinjam!")
    popup_notification("Barang berhasil dipinjam!")

# Fungsi untuk mencetak struk pengembalian
def print_receipt(peminjaman_id, tanggal_kembali):
    print(f"{Fore.GREEN}=== STRUK PENGEMBALIAN ==={Fore.RESET}")
    print(f"ID Peminjaman: {peminjaman_id}")
    print(f"Tanggal Kembali: {tanggal_kembali}")
    print(f"{Fore.GREEN}=========================={Fore.RESET}")

# Fungsi untuk mengembalikan barang
def kembalikan_barang():
    print(f"{Fore.YELLOW}Daftar Peminjaman Barang yang Belum Dikembalikan:{Fore.RESET}")
    conn = connect_db()
    if conn is None:
        return  # Kembali jika koneksi gagal
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM peminjaman WHERE tanggal_kembali IS NULL")
    peminjaman = cursor.fetchall()
    conn.close()
    
    if not peminjaman:
        print(f"{Fore.RED}Tidak ada peminjaman yang belum dikembalikan.{Fore.RESET}")
        return
    
    print_table(peminjaman, ["Peminjaman ID", "Peminjam ID", "Barang ID", "Tanggal Pinjam","Tanggal Kembali"])
    
    try:
        peminjaman_id = int(input(f"{Fore.CYAN}Masukkan ID Peminjaman yang ingin dikembalikan: {Fore.RESET}"))
    except ValueError:
        print(f"{Fore.RED}ID Peminjaman harus berupa angka.{Fore.RESET}")
        return

    tanggal_kembali = input(f"{Fore.CYAN}Masukkan Tanggal Kembali (YYYY-MM-DD): {Fore.RESET}")
    
    conn = connect_db()
    if conn is None:
        return  # Kembali jika koneksi gagal
    cursor = conn.cursor()
    
    # Memperbarui tanggal kembali
    cursor.execute("UPDATE peminjaman SET tanggal_kembali = %s WHERE peminjaman_id = %s", 
                   (tanggal_kembali, peminjaman_id))
    
    # Menambah jumlah barang
    cursor.execute("UPDATE barang SET jumlah = jumlah + 1 WHERE barang_id = (SELECT barang_id FROM peminjaman WHERE peminjaman_id = %s)", (peminjaman_id,))
    
    conn.commit()
    conn.close()
    
    success_message("Barang berhasil dikembalikan!")
    popup_notification("Barang berhasil dikembalikan!")
    
    # Cetak struk setelah pengembalian
    print_receipt(peminjaman_id, tanggal_kembali)

# Fungsi untuk menampilkan barang yang tersedia
def lihat_barang_tersedia():
    print(f"{Fore.YELLOW}Daftar Barang Tersedia untuk Dipinjam:{Fore.RESET}")
    conn = connect_db()
    if conn is None:
        return  # Kembali jika koneksi gagal
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM barang WHERE jumlah > 0")
    barang = cursor.fetchall()
    conn.close()
    print_table(barang, ["ID Barang", "Nama Barang", "Kategori", "Jumlah", "Kondisi"])

# Fungsi untuk menu admin
def manage_admin():
    menu_data = [
        ["1", "Manage Peminjam"],
        ["2", "Manage Barang"],
        ["3", "Exit"]
    ]
    print_table(menu_data, ["No", "Option"])
    choice = input(f"{Fore.MAGENTA}Choose an option: {Fore.RESET}")
    return choice

# Fungsi untuk manage peminjam (admin)
def manage_peminjam():
    while True:
        menu_data = [
            ["1", "Lihat Daftar Peminjam"],
            ["2", "Hapus Peminjam"],
            ["3", "Back"]
        ]
        print_table(menu_data, ["No", "Option"])
        peminjam_choice = input(f"{Fore.MAGENTA}Choose an option: {Fore.RESET}")

        if peminjam_choice == '1':
            # Menampilkan daftar peminjam
            print(f"{Fore.YELLOW}Daftar Peminjam:{Fore.RESET}")
            conn = connect_db()
            if conn is None:
                return  # Kembali jika koneksi gagal
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM peminjam")
            peminjam = cursor.fetchall()
            conn.close()
            print_table(peminjam, ["ID Peminjam", "Nama", "NIM", "No Telepon", "Email", "Alamat", "Kondisi Barang"])
        
        elif peminjam_choice == '2':
            # Hapus data peminjam berdasarkan ID
            try:
                peminjam_id = int(input(f"{Fore.CYAN}Masukkan ID Peminjam yang ingin dihapus: {Fore.RESET}"))
            except ValueError:
                print(f"{Fore.RED}ID Peminjam harus berupa angka.{Fore.RESET}")
                continue
            
            conn = connect_db()
            if conn is None:
                return  # Kembali jika koneksi gagal
            cursor = conn.cursor()
            cursor.execute("DELETE FROM peminjam WHERE peminjam_id = %s", (peminjam_id,))
            conn.commit()
            conn.close()
            success_message(f"Peminjam dengan ID {peminjam_id} telah dihapus!")
            popup_notification(f"Peminjam dengan ID {peminjam_id} telah dihapus!")

        elif peminjam_choice == '3':
            break  # Kembali ke menu sebelumnya

# Fungsi untuk manage barang (admin)
def manage_barang():
    while True:
        menu_data = [
            ["1", "Lihat Daftar Barang"],
            ["2", "Tambah Barang"],
            ["3", "Update Barang"],
            ["4", "Hapus Barang"],
            ["5", "Back"]
        ]
        print_table(menu_data, ["No", "Option"])
        barang_choice = input(f"{Fore.MAGENTA}Choose an option: {Fore.RESET}")

        if barang_choice == '1':
            print(f"{Fore.YELLOW}Daftar Barang:{Fore.RESET}")
            conn = connect_db()
            if conn is None:
                return  # Kembali jika koneksi gagal
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM barang")
            barang = cursor.fetchall()
            conn.close()
            print_table(barang, ["ID Barang", "Nama Barang", "Kategori", "Jumlah", "Kondisi"])

        elif barang_choice == '2':
            # Menambah barang baru
            nama_barang = input(f"{Fore.CYAN}Masukkan Nama Barang: {Fore.RESET}")
            kategori = input(f"{Fore.CYAN}Masukkan Kategori: {Fore.RESET}")
            try:
                jumlah = int(input(f"{Fore.CYAN}Masukkan Jumlah: {Fore.RESET}"))
            except ValueError:
                print(f"{Fore.RED}Jumlah harus berupa angka.{Fore.RESET}")
                continue
            kondisi = input(f"{Fore.CYAN}Masukkan Kondisi: {Fore.RESET}")
            conn = connect_db()
            if conn is None:
                return  # Kembali jika koneksi gagal
            cursor = conn.cursor()
            cursor.execute("INSERT INTO barang (nama_barang, kategori, jumlah, kondisi) VALUES (%s, %s, %s, %s)", (nama_barang, kategori, jumlah, kondisi))
            conn.commit()
            conn.close()
            success_message("Barang berhasil ditambahkan!")
            popup_notification("Barang berhasil ditambahkan!")

        elif barang_choice == '3':
            # Update barang
            try:
                barang_id = int(input(f"{Fore.CYAN}Masukkan ID Barang yang ingin diubah: {Fore.RESET}"))
            except ValueError:
                print(f"{Fore.RED}ID Barang harus berupa angka.{Fore.RESET}")
                continue
            
            nama_barang = input(f"{Fore.CYAN}Masukkan Nama Barang: {Fore.RESET}")
            kategori = input(f"{Fore.CYAN}Masukkan Kategori: {Fore.RESET}")
            try:
                jumlah = int(input(f"{Fore.CYAN}Masukkan Jumlah: {Fore.RESET}"))
            except ValueError:
                print(f"{Fore.RED}Jumlah harus berupa angka.{Fore.RESET}")
                continue
            kondisi = input(f"{Fore.CYAN}Masukkan Kondisi: {Fore.RESET}")
            conn = connect_db()
            if conn is None:
                return  # Kembali jika koneksi gagal
            cursor = conn.cursor()
            cursor.execute("UPDATE barang SET nama_barang = %s, kategori = %s, jumlah = %s, kondisi = %s WHERE barang_id = %s", (nama_barang, kategori, jumlah, kondisi, barang_id))
            conn.commit()
            conn.close()
            success_message("Barang berhasil diperbarui!")
            popup_notification("Barang berhasil diperbarui!")

        elif barang_choice == '4':
            # Hapus barang
            try:
                barang_id = int(input(f"{Fore.CYAN}Masukkan ID Barang yang ingin dihapus: {Fore.RESET}"))
            except ValueError:
                print(f"{Fore.RED}ID Barang harus berupa angka.{Fore.RESET}")
                continue
            
            conn = connect_db()
            if conn is None:
                return  # Kembali jika koneksi gagal
            cursor = conn.cursor()
            cursor.execute("DELETE FROM barang WHERE barang_id = %s", (barang_id,))
            conn.commit()
            conn.close()
            success_message("Barang berhasil dihapus!")
            popup_notification("Barang berhasil dihapus!")

        elif barang_choice == '5':
            break  # Kembali ke menu admin

# Menu utama aplikasi
def main_menu():
    while True:
        show_header()
        menu_data = [
            ["1", "Peminjam Menu"],
            ["2", "Admin Menu"],
            ["3", "Exit"]
        ]
        print_table(menu_data, ["No", "Option"])
        
        choice = input(f"{Fore.MAGENTA}Pilih menu: {Fore.RESET}")

        if choice == '1':
            while True:
                peminjam_choice = peminjam_menu()
                if peminjam_choice == '1':
                    daftar_peminjam()
                elif peminjam_choice == '2':
                    pinjam_barang()
                elif peminjam_choice == '3':
                    lihat_barang_tersedia()
                elif peminjam_choice == '4':
                    kembalikan_barang()
                elif peminjam_choice == '5':
                    break  # Kembali ke menu utama
                
        elif choice == '2':
            if admin_login():
                while True:
                    admin_choice = manage_admin()
                    if admin_choice == '1':
                        manage_peminjam()
                    elif admin_choice == '2':
                        manage_barang()
                    elif admin_choice == '3':
                        break  # Kembali ke menu utama

        elif choice == '3':
            print(f"{Fore.YELLOW}Terima kasih telah menggunakan aplikasi Laboratorium Abal-Abal!{Fore.RESET}")
            break  # Keluar dari aplikasi

if __name__ == "__main__":
    loading_message()
    main_menu()