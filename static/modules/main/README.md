# Main Dashboard Modules

## Struktur Modul Main (Maksimal 50 baris per file)

### API Services
- `api/main-api-service.js` - Service API untuk dashboard stats dan transaksi

### UI Components  
- `ui/main-ui-service.js` - Service UI untuk stats cards dan transaksi

### Bridge Services
- `bridge/main-bridge-service.js` - Service bridge untuk integrasi modul

### Main Files
- `main-controller.js` - Controller utama
- `main-module-loader.js` - Module loader

## Cara Penggunaan

1. Load module loader terlebih dahulu:
```html
<script src="/static/modules/main/main-module-loader.js"></script>
```

2. Gunakan file modular sebagai pengganti:
```html
<script src="/static/admin/dashboard/dashboard_main.js"></script>
```

## File yang Diganti

- `dashboard_main.js` (275 baris) → Dipecah menjadi 5+ modul kecil
- Backup tersimpan di `dashboard_main_backup.js`

## Keuntungan Pemecahan

1. **Maintainability**: Setiap modul fokus pada satu tanggung jawab
2. **Reusability**: Modul dapat digunakan ulang di bagian lain
3. **Testability**: Mudah untuk testing individual
4. **Performance**: Lazy loading modules
5. **Collaboration**: Tim dapat bekerja pada modul berbeda

## Dependencies

- Shared modules (auth, ui, api services)
- Bridge compatibility untuk integrasi modul lain

## Features

- Auto-refresh setiap 15 detik
- Bridge integration untuk Discord stats
- Fallback mechanism jika bridge tidak tersedia

## Status: ✅ SELESAI
Dashboard Main berhasil dipecah dari 275 baris menjadi 5+ modul kecil.
