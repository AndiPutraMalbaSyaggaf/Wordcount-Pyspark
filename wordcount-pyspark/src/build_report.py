import json, matplotlib
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
                                TableStyle, Image, PageBreak, KeepTogether, Preformatted)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

fd = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data/fonts/ttf")
for nm, fn in [("DV", "DejaVuSans.ttf"), ("DV-B", "DejaVuSans-Bold.ttf"),
               ("DV-I", "DejaVuSans-Oblique.ttf"), ("DV-BI", "DejaVuSans-BoldOblique.ttf"),
               ("DVM", "DejaVuSansMono.ttf")]:
    pdfmetrics.registerFont(TTFont(nm, os.path.join(fd, fn)))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-BI")

R = json.load(open("results/benchmark.json")); X = json.load(open("results/extra.json")); F = json.load(open("results/fit.json"))
NAVY = colors.HexColor("#1e3a8a"); LIGHT = colors.HexColor("#eff6ff"); GRID = colors.HexColor("#cbd5e1")

body = ParagraphStyle("b", fontName="DV", fontSize=9.1, leading=13.0, alignment=TA_JUSTIFY, spaceAfter=4)
h1 = ParagraphStyle("h1", fontName="DV-B", fontSize=11, leading=14, textColor=NAVY, spaceBefore=7, spaceAfter=4)
h2 = ParagraphStyle("h2", fontName="DV-B", fontSize=9.2, leading=12, textColor=colors.HexColor("#0f172a"), spaceBefore=4, spaceAfter=2)
cap = ParagraphStyle("c", fontName="DV-I", fontSize=8, leading=10.5, textColor=colors.HexColor("#475569"), spaceAfter=5)
cell = ParagraphStyle("cell", fontName="DV", fontSize=8.4, leading=11)
cellb = ParagraphStyle("cellb", parent=cell, fontName="DV-B")
cellh = ParagraphStyle("cellh", parent=cell, fontName="DV-B", textColor=colors.white)
bul = ParagraphStyle("bul", parent=body, leftIndent=11, bulletIndent=2, spaceAfter=2.5)
code = ParagraphStyle("code", fontName="DVM", fontSize=6.9, leading=9.2, textColor=colors.HexColor("#e2e8f0"))

def CodeBox(txt, st):
    t = Table([[Preformatted(txt, st)]], colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#0f172a")), ("LEFTPADDING", (0,0), (-1,-1), 7),
                           ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)]))
    return t
def P(t, s=body): return Paragraph(t, s)
def B(t): return Paragraph(t, bul, bulletText="•")
def tbl(rows, widths, header=True, zebra=True, small=False):
    cs = ParagraphStyle("cs", parent=cell, fontSize=7.3, leading=9.5) if small else cell
    ch = ParagraphStyle("ch", parent=cellh, fontSize=7.8) if small else cellh
    data = [[Paragraph(str(c), ch if (header and i == 0) else cs) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("GRID", (0, 0), (-1, -1), .4, GRID), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
          ("LEFTPADDING", (0, 0), (-1, -1), 2.5 if small else 4), ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 if small else 4)]
    if header: st.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    if zebra:
        for i in range(1, len(rows)):
            if i % 2 == 0: st.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(st)); return t
def img(path, w):
    from PIL import Image as PI
    iw, ih = PI.open(path).size
    return Image(path, width=w, height=w * ih / iw)

W = A4[0] - 3.6 * cm
def footer(c, d):
    c.saveState(); c.setFont("DV", 7.2); c.setFillColor(colors.HexColor("#64748b"))
    c.drawString(1.8 * cm, 1.0 * cm, "Tugas Individu - Analisis Pemrosesan Data Paralel | WordCount dengan PySpark")
    c.drawRightString(A4[0] - 1.8 * cm, 1.0 * cm, f"Halaman {d.page}"); c.restoreState()
doc = BaseDocTemplate("results/Laporan_WordCount_PySpark.pdf", pagesize=A4, leftMargin=1.8*cm, rightMargin=1.8*cm,
                      topMargin=1.5*cm, bottomMargin=1.6*cm, title="Laporan WordCount PySpark",
                      author="Tugas Individu - Analisis Pemrosesan Data Paralel")
doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(1.8*cm, 1.6*cm, W, A4[1]-3.1*cm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=footer)])
S = []

# ---------------------------------------------------------------- HALAMAN 1
head = Table([[Paragraph("<font color='white' size=15><b>Implementasi WordCount dengan PySpark</b></font><br/>"
                         "<font color='#bfdbfe' size=9>Pembuktian pemrosesan paralel: data masuk → partition → transformation → action → pengaruh partition terhadap performa</font>",
                         ParagraphStyle("hd", fontName="DV", leading=17))]], colWidths=[W])
head.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), NAVY), ("LEFTPADDING", (0,0), (-1,-1), 10), ("TOPPADDING", (0,0), (-1,-1), 9), ("BOTTOMPADDING", (0,0), (-1,-1), 9)]))
S += [head, Spacer(1, 4),
      P("<b>Mata kuliah:</b> Analisis Pemrosesan Data Paralel &nbsp;|&nbsp; <b>Nama:</b> ____________________ &nbsp;|&nbsp; <b>NIM:</b> ____________", ParagraphStyle("m", parent=body, alignment=0, fontSize=8)),
      P("1. Pendahuluan dan Tujuan", h1),
      P("Laporan ini bukan sekadar menjalankan program WordCount, tetapi <b>membuktikan</b> bagaimana Apache Spark memproses data secara paralel: "
        "(1) bagaimana data dibagi menjadi <i>partition</i>, (2) bagaimana <i>transformation</i> disusun menjadi DAG yang dibagi menjadi <i>stage</i> pada batas <i>shuffle</i>, "
        "(3) bagaimana <i>action</i> memicu <i>job</i> yang dijalankan sebagai <i>task</i> (satu task per partition), dan (4) bagaimana jumlah partition memengaruhi waktu eksekusi. "
        "Semua angka pada laporan ini adalah <b>hasil pengukuran nyata</b> dari kode yang disertakan (<font name='DVM'>wordcount_pyspark.py</font>, <font name='DVM'>benchmark.py</font>), "
        "bukan angka contoh."),
      P("2. Lingkungan dan Dataset", h1)]
env = [["Komponen", "Nilai", "Komponen", "Nilai"],
       ["Apache Spark", f"{R['spark']} (mode <i>local[*]</i>)", "Dataset", "bigdata.txt, 100.000 baris (8,2 MB)"],
       ["Python / Java", "3.12 / OpenJDK 21", "Total token", "1.298.900 kata (setelah preprocessing)"],
       ["CPU / RAM", f"<b>{R['cores']} core</b> / 4 GB", "Kata unik", "148 kata"]]
S += [tbl(env, [2.6*cm, 4.7*cm, 2.3*cm, W - 9.6*cm]), Spacer(1, 3),
      P("<b>Dataset.</b> Teks berbahasa Indonesia sintetis yang dibuat oleh <font name='DVM'>generate_dataset.py</font> (seed 42) dengan distribusi frekuensi kata ala Zipf "
        "(kata fungsi seperti <i>yang, dan, di</i> sangat sering, kata isi jarang), 8–18 kata per baris, diberi huruf kapital dan tanda baca agar tahap preprocessing bermakna. "
        "Ukurannya 20× lipat dari syarat minimal 5.000 baris supaya waktu eksekusi cukup besar untuk diukur. "
        "<b>Catatan keterbukaan:</b> dataset sintetis, bukan korpus nyata; hanya 148 kata unik, sehingga beberapa temuan (partition kosong, skew) dipengaruhi karakter data ini."),
      P("<b>Hasil: 10 kata terbanyak</b> (keluaran program; diverifikasi identik dengan hitungan Python murni untuk P = 1, 8, dan 32):", ParagraphStyle("x", parent=body, spaceAfter=2))]
