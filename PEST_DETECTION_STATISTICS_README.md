# Dashboard Statistik Deteksi Hama

## Gambaran Umum

Fitur ini menambahkan statistik deteksi hama yang komprehensif ke dashboard monitoring, memungkinkan pengguna untuk memvisualisasikan dan menganalisis data deteksi hama dari perangkat IoT secara real-time.

## Fitur

### 1. Statistik Deteksi Hama Real-time
- **Chart Langsung**: Bar chart menampilkan jumlah deteksi hama dari waktu ke waktu
- **Pemilihan Periode**: Pilih antara 7, 14, atau 30 hari data
- **Auto-refresh**: Chart diperbarui otomatis setiap 30 detik
- **Multiple Kelas Hama**: Dukungan untuk berbagai jenis hama (wereng, ulat, kutu, dll.)

### 2. Manajemen Data Deteksi
- **Model DetectionData**: Model Django khusus untuk menyimpan hasil deteksi
- **Integrasi MQTT**: Ingestion data otomatis dari perangkat IoT
- **Analisis Statistik**: Statistik agregat dan breakdown harian

### 3. Endpoint API
- `/api/detection-statistics/`: Mendapatkan data chart dan statistik ringkasan
- `/api/latest-detection/`: Mendapatkan data deteksi terbaru

## Skema Database

### Model DetectionData
```python
class DetectionData(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    total_detections = models.IntegerField(default=0)
    class_counts = models.JSONField(default=dict)
    detection_details = models.JSONField(default=list)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Completed')
```

### Deskripsi Field
| Field | Type | Deskripsi |
|-------|------|-----------|
| `timestamp` | DateTimeField | Kapan deteksi terjadi |
| `total_detections` | IntegerField | Total jumlah hama yang terdeteksi |
| `class_counts` | JSONField | Jumlah setiap kelas hama (contoh: {"wereng": 5, "ulat": 3}) |
| `detection_details` | JSONField | Informasi deteksi detail dengan skor confidence |
| `latitude` | FloatField | GPS latitude tempat deteksi terjadi |
| `longitude` | FloatField | GPS longitude tempat deteksi terjadi |
| `status` | CharField | Status deteksi (Completed, Failed, dll.) |

## Integrasi MQTT

### Struktur Topic
- **Topic Utama**: `alat/data/detection`
- **Format Data**: JSON dengan hasil deteksi

### Format Pesan
```json
{
  "timestamp": "2024-01-15 14:30:00",
  "type": "detection",
  "total_detections": 8,
  "class_counts": {
    "wereng": 5,
    "ulat": 3
  },
  "detection_details": [
    {
      "class": "wereng",
      "confidence": 0.85,
      "bbox": [100, 100, 200, 200]
    }
  ],
  "latitude": -6.2088,
  "longitude": 106.8456,
  "status": "Completed"
}
```

## Fitur Dashboard

### 1. Chart Deteksi Hama
- **Tipe Chart**: Bar chart
- **Sumbu X**: Tanggal
- **Sumbu Y**: Jumlah hama yang terdeteksi
- **Legenda**: Warna berbeda untuk setiap kelas hama
- **Responsive**: Menyesuaikan ukuran layar

### 2. Statistik Ringkasan
- **Total Deteksi**: Jumlah sesi deteksi
- **Total Hama**: Total jumlah hama individual yang terdeteksi
- **Pemilih Periode**: Pilih rentang data (7, 14, 30 hari)
- **Tombol Refresh**: Refresh chart manual

### 3. Update Real-time
- **Data Deteksi**: Diperbarui setiap 10 detik
- **Data Chart**: Diperbarui setiap 30 detik
- **Perubahan Periode**: Refresh chart langsung

## Endpoint API

### GET /api/detection-statistics/
Mengembalikan data chart dan statistik ringkasan.

**Parameter:**
- `days` (opsional): Jumlah hari yang disertakan (default: 7)

