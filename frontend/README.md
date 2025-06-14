# FA PPOB Frontend

Frontend aplikasi FA PPOB (Payment Point Online Bank) yang dibangun dengan HTML, CSS (Tailwind), dan JavaScript vanilla.

## Fitur

### 🔐 Autentikasi
- Login dan Register dengan validasi real-time
- Token-based authentication
- Password toggle visibility
- Form validation dengan feedback visual

### 📊 Dashboard
- Overview saldo wallet
- Statistik transaksi
- Transaksi terbaru
- Quick access ke layanan PPOB

### 💰 Wallet Management
- Cek saldo wallet
- Top up via transfer bank manual
- Top up via Midtrans (kartu kredit/debit)
- Transfer antar pengguna
- Riwayat transaksi wallet

### 🏪 Layanan PPOB
- Pulsa (dengan pilihan produk)
- Token Listrik PLN
- Tagihan PDAM
- Tagihan Internet
- Tagihan BPJS
- Tagihan Multifinance
- Inquiry sebelum pembayaran

### 📋 Riwayat Transaksi
- Gabungan transaksi PPOB dan wallet
- Filter berdasarkan jenis, status, dan tanggal
- Pagination
- Detail transaksi
- Export ke PDF/Excel/CSV

### 👤 Profil Pengguna
- Edit informasi profil
- Ubah password
- Statistik akun
- Pengaturan notifikasi

## Struktur File

```
frontend/
├── index.html              # Landing page
├── login.html              # Halaman login/register
├── dashboard.html          # Dashboard utama
├── wallet.html             # Manajemen wallet
├── history.html            # Riwayat transaksi
├── profile.html            # Profil pengguna
├── assets/
│   ├── css/
│   │   └── style.css       # Custom CSS (opsional)
│   └── js/
│       ├── api.js          # API client dan utilities
│       ├── auth.js         # Autentikasi
│       ├── dashboard.js    # Dashboard functionality
│       ├── wallet.js       # Wallet management
│       ├── history.js      # Transaction history
│       └── profile.js      # Profile management
└── README.md               # Dokumentasi ini
```

## Teknologi yang Digunakan

- **HTML5** - Struktur halaman
- **Tailwind CSS** - Framework CSS utility-first
- **JavaScript (ES6+)** - Logika aplikasi
- **Font Awesome** - Icons
- **Google Fonts (Inter)** - Typography

## Setup dan Instalasi

1. **Clone atau download** project ini
2. **Konfigurasi API endpoint** di `assets/js/api.js`:
   ```javascript
   const API_BASE_URL = 'http://localhost:8000/api/v1';
   ```
3. **Buka file HTML** di browser atau setup web server

### Menggunakan Live Server (Recommended)

```bash
# Install live-server globally
npm install -g live-server

# Jalankan di direktori frontend
live-server
```

### Menggunakan Python HTTP Server

```bash
# Python 3
python -m http.server 8080

# Python 2
python -m SimpleHTTPServer 8080
```

## Konfigurasi

### API Configuration
Edit file `assets/js/api.js` untuk mengubah endpoint API:

```javascript
const API_BASE_URL = 'http://your-api-domain.com/api/v1';
```

### Authentication
Aplikasi menggunakan JWT token yang disimpan di localStorage:
- Token otomatis disertakan dalam setiap request
- Auto-redirect ke login jika token expired
- Token dihapus saat logout

## Fitur JavaScript

### API Client
- Centralized API calls dengan error handling
- Automatic token management
- Request/response interceptors

### Utilities
- Currency formatting (IDR)
- Date formatting (Indonesian locale)
- Form validation
- Status badges
- Alert modals

### Real-time Features
- Auto-refresh data setiap 30-60 detik
- Real-time form validation
- Loading states untuk semua actions

## Responsive Design

Aplikasi fully responsive dengan breakpoints:
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

## Browser Support

- Chrome 60+
- Firefox 60+
- Safari 12+
- Edge 79+

## Security Features

- XSS protection dengan proper escaping
- CSRF protection via API
- Secure token storage
- Input validation dan sanitization

## Performance

- Lazy loading untuk data berat
- Efficient DOM manipulation
- Minimal external dependencies
- Optimized images dan assets

## Customization

### Mengubah Tema Warna
Edit Tailwind classes di HTML files atau tambahkan custom CSS:

```css
:root {
  --primary-color: #4f46e5;
  --secondary-color: #6b7280;
}
```

### Menambah Layanan PPOB Baru
1. Tambahkan service type di `dashboard.js`
2. Update icon mapping di `api.js`
3. Tambahkan handling di modal PPOB

### Custom Validation Rules
Extend validation di `api.js`:

```javascript
const customRules = {
  field_name: {
    required: true,
    pattern: /your-regex/,
    message: 'Custom error message'
  }
};
```

## Troubleshooting

### CORS Issues
Jika mengalami CORS error:
1. Pastikan backend mengizinkan origin frontend
2. Gunakan proxy atau disable CORS di development

### Token Issues
Jika login tidak persistent:
1. Check localStorage di browser dev tools
2. Pastikan token format sesuai dengan backend

### API Connection
Jika tidak bisa connect ke API:
1. Verify API_BASE_URL di `api.js`
2. Check network tab di browser dev tools
3. Pastikan backend server running

## Development

### Adding New Pages
1. Buat file HTML baru
2. Include `api.js` dan file JS spesifik
3. Tambahkan navigation links
4. Update authentication check

### Adding New Features
1. Extend API client di `api.js`
2. Buat JavaScript module baru
3. Update UI components
4. Add proper error handling

## Production Deployment

### Optimizations
- Minify CSS dan JavaScript
- Optimize images
- Enable gzip compression
- Setup CDN untuk assets

### Environment Variables
Gunakan environment-specific config:

```javascript
const config = {
  development: {
    API_BASE_URL: 'http://localhost:8000/api/v1'
  },
  production: {
    API_BASE_URL: 'https://api.yoursite.com/api/v1'
  }
};
```

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

MIT License - see LICENSE file for details.

## Support

Untuk bantuan dan pertanyaan:
- Email: support@fappob.com
- Documentation: [Link to docs]
- Issues: [GitHub Issues]
