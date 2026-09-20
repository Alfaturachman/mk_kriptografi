"""Skema reversible watermarking - prototipe Fase 5A.

Teknik utama: **Histogram Shifting bertingkat (HS-L)**.
  - Self-contained, eksak (citra asli kembali sama per-bit).
  - Kapasitas = f  x  L  bit, dengan f = frekuensi bin peak, L = bit per piksel peak.
  - Generalisasi yang benar: shift sebesar S = 2**L - 1 agar nilai embedded
    b in [0, S] menempati bin kosong p+1..p+S tanpa tabrakan.

Teknik cadangan: **Difference Expansion (DE)** (perlu location map / DE-safe).

Catatan prototipe:
  - Side-channel (peak/L/direction) dikembalikan via dict `params`; akan diembed
    ke dalam payload pada integrasi Fase 5B/5C.
  - Asumsi HS-L: max(piksel) + S <= nilai maks dtype (tipikal citra medis 16-bit).
"""

import numpy as np


def _to_bits(data: bytes) -> np.ndarray:
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8)).astype(np.int64)


def _from_bits(bits) -> bytes:
    return np.packbits(np.asarray(bits, dtype=np.uint8)).tobytes()


def _dtype_max(img: np.ndarray) -> int:
    return int(np.iinfo(img.dtype).max)


def _shift_for(levels: int) -> int:
    return (1 << levels) - 1


def _hs_params(img: np.ndarray, max_levels: int) -> dict:
    hi = _dtype_max(img)
    hist = np.bincount(img.ravel(), minlength=hi + 1)
    peak = int(np.argmax(hist))
    freq = int(hist[peak])
    if freq == 0:
        raise ValueError("HS: bin peak kosong")

    # cari L terbesar dengan S = 2**L - 1 memenuhi: bin p+1..p+S kosong
    best = 0
    for levels in range(1, max_levels + 1):
        s = _shift_for(levels)
        if peak + s >= hi:
            break
        if hist[peak + 1 : peak + s + 1].sum() == 0:
            best = levels
        else:
            break
    if best == 0:
        raise ValueError("HS: tidak ada bin kosong setelah peak")
    vmax = int(img.max())
    if vmax + _shift_for(best) > hi:
        best = max(best - 1, 1)
    return {"peak": peak, "levels": best, "freq": freq, "shift": _shift_for(best)}


def hs_l_capacity(img: np.ndarray, max_levels: int = 8) -> int:
    try:
        par = _hs_params(img, max_levels)
    except ValueError:
        return 0
    return par["freq"] * par["levels"]


def hs_l_embed(img: np.ndarray, bits, max_levels: int = 8) -> tuple:
    bits = np.asarray(bits, dtype=np.int64)
    par = _hs_params(img, max_levels)
    p, lvl, s = par["peak"], par["levels"], par["shift"]

    out = np.array(img, dtype=np.int64, copy=True)
    movable = out > p
    out[movable] += s

    cap = par["freq"] * lvl
    n_bits = min(len(bits), cap)
    n_bits = n_bits - (n_bits % lvl)
    take = bits[:n_bits]
    n_px = n_bits // lvl

    vals = np.zeros(n_px, dtype=np.int64)
    for k in range(lvl):
        vals = (vals << 1) | take[k::lvl]

    idx = np.flatnonzero(out.ravel() == p)[:n_px]
    flat = out.ravel()
    flat[idx] = p + vals
    out = flat.reshape(img.shape).astype(img.dtype)

    return out, {**par, "n_bits": int(n_bits)}


