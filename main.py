import os
import time

import cv2
import face_recognition
import numpy as np

from config import *  # noqa: F401,F403
from camera_utils import resolve_camera


def load_known_faces(faces_dir=FACES_DIR, debug=DEBUG_MODE):
    """Muat semua encoding wajah dari folder `faces_dir`.

    Mengembalikan tuple (known_faces, known_names).
    """
    print(f"Memuat database wajah dari folder /{faces_dir}...")

    known_faces = []
    known_names = []

    if not os.path.exists(faces_dir):
        os.makedirs(faces_dir)
        print(f"Folder '{faces_dir}' dibuat. Silakan tambahkan foto referensi wajah.")
        return known_faces, known_names

    for filename in os.listdir(faces_dir):
        if not filename.lower().endswith((".jpg", ".png", ".jpeg")):
            continue

        filepath = os.path.join(faces_dir, filename)
        if debug:
            print(f"Memproses: {filename}")

        image = face_recognition.load_image_file(filepath)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) > 0:
            known_faces.append(encodings[0])
            name = os.path.splitext(filename)[0].replace("_", " ").title()
            known_names.append(name)
            if debug:
                print(f"  ✓ Berhasil: {name}")
        else:
            print(f"  ✗ Tidak ada wajah terdeteksi di: {filename}")

    if len(known_faces) == 0:
        print("⚠️  Peringatan: Tidak ada wajah yang berhasil dimuat dari folder faces/")
        print("   Pastikan ada file gambar (.jpg/.png/.jpeg) dengan wajah yang jelas")
    else:
        print(f"✅ Database siap! {len(known_faces)} wajah dimuat: {known_names}")

    return known_faces, known_names


def main():
    known_faces, known_names = load_known_faces()

    # Setup kamera (lintas platform + auto-detect)
    print(f"\nMenghubungkan ke kamera (index: {CAMERA_INDEX}, backend: {CAMERA_BACKEND})...")
    camera_index, video_capture = resolve_camera(
        camera_index=CAMERA_INDEX,
        max_scan=MAX_CAMERA_SCAN,
        width=CAMERA_WIDTH,
        height=CAMERA_HEIGHT,
        backend=CAMERA_BACKEND,
    )

    if video_capture is None:
        print("❌ Error: Tidak ada kamera yang bisa dibuka!")
        print("💡 Solusi:")
        print("   1. Pastikan kamera / Insta360 Link 2 terhubung via USB")
        print("   2. Set CAMERA_INDEX di config.py ke angka spesifik (0, 1, 2, ...)")
        print("   3. Coba ganti CAMERA_BACKEND di config.py (mis. 'v4l2' di Linux)")
        print("   4. Restart aplikasi setelah mencolok kamera")
        input("\nTekan Enter untuk keluar...")
        return

    actual_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))

    print("✅ Kamera terhubung!")
    print(f"   Index    : {camera_index}")
    print(f"   Resolusi : {actual_width}x{actual_height}")
    print(f"   FPS      : {fps}")
    print(f"   Resize   : {FRAME_RESIZE}")
    print(f"   Tolerance: {TOLERANCE}")
    print("\n🎥 Sistem Face Recognition aktif!")
    print("   Tekan 'q' di jendela video untuk keluar")
    print("   Tekan 'r' untuk reload database wajah")

    debug_mode = DEBUG_MODE
    show_fps = SHOW_FPS

    frame_count = 0
    start_time = time.time()
    fps_display = 0
    face_locations = []
    face_encodings = []

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("❌ Gagal mengambil gambar dari kamera.")
            break

        frame_count += 1
        if show_fps and frame_count % 30 == 0:
            end_time = time.time()
            fps_display = 30 / (end_time - start_time)
            start_time = end_time

        # Resize frame untuk performa
        small_frame = cv2.resize(frame, (0, 0), fx=FRAME_RESIZE, fy=FRAME_RESIZE)
        # Gunakan cvtColor (array contiguous) agar kompatibel dengan dlib/face_recognition
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Deteksi wajah (setiap N frame untuk performa)
        if frame_count % DETECTION_FREQUENCY == 0:
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            if len(face_locations) > MAX_FACES_TO_PROCESS:
                face_locations = face_locations[:MAX_FACES_TO_PROCESS]
                face_encodings = face_encodings[:MAX_FACES_TO_PROCESS]

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
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

            color = COLOR_KNOWN if name != "Unknown" else COLOR_UNKNOWN
            cv2.rectangle(frame, (left, top), (right, bottom), color, BOX_THICKNESS)

            label_text = name
            if debug_mode and name != "Unknown":
                label_text = f"{name} ({confidence:.2f})"

            (text_width, text_height), _ = cv2.getTextSize(
                label_text, cv2.FONT_HERSHEY_DUPLEX, FONT_SCALE, FONT_THICKNESS)

            cv2.rectangle(frame, (left, bottom - text_height - 10),
                         (left + text_width + 10, bottom), color, cv2.FILLED)
            cv2.putText(frame, label_text, (left + 5, bottom - 5),
                       cv2.FONT_HERSHEY_DUPLEX, FONT_SCALE, COLOR_TEXT, FONT_THICKNESS)

        if show_fps:
            fps_text = f"FPS: {fps_display:.1f}"
            cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                       0.7, (0, 255, 255), 2)

        if debug_mode:
            info_text = f"Faces: {len(face_locations)} | Frame: {frame_count}"
            cv2.putText(frame, info_text, (10, frame.shape[0] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.imshow(WINDOW_NAME, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("🛑 Sistem dihentikan oleh user")
            break
        elif key == ord('r'):
            print("🔄 Reloading database wajah...")
            known_faces, known_names = load_known_faces(debug=debug_mode)
        elif key == ord('d'):
            debug_mode = not debug_mode
            print(f"🔧 Debug mode: {'ON' if debug_mode else 'OFF'}")
        elif key == ord('f'):
            show_fps = not show_fps
            print(f"📊 FPS display: {'ON' if show_fps else 'OFF'}")

    video_capture.release()
    cv2.destroyAllWindows()
    print("\n✅ Sistem berhasil dihentikan.")
    print("💡 Tips: Edit config.py untuk menyesuaikan pengaturan")


if __name__ == "__main__":
    main()
