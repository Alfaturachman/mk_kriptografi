import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto import metrics as mt

failures = []
total = 0


def check(name, cond, detail=""):
    global total
    total += 1
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name} {detail}")
    if not cond:
        failures.append(name)


def main():
    rng = np.random.default_rng(7)
    a8 = rng.integers(0, 256, size=(64, 64)).astype(np.uint8)
    a16 = rng.integers(0, 65536, size=(64, 64)).astype(np.uint16)

    print("== SSIM ==")
    check("identik uint8 -> 1.0", mt.ssim(a8, a8) == 1.0, f"got={mt.ssim(a8, a8):.6f}")
    check("identik uint16 -> 1.0", mt.ssim(a16, a16) == 1.0, f"got={mt.ssim(a16, a16):.6f}")
    noisy = np.clip(a8.astype(np.int16) + rng.integers(-2, 3, size=a8.shape), 0, 255).astype(np.uint8)
    s_noisy = mt.ssim(a8, noisy)
    zero = np.zeros_like(a8)
    s_zero = mt.ssim(a8, zero)
    check("noise kecil -> SSIM masih tinggi", s_noisy > 0.9, f"got={s_noisy:.4f}")
    check("citra vs nol -> SSIM rendah", s_zero < 0.1, f"got={s_zero:.4f}")

    print("== block_confusion ==")
    gt = np.zeros((64, 64), dtype=bool)
    gt[16:32, 16:32] = True  # blok (1,1) ukuran 1 blok 16x16
    pred = np.zeros((64, 64), dtype=bool)
    pred[16:32, 16:48] = True  # 2 blok (1,1) & (1,2)
    r = mt.block_confusion(gt, pred, block=16)
    # grid 4x4=16 blok; gt=1, pred=2, tp=1 fp=1 fn=0 tn=14
    check("tp=1", r["tp"] == 1, f"got={r}")
    check("fp=1", r["fp"] == 1)
    check("fn=0", r["fn"] == 0)
    check("precision=0.5", abs(r["precision"] - 0.5) < 1e-9)
    check("recall=1.0", r["recall"] == 1.0)
    check("accuracy=15/16", abs(r["accuracy"] - 15 / 16) < 1e-9)
    check("iou=1/2", abs(r["localization_iou"] - 1 / 2) < 1e-9)
    check("fpr=1/15", abs(r["fpr"] - 1 / 15) < 1e-9)

    r = mt.block_confusion(np.zeros((64, 64), dtype=bool), np.zeros((64, 64), dtype=bool))
    check("bersih -> tak ada FP", r["fp"] == 0 and r["precision"] == 1.0 and r["recall"] == 0.0, f"got={r}")

    agg = mt.summarize_confusion([r, r])
    check("agregasi merata", "precision" in agg and "recall" in agg, f"got={agg}")

    print(f"\nHasil: {total - len(failures)}/{total}")
    return len(failures) == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)