import cv2
import face_recognition
import numpy as np
import os
import time
from config import *   

print("Memuat database wajah dari folder /faces...")
known_faces = []
known_names = []

if not os.path.exists(FACES_DIR):
    os.makedirs(FACES_DIR)
    print(f"Folder '{FACES_DIR}' dibuat. Silakan tambahkan foto referensi wajah.")

face_count = 0
for filename in os.listdir(FACES_DIR):
    if filename.lower().endswith((".jpg", ".png", ".jpeg")):
        filepath = os.path.join(FACES_DIR, filename)
        
        if DEBUG_MODE:
            print(f"Memproses: {filename}")
            
        image = face_recognition.load_image_file(filepath)
        encodings = face_recognition.face_encodings(image)
        
        if len(encodings) > 0:
            known_faces.append(encodings[0])
            name = os.path.splitext(filename)[0].replace("_", " ").title()
            known_names.append(name)
            face_count += 1
            if DEBUG_MODE:
                print(f"  ✓ Berhasil: {name}")
        else:
            print(f"  ✗ Tidak ada wajah terdeteksi di: {filename}")

if face_count == 0:
    print("⚠️  Peringatan: Tidak ada wajah yang berhasil dimuat dari folder faces/")
    print("   Pastikan ada file gambar (.jpg/.png/.jpeg) dengan wajah yang jelas")
else:
    print(f"✅ Database siap! {face_count} wajah dimuat: {known_names}")

# Setup kamera
print(f"\nMenghubungkan ke kamera (indeks: {CAMERA_INDEX})...")
video_capture = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

# Set resolusi kamera
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

if not video_capture.isOpened():
    print(f"❌ Error: Kamera dengan indeks {CAMERA_INDEX} tidak ditemukan!")
    print("💡 Solusi:")
    print("   1. Pastikan Insta360 Link 2 terhubung via USB")
    print("   2. Coba ganti CAMERA_INDEX di config.py ke 1 atau 2")
    print("   3. Restart aplikasi setelah mencolok kamera")
    input("\nTekan Enter untuk keluar...")
    exit()

# Informasi kamera
actual_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
actual_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(video_capture.get(cv2.CAP_PROP_FPS))

print(f"✅ Kamera terhubung!")
print(f"   Resolusi: {actual_width}x{actual_height}")
print(f"   FPS: {fps}")
print(f"   Resize factor: {FRAME_RESIZE}")
print(f"   Tolerance: {TOLERANCE}")
print("\n🎥 Sistem Face Recognition aktif!")
print("   Tekan 'q' di jendela video untuk keluar")
print("   Tekan 'r' untuk reload database wajah")

# Variables untuk FPS counter
frame_count = 0
start_time = time.time()
fps_display = 0

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("❌ Gagal mengambil gambar dari kamera.")
        break

    # FPS Counter
    frame_count += 1
    if SHOW_FPS and frame_count % 30 == 0:
        end_time = time.time()
        fps_display = 30 / (end_time - start_time)
        start_time = end_time

    # Resize frame untuk performa
    small_frame = cv2.resize(frame, (0, 0), fx=FRAME_RESIZE, fy=FRAME_RESIZE)
    rgb_small_frame = small_frame[:, :, ::-1]
    
    # Deteksi wajah (setiap N frame untuk performa)
    if frame_count % DETECTION_FREQUENCY == 0:
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        # Batasi jumlah wajah yang diproses
        if len(face_locations) > MAX_FACES_TO_PROCESS:
            face_locations = face_locations[:MAX_FACES_TO_PROCESS]
            face_encodings = face_encodings[:MAX_FACES_TO_PROCESS]

    # Process setiap wajah yang terdeteksi
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Hitung jarak dengan database wajah
        name = "Unknown"
        confidence = 0
        
        if len(known_faces) > 0:
            face_distances = face_recognition.face_distance(known_faces, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            if face_distances[best_match_index] <= TOLERANCE:
                name = known_names[best_match_index]
                confidence = 1 - face_distances[best_match_index]

        # Convert koordinat kembali ke ukuran asli
        top = int(top / FRAME_RESIZE)
        right = int(right / FRAME_RESIZE)
        bottom = int(bottom / FRAME_RESIZE)
        left = int(left / FRAME_RESIZE)

        # Pilih warna berdasarkan status
        color = COLOR_KNOWN if name != "Unknown" else COLOR_UNKNOWN
        
        # Gambar kotak deteksi
        cv2.rectangle(frame, (left, top), (right, bottom), color, BOX_THICKNESS)
        
        # Gambar background untuk text
        label_text = name
        if DEBUG_MODE and name != "Unknown":
            label_text = f"{name} ({confidence:.2f})"
        
        # Hitung ukuran text
        (text_width, text_height), _ = cv2.getTextSize(
            label_text, cv2.FONT_HERSHEY_DUPLEX, FONT_SCALE, FONT_THICKNESS)
        
        # Gambar background text
        cv2.rectangle(frame, (left, bottom - text_height - 10), 
                     (left + text_width + 10, bottom), color, cv2.FILLED)
        
        # Gambar text nama
        cv2.putText(frame, label_text, (left + 5, bottom - 5), 
                   cv2.FONT_HERSHEY_DUPLEX, FONT_SCALE, COLOR_TEXT, FONT_THICKNESS)

    # Tampilkan FPS jika diaktifkan
    if SHOW_FPS:
        fps_text = f"FPS: {fps_display:.1f}"
        cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.7, (0, 255, 255), 2)

    # Tampilkan informasi debug
    if DEBUG_MODE:
        info_text = f"Faces: {len(face_locations)} | Frame: {frame_count}"
        cv2.putText(frame, info_text, (10, frame.shape[0] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Tampilkan video
    cv2.imshow(WINDOW_NAME, frame)

    # Handle keyboard input
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("🛑 Sistem dihentikan oleh user")
        break
    elif key == ord('r'):
        print("🔄 Reloading database wajah...")
        # TODO: Implement reload functionality
        print("   (Fitur reload akan ditambahkan di update berikutnya)")
    elif key == ord('d'):
        # Toggle debug mode
        globals()['DEBUG_MODE'] = not DEBUG_MODE
        print(f"🔧 Debug mode: {'ON' if DEBUG_MODE else 'OFF'}")
    elif key == ord('f'):
        # Toggle FPS display
        globals()['SHOW_FPS'] = not SHOW_FPS
        print(f"📊 FPS display: {'ON' if SHOW_FPS else 'OFF'}")

video_capture.release()
cv2.destroyAllWindows()
print("\n✅ Sistem berhasil dihentikan.")
print("💡 Tips: Edit config.py untuk menyesuaikan pengaturan")
input("Tekan Enter untuk keluar...")