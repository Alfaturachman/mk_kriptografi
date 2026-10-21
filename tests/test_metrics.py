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

    print("== 10 Parameter Evaluasi Dosen ==")
    # 1. MSE
    check("calc_mse identik -> 0.0", mt.calc_mse(a16, a16) == 0.0)
    check("calc_mse beda > 0", mt.calc_mse(a8, noisy) > 0.0)

    # 2. PSNR
    check("calc_psnr mse=0 -> inf", mt.calc_psnr(0.0) == float("inf"))
    check("calc_psnr mse>0 -> finite", mt.calc_psnr(10.0, 65535.0) > 80.0)

    # 3. SSIM Robust
    check("calc_ssim_robust 2D -> 1.0", mt.calc_ssim_robust(a16, a16) == 1.0)

    # 4. NPCR & UACI
    check("calc_npcr identik -> 0.0", mt.calc_npcr(a16, a16) == 0.0)
    check("calc_npcr beda > 0", mt.calc_npcr(a8, noisy) > 0.0)
    check("calc_uaci identik -> 0.0", mt.calc_uaci(a16, a16) == 0.0)
    check("calc_uaci beda > 0", mt.calc_uaci(a8, noisy, 255.0) > 0.0)

    # 5. Entropy
    check("calc_entropy > 0", mt.calc_entropy(a8) > 5.0)
    check("calc_entropy_bytes > 0", mt.calc_entropy_bytes(b"sample ciphertext bytes 1234567890" * 10) > 3.0)

    # 6. NC & NCC
    check("calc_nc identik -> 1.0", abs(mt.calc_nc(a16, a16) - 1.0) < 1e-6)
    check("calc_ncc identik -> 1.0", abs(mt.calc_ncc(a16, a16) - 1.0) < 1e-6)

    # 7. Chi-Square
    check("calc_chi_square_hist identik -> 0.0", mt.calc_chi_square_hist(a8, a8) == 0.0)
    chi2_val, p_val = mt.calc_chi_square_uniformity_bytes(b"uniform_bytes_sample" * 20)
    check("calc_chi_square_uniformity_bytes -> tuple", chi2_val >= 0.0 and 0.0 <= p_val <= 1.0)

    # 8. BER
    check("calc_ber identik -> 0.0", mt.calc_ber(a16, a16) == 0.0)
    check("calc_ber beda > 0", mt.calc_ber(a8, noisy) > 0.0)

    # 9. evaluate_comprehensive_metrics
    eval_res = mt.evaluate_comprehensive_metrics(a16, a16, rec=a16, cipher_bytes=b"cipher" * 50, is_dicom=False)
    check("eval_res mse_rec -> 0.0", eval_res["mse_rec"] == 0.0)
    check("eval_res psnr_rec -> inf", eval_res["psnr_rec"] == float("inf"))
    check("eval_res ssim_rec -> 1.0", eval_res["ssim_rec"] == 1.0)
    check("eval_res ber_rec -> 0.0", eval_res["ber_rec"] == 0.0)
    check("eval_res ber_rec_str formatted", eval_res["ber_rec_str"] == "0.00000000")

    print(f"\nHasil: {total - len(failures)}/{total}")
    return len(failures) == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)