top = [("yang", 183399), ("dan", 97727), ("di", 67919), ("untuk", 52675), ("dengan", 43042), ("dalam", 37126), ("pada", 31633), ("ini", 28150), ("itu", 25395), ("dari", 22802)]
tot = 1298900
rows1 = [["#", "Kata", "Frekuensi", "%"]] + [[i+1, w, f"{c:,}".replace(",", "."), f"{100*c/tot:.2f}".replace(".", ",")] for i, (w, c) in enumerate(top[:5])]
rows2 = [["#", "Kata", "Frekuensi", "%"]] + [[i+6, w, f"{c:,}".replace(",", "."), f"{100*c/tot:.2f}".replace(".", ",")] for i, (w, c) in enumerate(top[5:])]
two = Table([[tbl(rows1, [.8*cm, 2.2*cm, 2.4*cm, 1.6*cm]), tbl(rows2, [.8*cm, 2.2*cm, 2.4*cm, 1.6*cm])]], colWidths=[W/2, W/2])
two.setStyle(TableStyle([("LEFTPADDING", (0,0), (-1,-1), 0), ("VALIGN", (0,0), (-1,-1), "TOP")]))
S += [two, Spacer(1, 2),
      P("Kata <i>yang</i> saja menyumbang 14,1% dari seluruh token. Fakta ini penting: satu kunci yang dominan akan menjadi sumber <i>data skew</i> (Bagian 6).", body)]

# ---------------------------------------------------------------- IMPLEMENTASI
S += [P("3. Implementasi dan Penjelasan Transformation / Action", h1),
      P("Program memakai RDD API agar setiap langkah paralelnya terlihat jelas. Inti kodenya (lengkap di <font name='DVM'>wordcount_pyspark.py</font>):", body),
      CodeBox(
"""text  = sc.textFile(path, minPartitions=P).repartition(P)              # data masuk -> P partition
words = text.flatMap(lambda l: re.sub(r"[^\\w\\s]", " ", l.lower()).split())  # preprocessing
words = words.filter(lambda w: w and not w.isdigit())                    # buang token kosong/angka
pairs = words.map(lambda w: (w, 1))                                      # (kata, 1)
counts = pairs.reduceByKey(lambda a, b: a + b, numPartitions=P)          # agregasi (shuffle #2)
top10  = counts.sortBy(lambda kv: kv[1], ascending=False).take(10)       # urut + ACTION""", code), Spacer(1, 5),
      ]
ops = [["Operasi", "Jenis", "Peran dalam pipeline dan pengaruhnya pada paralelisme"],
       ["textFile(path, minPartitions=P)", "Transformation (lazy)", "Membentuk RDD dari berkas; Spark memecah berkas menjadi split sehingga tiap split menjadi satu partition. Belum ada data yang dibaca."],
       ["repartition(P)", "Wide (shuffle #1)", "Mengacak ulang data merata ke tepat P partition. Dipakai hanya agar eksperimen terkontrol, bukan bagian logika WordCount."],
       ["flatMap(preprocess)", "Narrow", "Satu baris menjadi banyak kata (lowercase, hapus tanda baca, split). Berjalan lokal di tiap partition, tanpa pindah data."],
       ["filter(...) dan map(w→(w,1))", "Narrow", "Membuang token kosong/angka dan membentuk pasangan kunci-nilai. Digabung (pipelining) dengan flatMap dalam satu stage."],
       ["reduceByKey(+, P)", "Wide (shuffle #2)", "Menjumlahkan per kata. Ada <i>combiner</i> di sisi map: tiap task menjumlahkan lokal lebih dulu sehingga hanya ≤148 pasangan per task yang dikirim."],
       ["sortBy(freq)", "Wide (shuffle #3)", "Mengurutkan global lewat <i>range partitioning</i>. Spark mengambil sampel data lebih dulu, sehingga memicu job tambahan walau tampak sebagai transformation."],
       ["take(10)", "<b>ACTION</b>", "Memicu eksekusi seluruh DAG sebagai satu job; mengembalikan 10 elemen ke driver (lebih aman daripada collect())."],
       ["mapPartitionsWithIndex+collect, count()", "Narrow / ACTION", "Diagnostik: menghitung baris per partition dan total token/kata unik."]]
S += [tbl(ops, [4.1*cm, 2.8*cm, W - 6.9*cm]), Spacer(1, 4)]
S += [img("results/fig_pipeline.png", W), P("Pipeline dibaca dari kiri ke kanan. Operasi <i>narrow</i> digabung dalam satu stage; setiap <i>wide</i> (shuffle) memotong stage baru.", cap)]

