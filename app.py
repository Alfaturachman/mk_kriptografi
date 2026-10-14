import base64
import io
import json
import os
import secrets
import subprocess
import sys
import time

import numpy as np
from flask import Flask, flash, redirect, render_template, request, session, url_for
from PIL import Image

from crypto import aes
from crypto.dicom import load, metadata_of, preview_8bit, save_watermarked
from crypto.tamper import mark_tampered, protect_image, verify_image, protect_image_rev, verify_image_rev
from crypto.histogram import (
    render_histogram_image,
    render_comparison_histogram,
    render_ciphertext_histogram,
    shannon_entropy,
    shannon_entropy_bytes,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(BASE_DIR, "tmp")
TMP_TTL = 24 * 60 * 60

app = Flask(__name__)
app.config["SECRET_KEY"] = "proyek-kriptografi-medis"
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024


def psnr(original, modified) -> float:
    maxv = float(np.iinfo(original.dtype).max)
    mse = np.mean((original.astype(np.float64) - modified.astype(np.float64)) ** 2)
    if mse == 0:
        return float("inf")
    return 10.0 * np.log10(maxv ** 2 / mse)


def data_uri(data: bytes, mime: str = "application/octet-stream") -> str:
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def png_bytes(arr: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(np.asarray(arr, dtype=np.uint8)).save(buf, format="PNG")
    return buf.getvalue()


def png_uri(arr: np.ndarray) -> str:
    return data_uri(png_bytes(arr), "image/png")


def jenis(plain: bytes) -> str:
    if plain[128:132] == b"DICM":
        return "dicom"
    if plain.startswith(b"\x89PNG"):
        return "png"
    if plain.startswith((b"\xff\xd8", b"\x42\x4d")):
        return "image"
    return "unknown"


def protek(raw: bytes, fname: str, ext: str, password: str, metadata: str) -> tuple:
    if ext == ".dcm":
        pixels, ds = load(io.BytesIO(raw))
        md = metadata.encode("utf-8") if metadata else metadata_of(ds)
        protected = protect_image_rev(pixels, md, passphrase=password)
        ver = verify_image_rev(protected, md, passphrase=password)
        recovered = ver["original_recovered"]
        buf = io.BytesIO()
        save_watermarked(buf, ds, protected)
        media_bytes = buf.getvalue()
        kind = "DICOM MRI (reversible)"
        reversible = True
        prev_orig = preview_8bit(pixels)
        prev_wm = preview_8bit(protected)
        prev_rec = preview_8bit(recovered)
    else:
        img = Image.open(io.BytesIO(raw))
        img.load()
        pixels = np.array(img.convert("RGB"))
        md = metadata.encode("utf-8") if metadata else f"FILE={fname};KUNCI-TANDA".encode("utf-8")
        protected = protect_image(pixels, md)
        recovered = protected
        buf = io.BytesIO()
        Image.fromarray(protected).save(buf, format="PNG")
        media_bytes = buf.getvalue()
        kind = "PNG"
        reversible = False
        prev_orig = pixels.astype(np.uint8)
        prev_wm = protected.astype(np.uint8)
        prev_rec = recovered.astype(np.uint8)

    cipher = aes.encrypt(media_bytes, password)
    p = psnr(pixels, protected)
    stem = os.path.splitext(fname)[0]

    # Bangkitkan Histogram Asli, Enkripsi, Dekripsi, Komparasi, dan Ciphertext
    hist_orig = render_histogram_image(prev_orig, "1. Histogram Citra Asli", color="#0284c7", edge_color="#0369a1")
    hist_enc = render_histogram_image(prev_wm, "2. Histogram Hasil Enkripsi / Watermark", color="#d97706", edge_color="#b45309")
    hist_dec = render_histogram_image(prev_rec, "3. Histogram Hasil Dekripsi (100% Eksak)", color="#059669", edge_color="#047857")
    hist_comp = render_comparison_histogram(prev_orig, prev_wm, prev_rec)
    hist_ciph = render_ciphertext_histogram(cipher)

    payload = {
        "mode": "protek",
        "kind": kind,
        "reversible": reversible,
        "metadata_used": md.decode("utf-8", errors="replace"),
        "psnr": "inf" if p == float("inf") else f"{p:.2f}",
        "size_src": len(media_bytes),
        "size_enc": len(cipher),
        "download_name": stem + ".krip",
        "ent_orig": round(shannon_entropy(prev_orig), 3),
        "ent_enc": round(shannon_entropy(prev_wm), 3),
        "ent_dec": round(shannon_entropy(prev_rec), 3),
        "ent_cipher": round(shannon_entropy_bytes(cipher), 3),
    }
    files = {
        "preview_orig.png": png_bytes(prev_orig),
        "preview_wm.png": png_bytes(prev_wm),
        "download": cipher,
        "hist_orig.png": hist_orig,
        "hist_enc.png": hist_enc,
        "hist_dec.png": hist_dec,
        "hist_compare.png": hist_comp,
        "hist_cipher.png": hist_ciph,
    }
    return payload, files


def verif(raw: bytes, fname: str, password: str, metadata: str) -> tuple:
    plain = aes.decrypt(raw, password)
    kind = jenis(plain)
    if kind == "dicom":
        pixels, ds = load(io.BytesIO(plain))
        md = metadata_of(ds)
        label = "DICOM MRI (reversible)"
        verdict = verify_image_rev(pixels, md, passphrase=password)
        recovered = verdict["original_recovered"]
        preview = preview_8bit(recovered)
        prev_wm = preview_8bit(pixels)
        prev_rec = preview
        prev_orig = preview
        recovered_name = os.path.splitext(fname)[0] + ".dcm"
        recovered_buf = io.BytesIO()
        save_watermarked(recovered_buf, ds, verdict["original_recovered"])
        recovered_bytes = recovered_buf.getvalue()
        reversible = True
    elif kind in ("png", "image"):
        if not metadata:
            raise ValueError("Untuk berkas gambar, isi metadata yang dipakai saat proteksi.")
        pixels = np.array(Image.open(io.BytesIO(plain)).convert("RGB"))
        md = metadata.encode("utf-8")
        label = "PNG"
        verdict = verify_image(pixels, md)
        recovered = pixels
        preview = pixels.astype(np.uint8)
        prev_wm = preview
        prev_rec = preview
        prev_orig = preview
        recovered_name = os.path.splitext(fname)[0] + ".png"
        recovered_bytes = plain
        reversible = False
    else:
        raise ValueError("Hasil dekripsi bukan gambar/DICOM yang dikenal.")

    mask = verdict["mask"]
    mask_px = int((mask == 255).sum())
    overlay = mark_tampered(preview, mask)

    hist_orig = render_histogram_image(prev_orig, "1. Histogram Citra Asli (Terekonstruksi)", color="#0284c7", edge_color="#0369a1")
    hist_enc = render_histogram_image(prev_wm, "2. Histogram Hasil Enkripsi / Watermark", color="#d97706", edge_color="#b45309")
    hist_dec = render_histogram_image(prev_rec, "3. Histogram Hasil Dekripsi & Pemulihan", color="#059669", edge_color="#047857")
    hist_comp = render_comparison_histogram(prev_orig, prev_wm, prev_rec)
    hist_ciph = render_ciphertext_histogram(raw)

    payload = {
        "mode": "verif",
        "kind": label,
        "reversible": reversible,
        "metadata_used": md.decode("utf-8", errors="replace"),
        "pixel_tamper": bool(verdict["pixel_tamper"]),
        "metadata_ok": bool(verdict["metadata_ok"]),
        "mask_px": mask_px,
        "recovered_name": recovered_name,
        "ent_orig": round(shannon_entropy(prev_orig), 3),
        "ent_enc": round(shannon_entropy(prev_wm), 3),
        "ent_dec": round(shannon_entropy(prev_rec), 3),
        "ent_cipher": round(shannon_entropy_bytes(raw), 3),
    }
    if verdict.get("error"):
        payload["error_pesan"] = verdict["error"]
    files = {
        "preview_rec.png": png_bytes(preview),
        "preview_ovl.png": png_bytes(overlay),
        "recovered": recovered_bytes,
        "hist_orig.png": hist_orig,
        "hist_enc.png": hist_enc,
        "hist_dec.png": hist_dec,
        "hist_compare.png": hist_comp,
        "hist_cipher.png": hist_ciph,
    }
    return payload, files


def pesan_ramah(exception: Exception) -> str:
    msg = str(exception)
    paduan = [
        (
            ("padding tidak valid", "panjang ciphertext tidak valid"),
            "Kunci tidak cocok dengan saat proteksi, atau berkas .krip sudah diubah/rusak. "
            "Periksa kunci kamu (harus sama persis, termasuk huruf besar/kecil) dan gunakan berkas .krip asli.",
        ),
        (
            ("bukan file hasil enkripsi",),
            "Berkas ini bukan hasil enkripsi CitraMedis. Gunakan file .krip yang benar-benar dihasilkan aplikasi ini.",
        ),
        (
            ("hasil dekripsi bukan gambar",),
            "Berkas berhasil dibuka kuncinya, tetapi isinya bukan citra/DICOM yang didukung. "
            "Pastikan berkas .krip dibuat dari gambar (PNG/JPG/BMP/DICOM).",
        ),
        (
            ("uncompressed",),
            "File DICOM ini memakai kompresi yang belum didukung. Aplikasi ini hanya menerima DICOM uncompressed.",
        ),
        (
            ("metadata yang dipakai",),
            "Citra gambar butuh metadata untuk verifikasi. Salin teks metadata yang kamu pakai saat proteksi "
            "ke kolom verifikasi, kemudian coba lagi.",
        ),
        (
            ("data kosong",),
            "Ada data kosong di dalam proses. Gunakan citra dan metadata yang valid.",
        ),
    ]
    for kunci, pesan in paduan:
        if any(k in msg for k in kunci):
            return pesan
    return msg


def simpan_token(token: str, payload: dict, files: dict) -> None:
    folder = os.path.join(TMP_DIR, token)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "data.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f)
    for name, blob in files.items():
        with open(os.path.join(folder, name), "wb") as f:
            f.write(blob)


def materialkan(token: str):
    folder = os.path.join(TMP_DIR, token)
    if not os.path.isdir(folder):
        return None
    with open(os.path.join(folder, "data.json"), encoding="utf-8") as f:
        result = json.load(f)

    def uri(name: str, mime: str) -> str:
        with open(os.path.join(folder, name), "rb") as f:
            return data_uri(f.read(), mime)

    if result["mode"] == "protek":
        result["preview_orig"] = uri("preview_orig.png", "image/png")
        result["preview_wm"] = uri("preview_wm.png", "image/png")
        result["download_uri"] = uri("download", "application/octet-stream")
    else:
        result["preview_rec"] = uri("preview_rec.png", "image/png")
        result["preview_ovl"] = uri("preview_ovl.png", "image/png")
        result["recovered_uri"] = uri("recovered", "application/octet-stream")

    for hname in ["hist_orig", "hist_enc", "hist_dec", "hist_compare", "hist_cipher"]:
        hfile = f"{hname}.png"
        if os.path.isfile(os.path.join(folder, hfile)):
            result[hname] = uri(hfile, "image/png")

    return result


def bersihkan_tmp() -> None:
    if not os.path.isdir(TMP_DIR):
        return
    now = time.time()
    for name in os.listdir(TMP_DIR):
        folder = os.path.join(TMP_DIR, name)
        try:
            if os.path.isdir(folder) and now - os.path.getmtime(folder) > TMP_TTL:
                for inner in os.listdir(folder):
                    os.remove(os.path.join(folder, inner))
                os.rmdir(folder)
        except OSError:
            pass


def gagal(pesan: str):
    flash(pesan, "error")
    return redirect(url_for("index"))


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action")
        file = request.files.get("file")
        password = request.form.get("password", "").strip()
        metadata = request.form.get("metadata", "").strip()
        if file is None or file.filename == "":
            return gagal("Pilih berkas terlebih dahulu.")
        if not password:
            return gagal("Kunci tidak boleh kosong.")

        raw = file.read()
        fname = os.path.basename(file.filename)
        ext = os.path.splitext(fname)[1].lower()
        t0 = time.perf_counter()
        try:
            if action == "protek":
                if ext not in (".png", ".jpg", ".jpeg", ".bmp", ".dcm"):
                    return gagal("Jenis berkas tidak didukung. Gunakan PNG/JPG/BMP atau DICOM.")
                payload, files = protek(raw, fname, ext, password, metadata)
            elif action == "verif":
                if ext != ".krip":
                    return gagal("Berkas verifikasi harus bertipe .krip.")
                payload, files = verif(raw, fname, password, metadata)
            else:
                return gagal("Aksi tidak dikenal.")
        except ValueError as exc:
            return gagal(pesan_ramah(exc))

        payload["waktu_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        token = secrets.token_hex(16)
        simpan_token(token, payload, files)
        return redirect(url_for("index", hasil=token))

    bersihkan_tmp()
    result = None
    token = request.args.get("hasil")
    if token:
        result = materialkan(token)
    return render_template("index.html", result=result)


@app.route("/algoritma")
def algoritma():
    return render_template("algoritma.html")


@app.route("/pengujian", methods=["GET", "POST"])
def pengujian():
    output = session.pop("uji_output", None)
    if request.method == "POST":
        skenario = request.form.get("skenario")
        if skenario == "reversible":
            target = "tests/test_reversible_tamper.py"
        elif skenario == "metrics":
            target = "tests/test_metrics.py"
        elif skenario == "dicom":
            target = "tests/test_dicom.py"
        else:
            target = "tests/test_core.py"
        try:
            proc = subprocess.run(
                [sys.executable, os.path.join(BASE_DIR, target)],
                capture_output=True,
                text=True,
                timeout=120,
            )
            output = proc.stdout if proc.returncode == 0 else proc.stderr
        except subprocess.TimeoutExpired:
            output = "Waktu pengujian habis (120 detik)."
        session["uji_output"] = output
        return redirect(url_for("pengujian"))
    return render_template("pengujian.html", output=output)


if __name__ == "__main__":
    app.run(debug=True)