# Implementasi WordCount dengan PySpark: Analisis Pemrosesan Data Paralel

Tugas Individu, mata kuliah Analisis Pemrosesan Data Paralel.
Program WordCount (RDD API) disertai bukti alur paralel Spark (partition → transformation → action →
Job/Stage/Task) dan analisis pengaruh jumlah partition terhadap performa.

**Laporan lengkap (PDF, 5 halaman):** [`report/Laporan_WordCount_PySpark.pdf`](report/Laporan_WordCount_PySpark.pdf)

## Struktur
```
src/
  generate_dataset.py   # membuat data/bigdata.txt (100.000 baris, sintetis, seed 42)
  wordcount_pyspark.py  # program utama: WordCount + diagnostik partition, lineage, Job/Stage/Task
  benchmark.py          # eksperimen: P=1..256, Python murni vs Spark, skew, partition kosong
  extra.py              # reduceByKey vs groupByKey (kardinalitas kunci rendah vs tinggi)
  verify.py             # memastikan hasil Spark == Python murni
  diagrams.py, charts.py, build_report.py   # membuat gambar & laporan PDF
results/                # hasil ukur (JSON), gambar, keluaran program
report/                 # laporan PDF
data/                   # dataset (dibuat oleh generate_dataset.py, tidak di-commit)
```

## Cara menjalankan
Prasyarat: Python 3.10+, Java 17+ (`java -version`). Jalankan dari root repositori.
```bash
pip install -r requirements.txt
python src/generate_dataset.py 100000                # buat dataset
python src/wordcount_pyspark.py data/bigdata.txt 8   # argumen: path, jumlah partition
python src/verify.py                                 # validasi hasil vs Python murni
python src/benchmark.py                              # eksperimen (beberapa menit)
python src/extra.py
python src/diagrams.py && python src/charts.py && python src/build_report.py
```

## Hasil ringkas (mesin uji: 1 core, Spark 4.2.0, mode local)
| Temuan | Nilai terukur |
|---|---|
| Partition P=8 | 100.000 baris terbagi merata (selisih 0,2%) |
| Kata teratas | `yang` = 183.399 (14,1% dari 1.298.900 token) |
| P=1 vs P=256 | 1,36 s vs 56,95 s (≈ 0,23 s per partition tambahan) |
| Python murni vs Spark | Python 3–32× lebih cepat pada data ≤ 41 MB |
| Data skew (tanpa combiner) | reducer terbesar 1,7× (P=8) dan 5,2× (P=32) dari rata-rata |

## Keterbatasan
- Mesin uji hanya 1 core, sehingga manfaat paralelisme (kurva turun lalu naik) tidak teramati; hanya biaya kelebihan partition yang terbukti. Jalankan `benchmark.py` di mesin multi-core untuk melihat efek sebenarnya.
- Dataset sintetis (distribusi Zipf, 148 kata unik); mode local, bukan cluster; 3 pengulangan per konfigurasi.
