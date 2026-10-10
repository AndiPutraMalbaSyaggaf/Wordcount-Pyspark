import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
r = json.load(open("results/benchmark.json")); ex = json.load(open("results/extra.json"))
P = r["partition"]; n = np.array([p["n"] for p in P]); med = np.array([p["median"] for p in P])
lo = np.array([p["min"] for p in P]); hi = np.array([p["max"] for p in P])

# model linear T = a + b*P
b, a = np.polyfit(n, med, 1)
print("fit: a=%.3f b=%.4f  (detik/partition)" % (a, b))
resid = med - (a + b*n); print("R2=%.4f" % (1 - resid.var()/med.var()))
for p in P: print(p["n"], p["real_input_partitions"], round(p["median"],2), round(p["min"],2), round(p["max"],2))
print("speed ratio 256 vs 1: %.1fx" % (med[-1]/med[0]))
print("sizes:", r["sizes"]); print("skew", {k:(v["max"], round(v["mean"]), round(v["max"]/v["mean"],2)) for k,v in r["skew"].items()})
print("empty", r["empty_after_reduce"])

plt.rcParams.update({"font.size": 6.6, "font.family": "DejaVu Sans"})
fig, axs = plt.subplots(1, 3, figsize=(7.0, 2.55))
ax = axs[0]
ax.plot(n, med, "o-", color="#2563eb", lw=2, label="median (3 run)")
ax.fill_between(n, lo, hi, color="#2563eb", alpha=.18, label="min–maks")
ax.plot(n, a + b*n, "--", color="#dc2626", lw=1, label=f"fit: {a:.2f}+{b:.3f}·P")
ax.set_xscale("log", base=2); ax.set_xticks(n); ax.set_xticklabels(n)
ax.set_xlabel("Jumlah partition (P)"); ax.set_ylabel("Waktu (detik)")
ax.set_title("(a) Waktu vs partition\n(100 rb baris, 1 core)", fontsize=6.8, fontweight="bold")
ax.legend(fontsize=5.4, loc="upper left"); ax.grid(alpha=.3)

ax = axs[1]; S = r["sizes"]; x = np.arange(len(S)); w = .36
b1 = ax.bar(x - w/2, [s["python"] for s in S], w, label="Python murni (1 mesin)", color="#f59e0b")
b2 = ax.bar(x + w/2, [s["spark"] for s in S], w, label="Spark (P=4)", color="#2563eb")
for bars in (b1, b2):
    for rct in bars: ax.text(rct.get_x()+rct.get_width()/2, rct.get_height()+.08, f"{rct.get_height():.2f}", ha="center", fontsize=5.6)
ax.set_ylim(0, 6.3); ax.set_xticks(x); ax.set_xticklabels([f"{s['lines']:,}\n({s['mb']:.1f} MB)".replace(",", ".") for s in S])
ax.set_xlabel("Ukuran data (baris)"); ax.set_ylabel("Waktu (detik)")
ax.set_title("(b) Python murni vs Spark\nmenurut ukuran data", fontsize=6.8, fontweight="bold"); ax.legend(fontsize=5.4, loc="upper left"); ax.grid(axis="y", alpha=.3)

ax = axs[2]
ns = [8, 64, 128, 256]; e = r["empty_after_reduce"]
pct = [100 * e[str(k)]["empty"] / k for k in ns]
bars = ax.bar([str(k) for k in ns], pct, color=["#16a34a", "#eab308", "#f97316", "#dc2626"])
for rct, pc, k in zip(bars, pct, ns): ax.text(rct.get_x()+rct.get_width()/2, pc+1.2, f"{e[str(k)]['empty']}/{k}", ha="center", fontsize=6)
ax.set_ylim(0, 70); ax.set_xlabel("Jumlah partition"); ax.set_ylabel("Partition kosong (%)")
ax.set_title("(c) Partition kosong setelah\nreduceByKey (148 kata unik)", fontsize=6.8, fontweight="bold"); ax.grid(axis="y", alpha=.3)
fig.suptitle("Gambar 3. Hasil eksperimen terukur", fontsize=7.6, fontweight="bold", x=0.01, ha="left")
plt.tight_layout(rect=(0, 0, 1, .95)); plt.savefig("results/fig_experiments.png", dpi=260)
json.dump({"a": a, "b": b}, open("results/fit.json", "w"))
