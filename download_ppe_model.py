"""
download_ppe_model.py - Unduh model YOLOv8 PPE (ppe.pt).

Sebelumnya repo merujuk model lewat submodule `ppe_reference` yang rusak
(tidak ada `.gitmodules`), sehingga `ppe.pt` tidak pernah ada dan deteksi
PPE selalu jatuh ke simulation mode. Script ini mengunduh model langsung.

Penggunaan:
    python download_ppe_model.py                 # unduh ke ppe_reference/ppe.pt
    python download_ppe_model.py -o ppe.pt       # unduh ke lokasi lain
    python download_ppe_model.py --url <URL>      # pakai sumber model lain

Model default (10 kelas: Hardhat, Mask, NO-Hardhat, NO-Mask, NO-Safety Vest,
Person, Safety Cone, Safety Vest, machinery, vehicle) berasal dari dataset
"Construction Site Safety" dan cocok dengan class_names di ppe_detector.py.
Sumber: https://github.com/Ansarimajid/Construction-PPE-Detection (MIT License)
"""

import argparse
import os
import sys
import urllib.request

DEFAULT_URL = (
    "https://raw.githubusercontent.com/Ansarimajid/"
    "Construction-PPE-Detection/main/Model/ppe.pt"
)
DEFAULT_OUTPUT = os.path.join("ppe_reference", "ppe.pt")


def _progress(block_num, block_size, total_size):
    if total_size <= 0:
        return
    downloaded = block_num * block_size
    pct = min(downloaded * 100 / total_size, 100)
    mb = downloaded / (1024 * 1024)
    total_mb = total_size / (1024 * 1024)
    sys.stdout.write(f"\r   Mengunduh... {pct:5.1f}%  ({mb:.1f}/{total_mb:.1f} MB)")
    sys.stdout.flush()


def is_valid_pt(path: str) -> bool:
    """Cek apakah file adalah arsip PyTorch (.pt) yang valid (ZIP, magic PK)."""
    try:
        with open(path, "rb") as f:
            return f.read(2) == b"PK"
    except OSError:
        return False


def download_model(url: str = DEFAULT_URL, output: str = DEFAULT_OUTPUT,
                  force: bool = False) -> str:
    """Unduh model PPE ke `output`. Mengembalikan path file."""
    output_dir = os.path.dirname(output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    if os.path.exists(output) and not force:
        if is_valid_pt(output):
            print(f"✅ Model sudah ada di '{output}' (lewati unduh).")
            print("   Gunakan --force untuk mengunduh ulang.")
            return output
        print(f"⚠️  File '{output}' ada tapi tidak valid, mengunduh ulang...")

    print(f"📥 Sumber : {url}")
    print(f"📂 Tujuan : {output}")
    try:
        urllib.request.urlretrieve(url, output, reporthook=_progress)
        print()
    except Exception as e:  # noqa: BLE001
        print(f"\n❌ Gagal mengunduh model: {e}")
        print("💡 Coba lagi, atau unduh manual & taruh di:", output)
        raise

    if not is_valid_pt(output):
        os.remove(output)
        raise RuntimeError(
            "File yang terunduh bukan model .pt yang valid (magic ZIP tidak cocok)."
        )

    size_mb = os.path.getsize(output) / (1024 * 1024)
    print(f"✅ Selesai! Model tersimpan ({size_mb:.1f} MB) di '{output}'.")
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Unduh model YOLOv8 PPE (ppe.pt) untuk sistem PPE Compliance.")
    parser.add_argument("--url", default=DEFAULT_URL, help="URL model .pt")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT,
                       help="Path tujuan penyimpanan model")
    parser.add_argument("--force", action="store_true",
                       help="Unduh ulang walau file sudah ada")
    args = parser.parse_args()

    try:
        download_model(args.url, args.output, args.force)
    except Exception:  # noqa: BLE001
        sys.exit(1)


if __name__ == "__main__":
    main()
