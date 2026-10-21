import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from app import app
from crypto.dicom import save_watermarked
from crypto.dicom import load
from crypto import tamper as tp
import numpy as np


def smk(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" {detail}" if detail else ""))
    return cond


def main():
    app.config["TESTING"] = True
    client = app.test_client()

    dcm_path = os.path.join(BASE, "dataset", "BrainTumorMRI", "IM-0001-0002.dcm")
    pixels, ds = load(dcm_path)
    dcm_bytes = io.BytesIO()
    save_watermarked(dcm_bytes, ds, pixels)

    ok = []
    ok.append(smk("GET / index render", client.get("/").status_code == 200))
    ok.append(smk("GET /algoritma", client.get("/algoritma").status_code == 200))
    ok.append(smk("GET /pengujian", client.get("/pengujian").status_code == 200))

    r = client.get("/")
    ok.append(smk("template reversible field diterima", b"Proteksi" in r.data))

    data = {
        "action": "protek",
        "password": "kunci-ui-2026",
        "metadata": "",
        "file": (io.BytesIO(dcm_bytes.getvalue()), "MRI.dcm"),
    }
    rp = client.post("/", data=data, content_type="multipart/form-data", follow_redirects=True)
    ok.append(smk("POST protek DICOM 200", rp.status_code == 200))
    ok.append(smk("hasil protek reversible + PSNR", b"PSNR" in rp.data and b"reversible" in rp.data))
    ok.append(smk("badge reversible muncul", b"PEE-HS" in rp.data))
    ok.append(smk("parameter MSE muncul di protek", b"MSE (Mean Squared Error)" in rp.data))
    ok.append(smk("parameter NPCR/UACI muncul di protek", b"NPCR &amp; UACI" in rp.data))
    ok.append(smk("parameter NC/NCC muncul di protek", b"NC &amp; NCC" in rp.data))
    ok.append(smk("parameter Chi-Square muncul di protek", b"Chi-Square" in rp.data))
    ok.append(smk("parameter BER muncul di protek", b"BER (Bit Error Rate)" in rp.data))

    urls = [r.headers.get("Location", "") for r in rp.history]
    token = None
    for u in urls:
        m = re.search(r"hasil=([0-9a-f]{32})", u)
        if m:
            token = m.group(1)
            break
    ok.append(smk("token hasil protek terbentuk", token is not None))

    # bangun .krip dari protek token (file download)
    from app import materialkan
    res = materialkan(token)
    ok.append(smk("dict metrics ada dalam token data", "metrics" in res and res["metrics"]["ber_rec_str"] == "0.00000000"))

    import base64
    krip_bytes = base64.b64decode(res["download_uri"].split(",")[1])

    data_v = {
        "action": "verif",
        "password": "kunci-ui-2026",
        "metadata": "",
        "file": (io.BytesIO(krip_bytes), "MRI.krip"),
    }
    rv = client.post("/", data=data_v, content_type="multipart/form-data", follow_redirects=True)
    ok.append(smk("POST verif DICOM 200", rv.status_code == 200))
    ok.append(smk("verif recovery lossless ditampilkan", b"lossless" in rv.data))
    ok.append(smk("verif piksel utuh pill", b"Piksel utuh" in rv.data))
    ok.append(smk("parameter evaluasi muncul di verif", b"Evaluasi Parameter Kuantitatif" in rv.data))

    # verif dengan kunci salah -> error flash
    data_w = {
        "action": "verif",
        "password": "salah",
        "metadata": "",
        "file": (io.BytesIO(krip_bytes), "MRI.krip"),
    }
    rw = client.post("/", data=data_w, content_type="multipart/form-data", follow_redirects=True)
    ok.append(smk("verif kunci salah -> pesan ramah", "Kunci tidak cocok" in rw.data.decode("utf-8", "replace")))

    # Pengujian page table and button checks
    r_peng = client.get("/pengujian")
    ok.append(smk("tabel 10 parameter dosen ada di /pengujian", b"Tabel Rekapitulasi 10 Parameter Evaluasi Dosen" in r_peng.data))
    ok.append(smk("tombol uji 10 parameter ada di /pengujian", b"lecturer_metrics" in r_peng.data))

    print(f"\nHasil: {sum(ok)}/{len(ok)}")
    return all(ok)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)