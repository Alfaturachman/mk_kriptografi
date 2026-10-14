"""Script untuk menghasilkan Diagram Alur Jurnal 300 DPI bergaya standar IEEE / Sinta.
Menghasilkan dua kolom paralel:
  (a) Embedding and Protection Flow (Pengirim)
  (b) Extraction and Recovery Flow (Penerima)
Gaya visual: Garis tegas hitam-putih, proporsional, font akademik bersih.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Polygon

def create_journal_flowchart(output_png, output_pdf=None):
    # Dimensi kanvas proporsional (lebar 12.0, tinggi 12.5 inci)
    fig, ax = plt.subplots(figsize=(12.0, 12.5), dpi=300)
    ax.set_xlim(0, 125)
    ax.set_ylim(5, 122)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Font styling akademik (DejaVu Sans)
    box_font = {"family": "DejaVu Sans", "weight": "normal", "size": 8.0}
    sub_font = {"family": "DejaVu Sans", "weight": "normal", "size": 7.0, "style": "italic"}
    key_font = {"family": "DejaVu Sans", "weight": "normal", "size": 7.3}
    caption_font = {"family": "DejaVu Sans", "weight": "bold", "size": 10.5}

    # Helper: draw rectangle box
    def draw_box(x, y, w, h, text, subtext=None, ec="black", fc="white", lw=1.3):
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="square,pad=0",
                              ec=ec, fc=fc, lw=lw)
        ax.add_patch(rect)
        if subtext:
            ax.text(x, y + 0.85, text, ha="center", va="center", fontdict=box_font)
            ax.text(x, y - 1.05, subtext, ha="center", va="center", fontdict=sub_font)
        else:
            ax.text(x, y, text, ha="center", va="center", fontdict=box_font)
        return (x, y, w, h)

    # Helper: draw doc / rounded box
    def draw_doc(x, y, w, h, text, subtext=None):
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0,rounding_size=1.2",
                              ec="black", fc="#F8FAFC", lw=1.4)
        ax.add_patch(rect)
        if subtext:
            ax.text(x, y + 0.85, text, ha="center", va="center", fontdict={"family": "DejaVu Sans", "weight": "bold", "size": 8.2})
            ax.text(x, y - 1.05, subtext, ha="center", va="center", fontdict=sub_font)
        else:
            ax.text(x, y, text, ha="center", va="center", fontdict={"family": "DejaVu Sans", "weight": "bold", "size": 8.2})
        return (x, y, w, h)

    # Helper: draw diamond (decision / loop check)
    def draw_diamond(x, y, w, h, text, subtext=None):
        pts = [[x, y + h/2], [x + w/2, y], [x, y - h/2], [x - w/2, y]]
        poly = Polygon(pts, closed=True, ec="black", fc="white", lw=1.4)
        ax.add_patch(poly)
        if subtext:
            ax.text(x, y + 0.75, text, ha="center", va="center", fontdict=box_font)
            ax.text(x, y - 0.95, subtext, ha="center", va="center", fontdict=sub_font)
        else:
            ax.text(x, y, text, ha="center", va="center", fontdict=box_font)
        return (x, y, w, h)

    # Helper: draw arrow
    def draw_arrow(x1, y1, x2, y2, text=None, text_offset=(1.5, 0)):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color="black", lw=1.3, mutation_scale=11))
        if text:
            ax.text((x1 + x2)/2 + text_offset[0], (y1 + y2)/2 + text_offset[1], text,
                    fontdict=key_font, va="center", ha="left")

    # Helper: draw key entry
    def draw_key_input(bx, by, bw, key_name, key_desc):
        kx = bx + bw/2 + 8.5
        ax.annotate("", xy=(bx + bw/2, by), xytext=(kx, by),
                    arrowprops=dict(arrowstyle="-|>", color="black", lw=1.3, mutation_scale=11))
        circ = plt.Circle((kx + 1.2, by), 1.0, ec="black", fc="white", lw=1.3)
        ax.add_patch(circ)
        ax.plot([kx, kx + 1.2 - 0.9], [by, by], color="black", lw=1.3)
        ax.text(kx + 2.8, by + 0.7, key_name, va="center", ha="left", fontdict=key_font)
        ax.text(kx + 2.8, by - 0.9, key_desc, va="center", ha="left", fontdict=sub_font)

    # =========================================================================
    # KOLOM A: (a) Embedding & Protection Flow (xa = 28)
    # =========================================================================
    xa = 28
    ya = 116
    bw = 27
    bh = 4.8

    # 1. Input Document
    draw_doc(xa, ya, bw, 5.0, "Citra Medis DICOM Asli", "Matriks 448x364 (16-bit) + Metadata")
    draw_arrow(xa, ya - 2.5, xa, ya - 6.2)
    ya -= 8.6

    # 2. Partisi ROI & RONI
    draw_box(xa, ya, bw, bh, "Partisi ROI & Strip RONI", "ROI: 432x364 px | RONI: 16x364 px")
    draw_arrow(xa, ya - 2.4, xa, ya - 6.2)
    ya -= 8.6

    # 3. Ekstraksi Hash & Digest
    draw_box(xa, ya, bw, bh, "Ekstraksi Hash & Digest", "Hash Blok (ROI >> 1) + SHA-256 Meta")
    draw_arrow(xa, ya - 2.4, xa, ya - 6.2)
    ya -= 8.6

    # 4. Konstruksi Payload Biner
    draw_box(xa, ya, bw, bh, "Konstruksi Payload Biner", "Header (RPEE01) + Digest + Hashes")
    draw_arrow(xa, ya - 2.4, xa, ya - 6.2)
    ya -= 8.6

    # 5. Enkripsi AES-256-CBC
    draw_box(xa, ya, bw, bh, "Enkripsi AES-256-CBC", "Ciphertext Bitstream (10.144 bit)")
    draw_key_input(xa, ya, bw, "Passphrase K", "AES-256 (PBKDF2)")
    draw_arrow(xa, ya - 2.4, xa, ya - 6.2)
    ya -= 8.8

    # 6. Loop Decision: Round Checking
    y_loop_a = ya
    draw_diamond(xa, ya, 24, 5.8, "Cek Nomor Round", "r <= 16 & Bit Tersisa?")
    draw_arrow(xa, ya - 2.9, xa, ya - 6.2, text="Ya", text_offset=(0.8, 0))
    ya -= 8.8

    # 7. MED Prediksi
    draw_box(xa, ya, bw, bh, "Prediksi MED Checkerboard", "Hitung Galat: e = x - x_hat")
    draw_arrow(xa, ya - 2.4, xa, ya - 6.2)
    ya -= 8.6

    # 8. PEE-HS Embedding & Shifting
    draw_box(xa, ya, bw, bh, "PEE-HS Embedding & Shifting", "e' = 2e + b (peak e0) & Shifting")

    # Loop back arrow (on left of col A)
    x_ret_a = xa - 17.5
    ax.plot([xa - bw/2, x_ret_a], [ya, ya], color="black", lw=1.3)
    ax.plot([x_ret_a, x_ret_a], [ya, y_loop_a], color="black", lw=1.3)
    ax.annotate("", xy=(xa - 12.0, y_loop_a), xytext=(x_ret_a, y_loop_a),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.3, mutation_scale=11))
    ax.text(x_ret_a - 1.2, (ya + y_loop_a)/2, "Iterasi Round (r = r + 1)",
            rotation=90, va="center", ha="right", fontdict=sub_font)

    # Exit arrow (Selesai -> Simpan Parameter)
    x_exit_a = xa + 16.0
    y_exit_a = ya - 8.6
    ax.plot([xa + 12.0, x_exit_a], [y_loop_a, y_loop_a], color="black", lw=1.3)
    ax.text(xa + 13.0, y_loop_a + 1.2, "Selesai (r > R)", fontdict=sub_font)
    ax.plot([x_exit_a, x_exit_a], [y_loop_a, y_exit_a], color="black", lw=1.3)
    ax.annotate("", xy=(xa, y_exit_a), xytext=(x_exit_a, y_exit_a),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.3, mutation_scale=11))

    ya = y_exit_a

    # 9. Simpan Parameter PEE
    draw_box(xa, ya, bw, bh, "Simpan Parameter PEE", "Format JSON -> LSB Strip RONI")
    draw_arrow(xa, ya - 2.4, xa, ya - 6.2)
    ya -= 8.8

    # 10. Output Document: Watermarked DICOM
    draw_doc(xa, ya, bw, 5.0, "Citra Ter-Watermark (Iw)", "PSNR ~86,35 dB | SSIM 0,999995")


    # =========================================================================
    # KOLOM B: (b) Extraction & Recovery Flow (xb = 86)
    # =========================================================================
    xb = 86
    yb = 116

    # 1. Input Document: Watermarked DICOM
    draw_doc(xb, yb, bw, 5.0, "Citra Ter-Watermark (I'w)", "Penerimaan via Jaringan PACS")
    draw_arrow(xb, yb - 2.5, xb, yb - 6.2)
    yb -= 8.6

    # 2. Ekstraksi Parameter
    draw_box(xb, yb, bw, bh, "Ekstraksi Parameter PEE", "Baca LSB Strip RONI -> Parse JSON")
    draw_arrow(xb, yb - 2.4, xb, yb - 6.2)
    yb -= 8.6

    # 3. Loop Decision: Inverse Round Check
    y_loop_b = yb
    draw_diamond(xb, yb, 24, 5.8, "Cek Round Invers", "r >= 1 (Mundur 16 -> 1)?")
    draw_arrow(xb, yb - 2.9, xb, yb - 6.2, text="Ya", text_offset=(0.8, 0))
    yb -= 8.8

    # 4. Inverse PEE-HS
    draw_box(xb, yb, bw, bh, "Pembalikan Galat PEE-HS", "e = floor(e'/2) | De-Shifting")
    draw_arrow(xb, yb - 2.4, xb, yb - 6.2)
    yb -= 8.6

    # 5. Ekstraksi Bit Ciphertext
    draw_box(xb, yb, bw, bh, "Ekstraksi Bit & Pulihkan Piksel", "b = e' mod 2 | x = x_hat + e")

    # Loop back arrow (on left of col B)
    x_ret_b = xb - 17.5
    ax.plot([xb - bw/2, x_ret_b], [yb, yb], color="black", lw=1.3)
    ax.plot([x_ret_b, x_ret_b], [yb, y_loop_b], color="black", lw=1.3)
    ax.annotate("", xy=(xb - 12.0, y_loop_b), xytext=(x_ret_b, y_loop_b),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.3, mutation_scale=11))
    ax.text(x_ret_b - 1.2, (yb + y_loop_b)/2, "Iterasi Invers (r = r - 1)",
            rotation=90, va="center", ha="right", fontdict=sub_font)

    # Exit arrow (Selesai invers -> Dekripsi)
    x_exit_b = xb + 16.0
    y_exit_b = yb - 8.6
    ax.plot([xb + 12.0, x_exit_b], [y_loop_b, y_loop_b], color="black", lw=1.3)
    ax.text(xb + 13.0, y_loop_b + 1.2, "Selesai (r < 1)", fontdict=sub_font)
    ax.plot([x_exit_b, x_exit_b], [y_loop_b, y_exit_b], color="black", lw=1.3)
    ax.annotate("", xy=(xb, y_exit_b), xytext=(x_exit_b, y_exit_b),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.3, mutation_scale=11))

    yb = y_exit_b

    # 6. Dekripsi AES-256 Payload (Key enters from right)
    draw_box(xb, yb, bw, bh, "Dekripsi AES-256-CBC", "Validasi PKCS#7 & Parse Payload")
    draw_key_input(xb, yb, bw, "Passphrase K", "AES-256 (PBKDF2)")
    draw_arrow(xb, yb - 2.4, xb, yb - 6.2)
    yb -= 8.6

    # 7. Hitung Ulang Hash & Digest
    draw_box(xb, yb, bw, bh, "Hitung Ulang Hash & Digest", "Hash (I_rec >> 1) & SHA-256 Meta")
    draw_arrow(xb, yb - 2.4, xb, yb - 6.2)
    yb -= 8.8

    # 8. Decision Diamond: Integritas Valid?
    draw_diamond(xb, yb, 24, 5.8, "Pencocokan Integritas", "Hash & Digest Cocok 100%?")

    # Arrow Tidak (Tamper) to right side
    ax.plot([xb + 12.0, xb + 19.5], [yb, yb], color="black", lw=1.3)
    ax.text(xb + 13.0, yb + 1.1, "Tidak", fontdict=key_font)
    ax.plot([xb + 19.5, xb + 19.5], [yb, yb - 5.0], color="black", lw=1.3)
    ax.annotate("", xy=(xb + 19.5, yb - 6.8), xytext=(xb + 19.5, yb - 5.0),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.3, mutation_scale=11))
    draw_box(xb + 19.5, yb - 9.2, 15.5, 4.4, "Alarm Tamper", "Mask Spasial 16x16", ec="#DC2626", fc="#FEF2F2", lw=1.3)

    # Arrow Ya (Valid) straight down
    draw_arrow(xb, yb - 2.9, xb, yb - 6.2, text="Ya", text_offset=(0.8, 0))
    yb -= 8.8

    # 9. Output Document: Bit-Exact Restored DICOM (Narrower width to avoid overlap)
    draw_doc(xb - 1.5, yb, bw - 2.0, 5.0, "Citra Asli Eksak (I_rec)", "Bit-Exact 100% | PSNR = inf, BER = 0")


    # =========================================================================
    # CAPTIONS & FOOTNOTE (Sejajar Horisontal Sempurna)
    # =========================================================================
    y_caption = 28.0
    ax.text(xa, y_caption, "(a) Alur Penyisipan & Proteksi (Pengirim)",
            ha="center", va="center", fontdict=caption_font)
    ax.text(xb, y_caption, "(b) Alur Pemulihan & Verifikasi (Penerima)",
            ha="center", va="center", fontdict=caption_font)

    # Footnote Box di bagian bawah
    note_box = FancyBboxPatch((12, 10.0), 101, 13.5, boxstyle="round,pad=0,rounding_size=1.2",
                              ec="#64748B", fc="#F8FAFC", lw=1.1, ls="--")
    ax.add_patch(note_box)
    ax.text(62.5, 19.5, "Keterangan Spesifikasi Sistem:", ha="center", fontdict={"family": "DejaVu Sans", "weight": "bold", "size": 8.5})
    ax.text(62.5, 15.0, "• ROI Diagnostik: 432x364 px (dipulihkan eksak bitwise 100%) | Strip RONI: 16x364 px (side-channel parameter PEE via LSB)\n• Derivasi Kunci: PBKDF2 (200.000 iterasi HMAC-SHA256) | Autentikasi: Hash Blok 16-bit (594 blok) + Digest SHA-256\n• Cipher Payload: AES-256-CBC dengan Salt (16B), IV (16B), dan PKCS#7 Padding",
            ha="center", fontdict={"family": "DejaVu Sans", "size": 7.4, "color": "#334155"})

    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_png, dpi=300, bbox_inches="tight")
    print(f"Grafik PNG disimpan ke: {output_png}")
    if output_pdf:
        plt.savefig(output_pdf, bbox_inches="tight")
        print(f"Grafik PDF vektor disimpan ke: {output_pdf}")
    plt.close()

if __name__ == "__main__":
    png_path = os.path.join(os.path.dirname(__file__), "figures", "diagram_alur_jurnal.png")
    pdf_path = os.path.join(os.path.dirname(__file__), "figures", "diagram_alur_jurnal.pdf")
    create_journal_flowchart(png_path, pdf_path)