# ---------------------------------------------------------------- PARALEL: partition, job, stage, task
S += [P("4. Bagaimana Data Diproses Secara Paralel", h1),
      P("<b>a) Data masuk dan pembagian partition.</b> Dengan P = 8, hasil diagnostik menunjukkan 100.000 baris terbagi hampir rata: "
        "<font name='DVM'>{0: 12516, 1: 12490, 2: 12510, 3: 12506, 4: 12499, 5: 12489, 6: 12490, 7: 12500}</font> "
        "(selisih terbesar-terkecil hanya 27 baris atau 0,2%). Karena satu task memproses satu partition, delapan partition berarti delapan task yang <i>dapat</i> berjalan bersamaan "
        "bila tersedia delapan core. Pembagian merata ini penting: stage baru selesai saat task <b>paling lambat</b> selesai."),
      P("<b>b) Action → Job → Stage → Task.</b> Transformation hanya mencatat <i>lineage</i> (DAG); tidak ada komputasi sampai ada action. Pada <font name='DVM'>toDebugString()</font> terlihat tiga batas shuffle "
        "(repartition, reduceByKey, sortBy). Pohon eksekusi pada Gambar 2 disederhanakan tanpa <i>repartition</i>; pada program sebenarnya ada satu stage tambahan di depan.", body),
      img("results/fig_jobstage.png", W), P("Task dalam satu stage berjalan paralel; antar-stage ada <i>barrier</i> karena stage berikutnya membutuhkan seluruh keluaran shuffle stage sebelumnya.", cap)]
jt = [["Kelompok (Job)", "Stage → jumlah task (hasil statusTracker)", "Penjelasan"],
      ["A. Diagnostik (Job 0)", "Stage 0, 1: masing-masing 8 task, dijalankan", "Action collect() pertama: membaca data + repartition; memaksa pembagian partition terjadi."],
      ["B. Sampling sortBy (Job 1, 2)", "Stage 2–7: 8 task per stage; sebagian dijalankan, sebagian <i>skipped</i>", "RangePartitioner menarik sampel kunci untuk menentukan batas rentang. Ini biaya tersembunyi dari sortBy."],
      ["C. Action take(10) (Job 3)", "Stage 8, 9: 8 task, <b>skipped</b>; Stage 10: 8 task; Stage 11: <b>1 task</b>", "Shuffle yang sudah ada dipakai ulang (skipped). Stage hasil hanya 1 task: take() memindai partition satu per satu dan 10 kata teratas sudah ada di partition pertama hasil sort menurun."]]
S += [tbl(jt, [3.2*cm, 5.6*cm, W - 8.8*cm]),
      P("Bukti ini menjawab pertanyaan inti: jumlah task per stage sama dengan jumlah partition (8), job dibuat per action, dan Spark menghindari kerja ulang dengan memakai kembali berkas shuffle (<i>stage skipped</i>).", ParagraphStyle("z", parent=body, spaceBefore=3))]

# ---------------------------------------------------------------- EKSPERIMEN PARTITION
S += [P("5. Analisis Pengaruh Jumlah Partition terhadap Performa", h1),
      P("Metode: pipeline lengkap (baca → preprocessing → reduceByKey → sortBy → take) dijalankan pada dataset 100.000 baris untuk P = 1…256, setelah <i>warm-up</i> JVM, dengan 3 kali pengulangan per konfigurasi (median dan rentang dilaporkan). "
        "Waktu di sini mencakup job sampling sortBy, sehingga lebih besar dari waktu action tunggal pada Bagian 4.")]
pr = [["Partition (P)", *[str(p["n"]) for p in R["partition"]]],
      ["Median (s)", *[f"{p['median']:.2f}".replace(".", ",") for p in R["partition"]]],
      ["Min–maks (s)", *[f"{p['min']:.1f}–{p['max']:.1f}".replace(".", ",") for p in R["partition"]]],
      ["Relatif thd P=1", *[f"{p['median']/R['partition'][0]['median']:.1f}×".replace(".", ",") for p in R["partition"]]]]
