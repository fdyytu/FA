# Scripts Directory

Folder ini berisi semua script utility yang digunakan dalam project, diorganisir berdasarkan fungsinya:

## 📁 Struktur Folder

### `/database/`
Script-script yang berhubungan dengan database management, setup, seeding, dan testing koneksi.

### `/admin/`
Script-script untuk admin management, pembuatan admin, dan maintenance admin system.

### `/setup/`
Script-script untuk setup dan konfigurasi aplikasi.

### `/testing/`
Script-script untuk testing berbagai komponen aplikasi.

## 🚀 Cara Penggunaan

Semua script dapat dijalankan dari root directory project:

```bash
# Contoh menjalankan script database
python scripts/database/setup_database.py

# Contoh menjalankan script admin
python scripts/admin/create_first_admin.py
```

## 📝 Catatan

- Pastikan virtual environment sudah aktif sebelum menjalankan script
- Beberapa script memerlukan konfigurasi database yang sudah setup
- Lihat README di masing-masing folder untuk detail lebih lanjut
