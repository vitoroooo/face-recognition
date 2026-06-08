"""
test_camera.py - Utility untuk mencari kamera yang tersedia.

Jalankan: `python test_camera.py`
Script ini memindai indeks kamera 0..N dan menampilkan kamera mana saja
yang bisa dibuka beserta resolusinya. Berguna untuk menentukan nilai
`CAMERA_INDEX` yang tepat di config.py.

Catatan: ini adalah utility CLI, BUKAN test pytest (tidak berisi
fungsi `test_*`), jadi tidak akan dijalankan oleh test suite.
"""

import cv2

from camera_utils import open_camera

try:
    from config import MAX_CAMERA_SCAN, CAMERA_BACKEND
except Exception:
    MAX_CAMERA_SCAN = 5
    CAMERA_BACKEND = "auto"


def scan_cameras(max_scan=MAX_CAMERA_SCAN, backend=CAMERA_BACKEND):
    """Pindai kamera dan kembalikan daftar indeks yang tersedia."""
    available = []
    print(f"🔍 Memindai kamera (0..{int(max_scan) - 1}, backend: {backend})...\n")

    for index in range(int(max_scan)):
        cap = open_camera(index, backend=backend)
        if cap is None:
            print(f"   [{index}] ✗ tidak tersedia")
            continue

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        ret, _ = cap.read()
        status = "✓ aktif" if ret else "⚠ terbuka tapi tidak ada frame"
        print(f"   [{index}] {status} - {width}x{height} @ {fps} FPS")
        available.append(index)
        cap.release()

    print()
    if available:
        print(f"✅ Kamera tersedia di index: {available}")
        print(f"💡 Set CAMERA_INDEX = {available[0]} di config.py untuk memakai kamera pertama.")
    else:
        print("❌ Tidak ada kamera yang terdeteksi.")
        print("   Pastikan kamera terhubung dan tidak dipakai aplikasi lain.")

    return available


if __name__ == "__main__":
    scan_cameras()