S += [tbl(pr, [2.5*cm] + [(W - 2.5*cm)/9]*9, small=True), Spacer(1, 4), img("results/fig_experiments.png", W)]
a, b = F["a"], F["b"]
S += [P("Gambar 3a: waktu naik monoton seiring bertambahnya partition; P = 256 kira-kira 42 kali lebih lambat daripada P = 1. Gambar 3b dibahas pada Bagian 6.", cap),
      P("<b>Interpretasi.</b> Hasil ini <b>berbeda dari tabel contoh di lembar tugas</b> (yang menurun sampai P = 8 lalu naik) dan perbedaannya bisa dijelaskan: mesin uji hanya memiliki "
        f"<b>{R['cores']} core</b>. Menambah partition hanya berguna bila ada core yang benar-benar menganggur untuk menjalankan task secara bersamaan. Dengan 1 core, "
        "semua task tetap berjalan bergiliran (indikator progres Spark selama eksperimen menampilkan pola ‘7 selesai + 1 berjalan’ dari 8 task, yaitu hanya satu task aktif pada satu waktu), sehingga yang tersisa hanya biaya tambahannya. Regresi linear terhadap data menghasilkan "
        f"T(P) ≈ {a:.2f} + {b:.3f}·P detik (R² = 0,98): setiap partition tambahan menambah sekitar {b:.2f} detik pada pipeline ini. Penyebab yang masuk akal dan konsisten dengan data:"),
      B("<b>Overhead per task:</b> penjadwalan, serialisasi <i>closure</i>, pembuatan berkas shuffle, dan komunikasi JVM–Python dibayar untuk setiap task di setiap stage."),
      B("<b>Jumlah blok shuffle M×R:</b> setiap reducer mengambil blok dari setiap mapper, sehingga ada M×R blok (P = 256 berarti 65.536 blok per shuffle). Namun kenaikan waktu per partition pada data ini relatif stabil (sekitar 0,16–0,32 detik), bukan kuadrat, sehingga kontribusi faktor ini tidak dapat saya pastikan."),
      B("<b>Partition kosong:</b> hanya ada 148 kata unik, sehingga pada P = 256 sebanyak 143 partition (56%) kosong setelah reduceByKey: task dijalankan tanpa pekerjaan berguna (Gambar 3c)."),
      P("Saya tidak mengisolasi kontribusi masing-masing faktor secara terpisah; ketiganya adalah penjelasan yang mungkin, bukan hasil pemisahan eksperimen. "
        "<b>Implikasi pada cluster nyata:</b> secara konseptual T(P) ≈ W / min(P, C) + c·P dengan C = jumlah core total, sehingga kurva berbentuk lembah dengan titik optimum di sekitar P ≈ C sampai beberapa kali C "
        "(panduan <i>Tuning</i> Spark menyarankan 2–3 task per core). Bagian turun pada kurva tersebut <b>tidak dapat saya buktikan pada mesin 1-core ini</b>; yang terbukti adalah bagian naiknya (biaya kelebihan partition).")]

# ---------------------------------------------------------------- SINGLE VS DISTRIBUTED + BOTTLENECK
Sz = R["sizes"]
fm = lambda v, d=2: f"{v:.{d}f}".replace(".", ",")
S += [P("6. Single Machine vs Distributed dan Identifikasi Bottleneck", h1),
      P("<b>Pengukuran (Gambar 3b).</b> Pembanding single machine adalah program Python murni (<font name='DVM'>collections.Counter</font>) pada data dan preprocessing yang sama. "
        f"Pada 5.000 baris Python selesai dalam {fm(Sz[0]['python'])} detik dan Spark {fm(Sz[0]['spark'])} detik (≈{Sz[0]['spark']/Sz[0]['python']:.0f}× lebih lambat); "
        f"pada 100.000 baris {fm(Sz[1]['python'])} s vs {fm(Sz[1]['spark'])} s (≈{fm(Sz[1]['spark']/Sz[1]['python'],1)}×); pada 500.000 baris {fm(Sz[2]['python'])} s vs {fm(Sz[2]['spark'])} s (≈{fm(Sz[2]['spark']/Sz[2]['python'],1)}×). "
        "Jadi pada data kecil, Spark <b>kalah</b> karena biaya tetap (JVM, penjadwalan job, serialisasi) tidak sebanding dengan pekerjaannya; selisih rasio menyempit seiring data membesar karena biaya tetap itu "
        "teramortisasi. Titik impas tidak tercapai pada rentang yang diuji (≤ 41 MB, 1 core); saya tidak mengekstrapolasi di luar rentang itu.")]