def hs_l_extract(img: np.ndarray, n_bits: int, peak: int, levels: int) -> np.ndarray:
    s = _shift_for(levels)
    flat = np.asarray(img).ravel()
    idx = np.flatnonzero((flat >= peak) & (flat <= peak + s))[: n_bits // levels]
    res = np.zeros(n_bits, dtype=np.int64)
    if len(idx) == 0:
        return res
    b_vals = flat[idx].astype(np.int64) - peak
    for k in range(levels):
        res[k::levels] = (b_vals >> (levels - 1 - k)) & 1
    return res


def hs_l_reverse(img: np.ndarray, params: dict) -> np.ndarray:
    out = np.asarray(img, dtype=np.int64).copy()
    p = params["peak"]
    s = params["shift"]
    emb = (out >= p) & (out <= p + s)
    out[emb] = p
    band = out > p + s
    out[band] -= s
    return out.astype(img.dtype)


def de_capacity(img: np.ndarray) -> int:
    h, w = img.shape
    return h * (w // 2)


def _de_bounds(img: np.ndarray) -> bool:
    x = img.astype(np.int64)[:, ::2]
    y = img.astype(np.int64)[:, 1::2]
    a = (x + y) // 2
    d = x - y
    d2 = 2 * d + 1
    xp = a + (d2 + 1) // 2
    yp = a - (d2 // 2)
    hi = _dtype_max(img)
    return bool((xp >= 0).all() and (yp >= 0).all() and (xp <= hi).all() and (yp <= hi).all())


def de_embed(img: np.ndarray, bits) -> tuple:
    if not _de_bounds(img):
        raise ValueError("citra tidak DE-safe (ada pasangan yang overflow)")
    bits = np.asarray(bits, dtype=np.int64)
    n = de_capacity(img)
    if len(bits) > n:
        raise ValueError("payload melebihi kapasitas DE")
    pad = np.zeros(n, dtype=np.int64)
    pad[: len(bits)] = bits
    pad = pad.reshape(img.shape[0], img.shape[1] // 2)

    out = np.array(img, dtype=np.int64, copy=True)
    x = out[:, ::2]
    y = out[:, 1::2]
    a = (x + y) // 2
    d = x - y
    d2 = 2 * d + pad
    out[:, ::2] = a + (d2 + 1) // 2
    out[:, 1::2] = a - (d2 // 2)
    return out.astype(img.dtype), {"n_bits": int(len(bits))}


def de_extract(img: np.ndarray, n_bits: int) -> np.ndarray:
    x = np.asarray(img, dtype=np.int64)[:, ::2]
    y = np.asarray(img, dtype=np.int64)[:, 1::2]
    return ((x - y) & 1).ravel()[:n_bits]


def de_reverse(img: np.ndarray, params: dict) -> np.ndarray:
    out = np.asarray(img, dtype=np.int64).copy()
    x = out[:, ::2]
    y = out[:, 1::2]
    a = (x + y) // 2
    d = (x - y) // 2
    out[:, ::2] = a + (d + 1) // 2
    out[:, 1::2] = a - (d // 2)
    return out.astype(img.dtype)


def _pee_mask(img: np.ndarray) -> np.ndarray:
    n, m = img.shape
    rr = np.arange(n)[:, None]
    cc = np.arange(m)[None, :]
    return (rr % 2 == 0) & (cc % 2 == 0) & (rr >= 2) & (cc >= 2)


def _pee_pred(img: np.ndarray) -> np.ndarray:
    left = np.roll(img, 1, axis=1)
    up = np.roll(img, 1, axis=0)
    upleft = np.roll(np.roll(img, 1, axis=0), 1, axis=1)
    with np.errstate(invalid="ignore"):
        pred = np.where(
            upleft >= np.maximum(left, up),
            np.minimum(left, up),
            np.where(
                upleft <= np.minimum(left, up),
                np.maximum(left, up),
                left + up - upleft,
            ),
        )
    return np.clip(pred.astype(np.int64), 0, _dtype_max(img))


def _pee_error_full(img: np.ndarray) -> np.ndarray:
    hi = _dtype_max(img)
    if int(img.max()) + 2 > hi:
        raise ValueError("PEE: nilai piksel terlalu dekat ke batas maks dtype")
    pred = _pee_pred(img)
    mask = _pee_mask(img)
    return (img.astype(np.int64) - pred)[mask]


def _pee_params(img: np.ndarray) -> dict:
    err = _pee_error_full(img)
    offset = int(err.min())
    hist = np.bincount(err.ravel() - offset)
    peak = int(np.argmax(hist)) + offset
    zeros = np.flatnonzero(hist == 0) + offset
    left = zeros[zeros < peak]
    right = zeros[zeros > peak]
    if right.size:
        z, direction = int(right[0]), 1
    elif left.size:
        z, direction = int(left[-1]), -1
    else:
        raise ValueError("PEE: tidak ada bin error kosong")
    return {
        "peak": peak,
        "z": int(z),
        "direction": int(direction),
        "freq": int(hist[peak - offset]),
    }


def pee_capacity(img: np.ndarray) -> int:
    try:
        return _pee_params(img)["freq"]
    except ValueError:
        return 0


def pee_embed(img: np.ndarray, bits) -> tuple:
    par = _pee_params(img)
    e0, z, direction = par["peak"], par["z"], par["direction"]
    n_bits = min(len(bits), par["freq"])

    mask = _pee_mask(img)
    pred = _pee_pred(img)
    err = (img.astype(np.int64) - pred) * mask

    flat = err[mask]
    if direction == 1:
        flat[(flat > e0) & (flat < z)] += 1
    else:
        flat[(flat > z) & (flat < e0)] -= 1

    take = np.asarray(bits, dtype=np.int64)[:n_bits]
    idx = np.flatnonzero(flat == e0)[:n_bits]
    flat[idx[take == 1]] = e0 + direction

    err[mask] = flat
    out = np.array(img, dtype=np.int64, copy=True)
    out[mask] = pred[mask] + err[mask]
    return out.clip(0, _dtype_max(img)).astype(img.dtype), {**par, "n_bits": int(n_bits)}


def pee_extract(img: np.ndarray, n_bits: int, peak: int, direction: int) -> np.ndarray:
    mask = _pee_mask(img)
    pred = _pee_pred(img)
    flat = ((img.astype(np.int64) - pred) * mask)[mask]
    hits = flat[(flat == peak) | (flat == peak + direction)]
    return (hits == peak + direction).astype(np.int64)[:n_bits]


def pee_reverse(img: np.ndarray, params: dict) -> np.ndarray:
    e0, z, direction = params["peak"], params["z"], params["direction"]
    mask = _pee_mask(img)
    pred = _pee_pred(img)
    flat = ((img.astype(np.int64) - pred) * mask)[mask]
    emb = (flat == e0) | (flat == e0 + direction)
    flat[emb] = e0
    if direction == 1:
        flat[(flat > e0 + 1) & (flat <= z)] -= 1
    else:
        flat[(flat >= z) & (flat < e0 - 1)] += 1
    err = np.zeros_like(img, dtype=np.int64)
    err[mask] = flat
    out = np.array(img, dtype=np.int64, copy=True)
    out[mask] = pred[mask] + err[mask]
    return out.clip(0, _dtype_max(img)).astype(img.dtype)


def pee_capacity_multi(img: np.ndarray, max_rounds: int = 8) -> list:
    caps = []
    cur = img
    for _ in range(max_rounds):
        c = pee_capacity(cur)
        if c < 1:
            break
        caps.append(c)
        try:
            cur, _ = pee_embed(cur, np.zeros(c, dtype=np.int64))
        except ValueError:
            break
    return caps


def pee_embed_multi(img: np.ndarray, bits, max_rounds: int = 8) -> tuple:
    bits = np.asarray(bits, dtype=np.int64)
    cur = img
    rounds = []
    total = 0
    for _ in range(max_rounds):
        wm, par = pee_embed(cur, bits[total:])
        if par["n_bits"] == 0:
            break
        rounds.append(par)
        total += par["n_bits"]
        cur = wm
        if total >= len(bits):
            break
    return cur, rounds


def pee_extract_multi(image_stack, rounds: list) -> np.ndarray:
    bits_all = []
    cur = image_stack
    for par in reversed(rounds):
        got = pee_extract(cur, par["n_bits"], par["peak"], par["direction"])
        bits_all.append(got)
        cur = pee_reverse(cur, par)
    return np.concatenate(bits_all[::-1])


def pee_reverse_multi(img: np.ndarray, rounds: list) -> np.ndarray:
    cur = img
    for par in reversed(rounds):
        cur = pee_reverse(cur, par)
    return cur


def psnr(original: np.ndarray, modified: np.ndarray) -> float:
    mse = float(np.mean((original.astype(np.float64) - modified.astype(np.float64)) ** 2))
    if mse == 0:
        return float("inf")
    hi = _dtype_max(original)
    return float(10 * np.log10(hi * hi / mse))


def ber(a_bits, b_bits) -> float:
    n = min(len(a_bits), len(b_bits))
    if n == 0:
        return 1.0
    return float(np.count_nonzero(np.asarray(a_bits)[:n] != np.asarray(b_bits)[:n]) / n)