"""Evaluasi jurnal - mengukur bukti kuantitatif skema reversible + AES.

Menghasilkan dua blok hasil:
  A. Kualitas & reversibilitas (24 slice): PSNR/SSIM watermarking, PSNR/SSIM recovery,
     BER recovery, kapasitas payload, runtime.
  B. Kinerja deteksi & lokalisasi tamper (default 8 slice) untuk 4 skenario ukuran
     tamper x 2 jalur (tanpa enkripsi & payload AES-256): detection rate,
     presisi/recall/F1/accuracy/FPR/IoU level-blok 16x16, plus frekuensi lokalisasi
     tersedia vs hilang -- dilaporkan jujur sesuai perilaku sistem nyata.

Output: konsol + `evaluation/journal_results.json` (dan CSV per-slice kualitas).

Run:  python evaluation\\journal_eval.py [n_slices_phase_b]
"""

import glob
import json
import os
import sys
import time

import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from crypto.dicom import load, metadata_of
from crypto.tamper import protect_image_rev, verify_image_rev, PARAM_STRIP
from crypto import reversible as rev
from crypto import metrics as mt

DCM_DIR = os.path.join(BASE, "dataset", "BrainTumorMRI")
OUT_DIR = os.path.join(BASE, "evaluation")
OUT_JSON = os.path.join(OUT_DIR, "journal_results.json")
OUT_CSV = os.path.join(OUT_DIR, "journal_quality_slice.csv")
PASSPHRASE = "jurnal-eval-2026"

BLOCK = 16
TAMPER_BASE_ROW, TAMPER_BASE_COL = 10 * BLOCK, 16 * BLOCK
SCENARIOS = [
    ("1px", 1, 1),
    ("8x8", 8, 8),
    ("16x16", 16, 16),
    ("48x48", 48, 48),
]