**Response:**
```json
{
  "chart_data": {
    "labels": ["2024-01-10", "2024-01-11", "2024-01-12"],
    "datasets": [
      {
        "label": "wereng",
        "data": [5, 3, 7],
        "backgroundColor": "#FF6384",
        "borderColor": "#FF6384"
      }
    ]
  },
  "summary": {
    "total_detections": 15,
    "total_pests": 45,
    "class_counts": {"wereng": 25, "ulat": 20},
    "period_days": 7
  }
}
```

### GET /api/latest-detection/
Mengembalikan data deteksi terbaru.

**Response:**
```json
{
  "total_detections": 8,
  "class_counts": {"wereng": 5, "ulat": 3},
  "timestamp": "2024-01-15 14:30:00",
  "status": "Completed",
  "latitude": -6.2088,
  "longitude": 106.8456
}
```

## Testing

### 1. Simulasi Data Deteksi
Jalankan script test untuk mensimulasikan data deteksi hama:
```bash
cd system-dashboard/app
python test_detection_data.py
```

Ini akan:
- Terhubung ke MQTT broker
- Mengirim 5 pesan deteksi simulasi
- Menyertakan kelas hama dan jumlah acak
- Menambahkan koordinat GPS yang realistis

### 2. Testing Manual
1. Jalankan Django development server
2. Navigasi ke dashboard
3. Jalankan script simulasi deteksi
4. Amati update chart secara real-time
5. Test pemilihan periode yang berbeda

## Konfigurasi

### Pengaturan MQTT
Update konfigurasi MQTT di `mqtt_client.py`:
```python
self.broker = "88.222.241.209"
self.port = 1883
self.detection_topic = "alat/data/detection"
self.username = "ahp123"
self.password = "kiki"
```

### Pengaturan Chart
Modifikasi tampilan chart di `index.html`:
- Warna untuk kelas hama yang berbeda
- Interval update
- Dimensi dan styling chart

## Troubleshooting

### Masalah Umum

1. **Tidak Ada Data Chart**
   - Periksa koneksi MQTT
   - Verifikasi data deteksi sedang dipublish
   - Periksa console browser untuk error JavaScript

2. **Chart Tidak Update**
   - Verifikasi endpoint API berfungsi
   - Periksa konektivitas jaringan
   - Pastikan MQTT client berjalan

3. **Masalah Database**
   - Jalankan migrasi: `python manage.py migrate`
   - Periksa koneksi database
   - Verifikasi field model sudah benar

### Langkah Debug

1. **Periksa Pesan MQTT**
   ```bash
   python Tests/test-mqtt-detection.py
   ```

2. **Test Endpoint API**
   ```bash
   curl http://localhost:8000/api/detection-statistics/
   curl http://localhost:8000/api/latest-detection/
   ```

3. **Periksa Log Django**
   ```bash
   python manage.py runserver --verbosity=2
   ```

## Pengembangan Masa Depan

1. **Analitik Lanjutan**
   - Analisis tren
   - Pemodelan prediktif
   - Pola musiman

2. **Fitur Export**
   - Export CSV
   - Laporan PDF
   - Notifikasi email

3. **Visualisasi Geografis**
   - Heat maps
   - Analisis berbasis lokasi
   - Tracking GPS

4. **Sistem Alert**
   - Alert berbasis threshold
   - Notifikasi Email/SMS
   - Aturan alert kustom

## Dependencies

- Django 3.2+
- Chart.js 3.0+
- paho-mqtt
- PostgreSQL/SQLite

## Instalasi

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Jalankan Migrasi**
   ```bash
   python manage.py makemigrations dashboard
   python manage.py migrate
   ```

3. **Jalankan MQTT Client**
   ```bash
   python manage.py start_mqtt
   ```

4. **Jalankan Development Server**
   ```bash
   python manage.py runserver
   ```

## Dukungan

Untuk masalah dan pertanyaan:
1. Periksa bagian troubleshooting
2. Review log MQTT
3. Periksa log error Django
4. Verifikasi response endpoint API 