cmpT = [["Aspek", "Single machine (diukur / konsep)", "Distributed Spark (diukur / konsep)"],
        ["Data yang diproses", "Dibatasi RAM dan disk satu mesin.", "Dibagi ke banyak node; ukuran data bisa melebihi RAM satu mesin (konsep)."],
        ["Waktu eksekusi", "<b>Lebih cepat pada data kecil</b> (diukur: 0,03 s vs 0,90 s pada 5.000 baris).", "Lebih cepat bila data besar <i>dan</i> core banyak (konsep); pada mesin ini belum terbukti."],
        ["Skalabilitas", "Vertikal (menambah spek mesin), ada batas fisik.", "Horizontal (menambah node)."],
        ["Ketahanan gagal", "Mesin mati = pekerjaan hilang.", "Task gagal dijadwal ulang; lineage RDD memungkinkan komputasi ulang partition hilang."],
        ["Biaya dan kompleksitas", "Murah dan sederhana.", "Overhead koordinasi, shuffle, konfigurasi cluster (terukur: ≈0,23 s per partition)."]]
S += [Spacer(1, 3), tbl(cmpT, [2.9*cm, (W-2.9*cm)/2, (W-2.9*cm)/2]), Spacer(1, 5),
      P("<b>Bottleneck yang teridentifikasi pada pipeline ini</b>", h2)]
sk = R["skew"]
lo_r, lo_g = X["rendah (148 kunci)|reduceByKey"], X["rendah (148 kunci)|groupByKey"]
hi_r, hi_g = X["tinggi (200.000 kunci)|reduceByKey"], X["tinggi (200.000 kunci)|groupByKey"]
fm = lambda v, d=2: f"{v:.{d}f}".replace(".", ",")
S += [B("<b>Shuffle (reduceByKey dan sortBy).</b> Memindahkan data antar-executor lewat disk/jaringan dan menjadi batas stage. Combiner menekan volumenya: shuffle write reduceByKey hanya "
        f"{fm(R['shuffle_cmp']['reduceByKey']['shuffle_write_mb'],3)} MB karena tiap task mengirim ≤148 pasangan, bukan sekitar 162 ribu token per task."),
      B("<b>Data skew.</b> Jika pasangan dikirim tanpa agregasi lokal, reducer yang menerima kata <i>yang</i> menanggung beban jauh lebih besar. Terukur: pada P = 8 reducer terbesar menerima "
        f"{sk['8']['max']:,} record vs rata-rata {round(sk['8']['mean']):,} ({fm(sk['8']['max']/sk['8']['mean'])}×); pada P = 32 reducer terbesar {sk['32']['max']:,} vs {round(sk['32']['mean']):,} ({fm(sk['32']['max']/sk['32']['mean'])}×). ".replace(",", ".") +
        "Menambah partition justru memperlebar rasio skew karena satu kunci tidak dapat dipecah; satu task menjadi penentu waktu stage."),
      B("<b>Overhead penjadwalan dan partition kosong</b> pada P berlebihan (Bagian 5): bottleneck dominan pada eksperimen ini."),
      B("<b>Biaya tersembunyi sortBy</b> (job sampling tambahan, Bagian 4) dan <b>serialisasi Python–JVM</b> pada PySpark: setiap lambda dipanggil per record di proses Python."),
      B(f"<b>reduceByKey vs groupByKey: hasilnya bergantung pada kardinalitas kunci.</b> Pada 148 kunci, reduceByKey mengirim shuffle lebih sedikit ({fm(lo_r['shuffle_mb'],3)} vs {fm(lo_g['shuffle_mb'],3)} MB) tetapi <b>lebih lambat</b> "
        f"({fm(lo_r['time'])} s vs {fm(lo_g['time'])} s); dugaan saya, karena lambda Python dipanggil per record sedangkan groupByKey memakai operasi bawaan. Pada 200.000 kunci (1 juta record), reduceByKey "
        f"<b>lebih cepat</b> ({fm(hi_r['time'])} s vs {fm(hi_g['time'])} s, ≈{100*(1-hi_r['time']/hi_g['time']):.0f}%), dengan volume shuffle hampir sama ({fm(hi_r['shuffle_mb'])} vs {fm(hi_g['shuffle_mb'])} MB). "
        "Jadi keunggulan reduceByKey yang lazim diajarkan tidak otomatis berlaku pada skala kecil di PySpark; penyebab pastinya belum saya verifikasi.")]