def _payload_bits(pixels: np.ndarray, block: int = 16, hash_bits: int = 16, encrypted: bool = True) -> int:
    rows = pixels.shape[0] - PARAM_STRIP
    n_blocks = (rows // block) * (pixels.shape[1] // block)
    raw = 6 + 1 + 1 + 2 + 32 + n_blocks * (hash_bits // 8)  # MAGIC+block+hash_bits+n_blocks+digest+hashes
    bits = raw * 8
    if encrypted:
        ci = raw + 16 - (raw % 16)      # PKCS7 padding
        bits = (4 + 16 + 16 + ci) * 8   # MAGIC(4)+salt(16)+iv(16)+ciphertext
    return bits


def _tamper(img: np.ndarray, h: int, w: int) -> np.ndarray:
    out = np.array(img, copy=True)
    hi = int(np.iinfo(out.dtype).max)
    r0, c0 = TAMPER_BASE_ROW, TAMPER_BASE_COL
    r0 = min(r0, out.shape[0] - h)
    c0 = min(c0, out.shape[1] - w)
    out[r0:r0 + h, c0:c0 + w] ^= np.array([0xBEEF], dtype=out.dtype)
    return out


def _gt_mask(shape, h: int, w: int) -> np.ndarray:
    mask = np.zeros(shape, dtype=bool)
    r0 = min(TAMPER_BASE_ROW, shape[0] - h)
    c0 = min(TAMPER_BASE_COL, shape[1] - w)
    mask[r0:r0 + h, c0:c0 + w] = True
    return mask


def phase_quality(files) -> tuple:
    rows = []
    failures = []
    print("== FASE A: kualitas & reversibilitas (jalur AES penuh) ==")
    head = f"{'slice':>8} | {'PSNR(wm)':>9} | {'SSIM(wm)':>9} | {'PSNR(rec)':>9} | {'SSIM(rec)':>9} | {'BER':>5} | {'exact':>5} | {'cap(bit)':>8} | {'t(s)':>6}"
    print(head)
    for f in files:
        name = os.path.basename(f)
        pixels, ds = load(f)
        meta = metadata_of(ds)
        t = time.perf_counter()
        wm = protect_image_rev(pixels, meta, passphrase=PASSPHRASE)
        ver = verify_image_rev(wm, meta, passphrase=PASSPHRASE)
        dt = time.perf_counter() - t

        ok = (ver["error"] is None) and (not ver["pixel_tamper"]) and ver["metadata_ok"]
        rec = ver["original_recovered"]
        region = pixels.shape[0] - PARAM_STRIP
        rec_region, orig_region = rec[:region].astype(np.int64), pixels[:region].astype(np.int64)
        exact = bool(np.array_equal(rec[:region], pixels[:region]))
        ber_val = float(np.count_nonzero(rec_region != orig_region) / orig_region.size)
        psnr_rec = rev.psnr(pixels, rec)
        psnr_wm = rev.psnr(pixels, wm)
        ssim_wm = mt.ssim(pixels, wm)
        ssim_rec = mt.ssim(pixels[:region], rec[:region])
        cap = _payload_bits(pixels, BLOCK, 16, encrypted=True)
        cap_est = sum(rev.pee_capacity_multi(pixels[:region], 16))

        row = {
            "slice": name, "psnr_wm": round(psnr_wm, 2), "ssim_wm": round(ssim_wm, 6),
            "psnr_rec": psnr_rec, "ssim_rec": round(ssim_rec, 6),
            "ber": round(ber_val, 8), "exact": exact, "cap_bits": cap, "cap_est_bits": cap_est,
            "runtime_s": round(dt, 3),
        }
        rows.append(row)
        print(f"{name[:8]:>8} | {psnr_wm:8.2f} | {ssim_wm:9.6f} | {str(psnr_rec):>9} | {ssim_rec:9.6f} | {ber_val:5.2f} | {'yes' if exact else 'no':>5} | {cap:8d} | {dt:6.2f}")
        if not (ok and exact):
            failures.append(name)

    n = len(rows)
    agg = {
        "n_slices": n,
        "ok_exact": n - len(failures),
        "psnr_wm": {"min": min(r["psnr_wm"] for r in rows), "max": max(r["psnr_wm"] for r in rows),
                    "mean": round(np.mean([r["psnr_wm"] for r in rows]), 2)},
        "ssim_wm": {"min": min(r["ssim_wm"] for r in rows), "max": max(r["ssim_wm"] for r in rows),
                    "mean": round(np.mean([r["ssim_wm"] for r in rows]), 6)},
        "ssim_rec": {"min": min(r["ssim_rec"] for r in rows), "max": max(r["ssim_rec"] for r in rows),
                     "mean": round(np.mean([r["ssim_rec"] for r in rows]), 6)},
        "cap_bits": {"min": min(r["cap_bits"] for r in rows), "max": max(r["cap_bits"] for r in rows),
                     "mean": round(np.mean([r["cap_bits"] for r in rows]), 1)},
        "runtime_s": {"min": min(r["runtime_s"] for r in rows), "max": max(r["runtime_s"] for r in rows),
                      "mean": round(np.mean([r["runtime_s"] for r in rows]), 3)},
    }
    print(f"\nRingkasan Fase A ({n} slice):")
    print(f"  PS NR(wm)   : {agg['psnr_wm']}")
    print(f"  SSIM(wm)    : {agg['ssim_wm']}")
    print(f"  SSIM(rec)   : {agg['ssim_rec']}")
    print(f"  PSNR(rec)   : semuanya inf (recovery {n - len(failures)}/{n} eksak)")
    print(f"  cap(bits)   : {agg['cap_bits']}")
    print(f"  runtime(s)  : {agg['runtime_s']}")
    return rows, agg, failures


def _evaluate_tamper_case(name, pixels, meta, scenario, encrypted):
    res = {"slice": name, "scenario": scenario[0], "encrypted": encrypted, "detected": None,
           "localized": False, "error": None, "confusion": None}
    try:
        wm = protect_image_rev(pixels, meta, passphrase=PASSPHRASE if encrypted else None)
    except ValueError as exc:
        res["error"] = f"protect: {exc}"
        return res

    h, w = scenario[1], scenario[2]
    tampered = _tamper(wm, h, w)
    ver = verify_image_rev(tampered, meta, passphrase=PASSPHRASE if encrypted else None)

    res["detected"] = bool(ver["pixel_tamper"] or ver["error"])
    mask = ver["mask"]
    if mask is not None and mask.any():
        res["localized"] = True
        gt = _gt_mask(pixels.shape, h, w)
        res["confusion"] = mt.block_confusion(gt, mask, BLOCK)
    return res


def phase_tamper(files, n_slices: int) -> tuple:
    subset = files[:n_slices]
    paths = [("plain", False), ("aes", True)]
    cases = []
    print(f"\n== FASE B: deteksi & lokalisasi tamper ({len(subset)} slice, 4 skenario x 2 jalur) ==")
    print("skenario TAMPER_BASE ditentukan di blok (10,16), ukuran bervariasi.")
    for f in subset:
        name = os.path.basename(f)
        pixels, ds = load(f)
        meta = metadata_of(ds)
        for scen in SCENARIOS:
            for pname, enc in paths:
                c = _evaluate_tamper_case(name, pixels, meta, scen, enc)
                cases.append(c)

    agg_by = {}
    for scen in SCENARIOS:
        for pname, enc in paths:
            sel = [c for c in cases if c["scenario"] == scen[0] and c["encrypted"] == enc]
            det = sum(1 for c in sel if c["detected"])
            loc = sum(1 for c in sel if c["localized"])
            confs = [c["confusion"] for c in sel if c["confusion"] is not None]
            m = mt.summarize_confusion(confs) if confs else {}
            agg_by[f"{scen[0]}|{pname}"] = {
                "n": len(sel), "detected": det, "localized": loc,
                "localization_available_rate": round(loc / len(sel), 3) if sel else 0.0,
                "metrics": {k: round(v, 4) for k, v in m.items()} if m else None,
            }

    print(f"{'skenario':>8} | {'jalur':>5} | {'deteksi':>7} | {'lokalisasi':>10} | {'acc':>6} | {'prec':>6} | {'rec':>6} | {'F1':>6} | {'IoU':>6} | {'FPR':>6}")
    for scen in SCENARIOS:
        for pname, _ in paths:
            a = agg_by[f"{scen[0]}|{pname}"]
            m = a["metrics"] or {}
            print(f"{scen[0]:>8} | {pname:>5} | {a['detected']:3d}/{a['n']:3d} | {a['localized']:3d}/{a['n']:3d} {a['localization_available_rate']:.2f} | {m.get('accuracy', 0):6.3f} | {m.get('precision', 0):6.3f} | {m.get('recall', 0):6.3f} | {m.get('f1', 0):6.3f} | {m.get('localization_iou', 0):6.3f} | {m.get('fpr', 0):6.3f}")
    return cases, agg_by


def main() -> bool:
    n_b = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    files = sorted(glob.glob(os.path.join(DCM_DIR, "*.dcm")))
    print(f"dataset: {len(files)} file DICOM di {DCM_DIR}")
    if not files:
        print("TIDAK ADA DATASET - jalankan dari folder proyek.")
        return False

    t0 = time.perf_counter()
    rows_a, agg_a, fail_a = phase_quality(files)
    cases_b, agg_b = phase_tamper(files, n_b)
    dur = time.perf_counter() - t0

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump({"quality": rows_a, "quality_agg": agg_a,
                   "tamper_agg": {k: v for k, v in agg_b.items()},
                   "meta": {"dataset": DCM_DIR, "n_slices": len(files), "passphrase": PASSPHRASE,
                            "runtime_total_s": round(dur, 2)}},
                  fh, indent=2)
    with open(OUT_CSV, "w", encoding="utf-8") as fh:
        fh.write("slice,psnr_wm,ssim_wm,psnr_rec,ssim_rec,ber,exact,cap_bits,cap_est_bits,runtime_s\n")
        for r in rows_a:
            fh.write(f"{r['slice']},{r['psnr_wm']},{r['ssim_wm']},{r['psnr_rec']},{r['ssim_rec']},"
                     f"{r['ber']},{int(r['exact'])},{r['cap_bits']},{r['cap_est_bits']},{r['runtime_s']}\n")

    print(f"\nHasil ditulis ke {OUT_JSON} dan {OUT_CSV}")
    print(f"waktu total: {dur:.1f}s")
    return len(fail_a) == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)