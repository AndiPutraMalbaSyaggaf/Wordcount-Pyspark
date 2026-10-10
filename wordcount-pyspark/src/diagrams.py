import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams["font.family"] = "DejaVu Sans"

def box(ax, x, y, w, h, text, fc, ec="#333", fs=6.6, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1))
    if text: ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal", linespacing=1.25)
def arrow(ax, x1, y1, x2, y2, color="#333", lw=1.2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=9, color=color, lw=lw))

# ---------- Gambar 1: pipeline (7.0 inci = lebar halaman)
fig, ax = plt.subplots(figsize=(7.0, 2.7)); ax.set_xlim(0, 22); ax.set_ylim(0, 8.3); ax.axis("off")
steps = [("Dataset teks\n100.000 baris", "#dbeafe", "INPUT"),
         ("Baca data\ntextFile()\n→ P partition", "#e9d5ff", "NARROW"),
         ("Preprocessing\nflatMap():\nlower, hapus\ntanda baca,\nsplit", "#fde68a", "NARROW"),
         ("Filter + Map\nfilter()\nmap(w→(w,1))", "#fde68a", "NARROW"),
         ("Agregasi\nreduceByKey()\n+ combiner\nlokal", "#fecaca", "SHUFFLE #1"),
         ("Urutkan\nsortBy(freq)\nrange\npartition", "#fecaca", "SHUFFLE #2"),
         ("ACTION\ntake(10)", "#bbf7d0", "TRIGGER")]
w, gap, x = 2.8, 0.33, 0.1
for i, (t, c, tag) in enumerate(steps):
    box(ax, x, 2.6, w, 3.6, t, c, fs=6.4)
    ax.text(x + w/2, 6.7, tag, ha="center", fontsize=6.4, fontweight="bold",
            color="#b91c1c" if "SHUFFLE" in tag else "#065f46" if tag == "TRIGGER" else "#1e3a8a")
    if i < 6: arrow(ax, x + w, 4.4, x + w + gap, 4.4)
    x += w + gap
s1 = 0.1 + 4*(w+gap) - gap/2; s2 = 0.1 + 5*(w+gap) - gap/2
for sx in (s1, s2): ax.plot([sx, sx], [1.4, 7.6], ls="--", color="#b91c1c", lw=1)
ax.text(s1/2, 1.9, "STAGE 1: narrow, 1 task per partition", ha="center", fontsize=6.4, color="#1e3a8a", fontweight="bold")
ax.text((s1+s2)/2, 1.9, "STAGE 2", ha="center", fontsize=6.4, color="#1e3a8a", fontweight="bold")
ax.text((s2+22)/2, 1.9, "STAGE 3 (hasil)", ha="center", fontsize=6.4, color="#1e3a8a", fontweight="bold")
ax.text(11, 0.6, "Garis putus-putus merah = batas stage (shuffle: data dipindah antar-executor lewat disk/jaringan)", ha="center", fontsize=6, style="italic", color="#444")
ax.set_title("Gambar 1. Pipeline pemrosesan data WordCount", fontsize=7.6, fontweight="bold", loc="left")
plt.tight_layout(pad=.3); plt.savefig("results/fig_pipeline.png", dpi=260); plt.close()

# ---------- Gambar 2: Job -> Stage -> Task
fig, ax = plt.subplots(figsize=(7.0, 4.0)); ax.set_xlim(0, 22); ax.set_ylim(0, 12.6); ax.axis("off")
box(ax, 0.1, 5.2, 2.7, 2.2, "Action\ntake(10)", "#bbf7d0", bold=True, fs=6.8)
box(ax, 3.5, 5.2, 3.2, 2.2, "Spark Job\n1 job per action\n(DAG dibuat oleh\nDAGScheduler)", "#dbeafe", bold=True, fs=6.2)
arrow(ax, 2.8, 6.3, 3.5, 6.3)
def stage(y, title, desc, fc):
    box(ax, 7.6, y, 5.2, 3.5, "", fc)
    ax.text(10.2, y+3.15, title, ha="center", fontsize=6.6, fontweight="bold", va="center")
    ax.text(10.2, y+2.35, desc, ha="center", fontsize=5.9, va="center", linespacing=1.3)
    for i in range(4): box(ax, 7.85 + i*1.2, y+.2, 1.1, .95, f"T{i}" if i < 3 else "…", "#fff", fs=6.2)
stage(8.7, "Stage 1 (ShuffleMapStage)", "textFile → flatMap → filter → map\n+ combiner reduceByKey (sisi map)", "#fef3c7")
stage(4.45, "Stage 2 (ShuffleMapStage)", "reduceByKey sisi reduce\n(setelah shuffle #1)", "#fee2e2")
stage(0.2, "Stage 3 (ResultStage)", "sortBy (setelah shuffle #2)\ntake(10) → hasil ke Driver", "#dcfce7")
arrow(ax, 6.7, 6.8, 7.6, 10.2); arrow(ax, 6.7, 6.3, 7.6, 6.2); arrow(ax, 6.7, 5.8, 7.6, 2.0)
arrow(ax, 10.2, 8.7, 10.2, 7.95, color="#b91c1c", lw=1.6); arrow(ax, 10.2, 4.45, 10.2, 3.7, color="#b91c1c", lw=1.6)
ax.text(10.5, 8.33, "SHUFFLE #1", fontsize=5.8, color="#b91c1c", fontweight="bold", va="center")
ax.text(10.5, 4.08, "SHUFFLE #2", fontsize=5.8, color="#b91c1c", fontweight="bold", va="center")
box(ax, 13.6, 0.2, 8.3, 12.0, "", "#f8fafc", ec="#94a3b8")
ax.text(17.75, 11.55, "Executor local[*]: task dijadwalkan ke core", ha="center", fontsize=6.4, fontweight="bold")
cols = ["#fde68a", "#fecaca", "#bbf7d0"]
for r, lab in enumerate(["Core 1", "Core 2", "Core 3", "Core N"]):
    y = 9.3 - r*1.85
    ax.text(13.9, y+.45, lab, fontsize=6, fontweight="bold", va="center")
    for k in range(3): box(ax, 15.4 + k*2.1, y, 1.95, .95, f"S{k+1}·T{r}", cols[k], fs=6)
ax.text(17.75, 2.0, "Waktu →  Task dalam 1 stage berjalan PARALEL\n(antar core). Stage berikutnya baru mulai setelah\nSEMUA task stage sebelumnya selesai.\n1 task = 1 partition.",
        ha="center", va="center", fontsize=5.9, style="italic", linespacing=1.4)
ax.set_title("Gambar 2. Alur Spark Job → Stage → Task", fontsize=7.6, fontweight="bold", loc="left")
plt.tight_layout(pad=.3); plt.savefig("results/fig_jobstage.png", dpi=260); plt.close()
print("ok")
