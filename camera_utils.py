"""
Camera helpers - lintas platform (Windows / Linux / macOS).

Modul ini memisahkan logika pembukaan kamera dari main.py supaya:
- Bug `CAMERA_INDEX = "auto"` yang sebelumnya dikirim langsung ke
  `cv2.VideoCapture(...)` tidak terjadi lagi.
- Backend OpenCV dipilih otomatis sesuai OS (DirectShow di Windows,
  default di Linux/macOS) dan tidak lagi hard-coded ke `CAP_DSHOW`.
- Logika ini bisa diuji tanpa kamera fisik.
"""

import platform

import cv2


def get_backend(backend: str = "auto") -> int:
    """Konversi nama backend menjadi konstanta cv2.CAP_*.

    "auto" akan memilih backend yang sesuai dengan sistem operasi:
    DirectShow di Windows, dan backend default (CAP_ANY) di Linux/macOS.
    """
    if backend is None:
        backend = "auto"

    name = str(backend).strip().lower()

    explicit = {
        "dshow": cv2.CAP_DSHOW,
        "msmf": cv2.CAP_MSMF,
        "v4l2": cv2.CAP_V4L2,
        "avfoundation": cv2.CAP_AVFOUNDATION,
        "any": cv2.CAP_ANY,
    }
    if name in explicit:
        return explicit[name]

    # "auto" (atau nilai tak dikenal) -> tergantung OS
    if platform.system() == "Windows":
        return cv2.CAP_DSHOW
    return cv2.CAP_ANY


def _apply_resolution(cap, width, height) -> None:
    """Set resolusi kamera hanya jika bukan "auto"."""
    if isinstance(width, (int, float)) and width:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
    if isinstance(height, (int, float)) and height:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))


def open_camera(index, width="auto", height="auto", backend="auto"):
    """Buka satu kamera pada `index` tertentu.

    Mengembalikan objek VideoCapture jika berhasil dibuka, atau None
    jika kamera tidak tersedia. Kamera yang gagal dibuka langsung
    dilepas supaya tidak menahan device.
    """
    cap = cv2.VideoCapture(int(index), get_backend(backend))
    if not cap.isOpened():
        cap.release()
        return None
    _apply_resolution(cap, width, height)
    return cap


def find_camera(max_scan=5, width="auto", height="auto", backend="auto"):
    """Pindai indeks 0..max_scan-1 dan kembalikan kamera pertama yang aktif.

    Mengembalikan tuple (index, cap). Jika tidak ada kamera ditemukan,
    mengembalikan (None, None).
    """
    for index in range(int(max_scan)):
        cap = open_camera(index, width, height, backend)
        if cap is not None:
            return index, cap
    return None, None


def resolve_camera(camera_index="auto", max_scan=5,
                   width="auto", height="auto", backend="auto"):
    """Tentukan & buka kamera berdasarkan konfigurasi.

    - camera_index == "auto"  -> scan dan pakai kamera pertama yang aktif.
    - camera_index berupa angka -> buka indeks tersebut.

    Mengembalikan tuple (index, cap). (None, None) jika gagal.
    """
    if isinstance(camera_index, str) and camera_index.strip().lower() == "auto":
        return find_camera(max_scan, width, height, backend)

    cap = open_camera(camera_index, width, height, backend)
    if cap is None:
        return None, None
    return int(camera_index), cap
