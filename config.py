# ========================================
# Konfigurasi Face Recognition System
# ========================================

# Pengaturan Kamera - AUTO DETECTION
# Sistem akan otomatis prioritaskan Insta360 Link 2 jika tersedia
CAMERA_INDEX = "auto"        # "auto" = otomatis detect Insta360 Link 2, atau angka untuk manual
CAMERA_WIDTH = "auto"        # "auto" = otomatis sesuai kamera, atau angka manual
CAMERA_HEIGHT = "auto"       # "auto" = otomatis sesuai kamera, atau angka manual

# Pengaturan Face Recognition
TOLERANCE = 0.5           # Sensitivitas pengenalan (0.0-1.0)
                         # 0.4 = Ketat, 0.6 = Longgar
FRAME_RESIZE = 0.25      # Skala resize untuk performa (0.1-1.0)
                         # 0.15 = Cepat, 0.5 = Akurat

# Pengaturan Folder
FACES_DIR = "faces"       # Folder database wajah

# Pengaturan Tampilan
WINDOW_NAME = "Insta360 Link 2 - Face Recognition"
FONT_SCALE = 0.7         # Ukuran font nama
FONT_THICKNESS = 1       # Ketebalan font
BOX_THICKNESS = 2        # Ketebalan kotak deteksi

# Warna (format BGR)
COLOR_KNOWN = (0, 255, 0)     # Hijau untuk wajah dikenal
COLOR_UNKNOWN = (0, 0, 255)   # Merah untuk wajah tidak dikenal
COLOR_TEXT = (255, 255, 255)  # Putih untuk text

# Pengaturan Performance
MAX_FACES_TO_PROCESS = 5      # Maksimal wajah yang diproses per frame
DETECTION_FREQUENCY = 1       # Deteksi setiap N frame (1 = setiap frame)

# Debug Mode
DEBUG_MODE = False            # True untuk menampilkan info debug
SHOW_FPS = False             # True untuk menampilkan FPS counter