# ---------------------------------------------------------------- KESIMPULAN
S += [P("7. Kesimpulan", h1),
      B("<b>Alur paralel terbukti:</b> data terbagi menjadi 8 partition yang seimbang (selisih 0,2%); transformation bersifat lazy; action take(10) memicu job; shuffle membagi job menjadi stage; "
        "jumlah task per stage sama dengan jumlah partition; stage yang keluarannya sudah ada dilewati (skipped)."),
      B("<b>Jumlah partition bukan 'makin banyak makin cepat'.</b> Pada mesin 1-core, P = 1 tercepat (1,36 s) dan P = 256 terlambat (56,95 s, 42×). Partition hanya menguntungkan jika ada core untuk menjalankannya bersamaan; "
        "di luar itu yang dibayar hanyalah overhead (≈0,23 s per partition; kemungkinan berasal dari overhead task, blok shuffle M×R, dan partition kosong)."),
      B("<b>Spark tidak selalu lebih baik daripada single machine.</b> Pada data ≤ 41 MB di satu mesin, Python murni 3–32× lebih cepat. Spark layak dipilih ketika data atau komputasi melampaui satu mesin, atau saat butuh toleransi kegagalan."),
      B("<b>Bottleneck utama</b> pipeline ini: overhead penjadwalan akibat partition berlebih, shuffle, dan data skew pada kata dominan; secara konseptual dapat dikurangi dengan memilih P ≈ 2–3× jumlah core (panduan Tuning Spark), memakai agregasi lokal, dan menghindari partition kosong; efek perbaikan ini belum diuji pada cluster multi-core."),
      P("<b>Keterbatasan.</b> Satu mesin 1-core dengan mode local (bukan cluster sungguhan); dataset sintetis dengan 148 kata unik; 3 pengulangan per konfigurasi. Nilai absolut tidak dapat digeneralisasi; "
        "arah tren (biaya overhead, skew, partition kosong) adalah temuan yang kuat. Pengujian di cluster multi-core adalah langkah lanjutan yang paling bernilai.", ParagraphStyle("k", parent=body, spaceBefore=3)),
      P("Referensi", h1)]
refs = ["Zaharia, M., Chowdhury, M., Das, T., Dave, A., Ma, J., McCauley, M., Franklin, M. J., Shenker, S., &amp; Stoica, I. (2012). Resilient Distributed Datasets: A fault-tolerant abstraction for in-memory cluster computing. <i>Proc. 9th USENIX NSDI</i>, 15–28.",
        "Dean, J., &amp; Ghemawat, S. (2004). MapReduce: Simplified data processing on large clusters. <i>Proc. 6th USENIX OSDI</i>, 137–150.",
        "Damji, J. S., Wenig, B., Das, T., &amp; Lee, D. (2020). <i>Learning Spark: Lightning-Fast Data Analytics</i> (2nd ed.). O'Reilly Media.",
        "Chambers, B., &amp; Zaharia, M. (2018). <i>Spark: The Definitive Guide</i>. O'Reilly Media.",
        "Apache Software Foundation. <i>RDD Programming Guide</i> dan <i>Tuning Spark</i>. https://spark.apache.org/docs/latest/ (diakses Oktober 2026)."]
S += [Paragraph(f"[{i+1}] {r}", ParagraphStyle("r", parent=body, fontSize=7.6, leading=10.4, leftIndent=14, firstLineIndent=-14, spaceAfter=1.5, alignment=0)) for i, r in enumerate(refs)]
doc.build(S)
print("built")
