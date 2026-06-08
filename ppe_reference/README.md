# ppe_reference/

Folder ini menampung **model deteksi PPE** (`ppe.pt`) yang dipakai oleh
`ppe_system_main.py` dan `ppe_detector.py`.

> ⚠️ **Penting:** Sebelumnya folder ini terdaftar sebagai *git submodule yang
> rusak* (gitlink tanpa `.gitmodules`), sehingga `ppe.pt` tidak pernah ikut
> ter-clone dan deteksi PPE selalu jatuh ke *simulation mode*. Submodule rusak
> tersebut sudah dihapus dan diganti dengan script unduh di bawah.

## Cara mendapatkan `ppe.pt`

Dari root repo, jalankan:

```bash
python download_ppe_model.py
```

Script akan mengunduh model ke `ppe_reference/ppe.pt`.

> File `*.pt` sengaja **tidak di-commit** (di-ignore lewat `.gitignore`) karena
> ukurannya besar (~24 MB). Setiap orang menjalankan script di atas sekali saja.

## Tentang model

- **Arsitektur:** YOLOv8 (Ultralytics)
- **10 kelas:** `Hardhat`, `Mask`, `NO-Hardhat`, `NO-Mask`, `NO-Safety Vest`,
  `Person`, `Safety Cone`, `Safety Vest`, `machinery`, `vehicle`
  (cocok dengan `class_names` di `ppe_detector.py`)
- **Sumber:** [Ansarimajid/Construction-PPE-Detection](https://github.com/Ansarimajid/Construction-PPE-Detection) — MIT License
- Dataset asal: "Construction Site Safety" (Roboflow)

Untuk memakai model lain, unduh dengan URL kustom:

```bash
python download_ppe_model.py --url <URL_MODEL_LAIN> -o ppe_reference/ppe.pt
```
