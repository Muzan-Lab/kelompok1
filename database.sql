-- Buat tabel peminjam
CREATE TABLE IF NOT EXISTS peminjam (
    peminjam_id INT AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    nim VARCHAR(20) NOT NULL,
    no_telepon VARCHAR(15) NOT NULL,
    email VARCHAR(100) NOT NULL,
    alamat TEXT NOT NULL
);

-- Buat tabel barang
CREATE TABLE IF NOT EXISTS barang (
    barang_id INT AUTO_INCREMENT PRIMARY KEY,
    nama_barang VARCHAR(100) NOT NULL,
    kategori VARCHAR(50) NOT NULL,
    jumlah INT NOT NULL,
    kondisi VARCHAR(50) NOT NULL
);

-- Buat tabel peminjaman
CREATE TABLE IF NOT EXISTS peminjaman (
    peminjaman_id INT AUTO_INCREMENT PRIMARY KEY,
    peminjam_id INT NOT NULL,
    barang_id INT NOT NULL,
    tanggal_pinjam DATE NOT NULL,
    tanggal_kembali DATE,
    FOREIGN KEY (peminjam_id) REFERENCES peminjam(peminjam_id),
    FOREIGN KEY (barang_id) REFERENCES barang(barang_id)
);

INSERT INTO barang (barang_id, nama_barang, kategori, jumlah, kondisi) VALUES
(1, 'MikroTik', 'Fasilitas Praktikum', 10, 'Baik'),
(2, 'Infocus', 'Fasilitas Prodi', 2, 'Baik');