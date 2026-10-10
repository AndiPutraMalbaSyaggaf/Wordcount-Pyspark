# Implementasi WordCount dengan PySpark

**Tugas Individu: Analisis Pemrosesan Data Paralel**

| | |
|---|---|
| Nama | Andi Putra Malba Syaggaf |
| NIM | 312410370 |
| Mata kuliah | BIG DATA |
| Dosen | Hemdani Rahendra Herlianto, S.Kom., M.T.I. |

## Deskripsi

Repositori ini berisi implementasi WordCount menggunakan Apache Spark (PySpark, RDD API).
Tujuannya bukan hanya menghitung frekuensi kata, tetapi **membuktikan bagaimana Spark memproses
data secara paralel**: data masuk, dibagi menjadi partition, diproses melalui transformation,
dijalankan melalui action, lalu dianalisis pengaruh jumlah partition terhadap performa.

Laporan lengkap (5 halaman) tersedia di
[`report/Laporan_WordCount_PySpark.pdf`](report/Laporan_WordCount_PySpark.pdf).

## Yang Dikerjakan

1. **Implementasi WordCount** dengan pipeline `textFile → flatMap → filter → map → reduceByKey → sortBy → take(10)`.
2. **Diagram** pipeline pemrosesan data dan alur Spark Job → Stage → Task.
3. **Bukti eksekusi paralel**: distribusi baris per partition, lineage RDD (`toDebugString`),
   serta jumlah stage dan task per job yang diambil langsung dari Spark.
4. **Eksperimen performa** pada 100.000 baris teks:
   - pengaruh jumlah partition (P = 1 sampai 256),
   - perbandingan single machine (Python murni) vs Spark,
   - identifikasi bottleneck: shuffle, data skew, partition kosong, overhead penjadwalan task.

## Dataset

Dataset dibuat oleh `src/generate_dataset.py`: teks berbahasa Indonesia sintetis,
100.000 baris (8,2 MB), dengan distribusi frekuensi kata ala Zipf dan seed tetap (42)
sehingga hasilnya dapat direproduksi. Dataset tidak di-commit; buat ulang dengan perintah di bawah.

> Dataset ini sintetis dan hanya memiliki 148 kata unik, sehingga beberapa temuan
> (misalnya partition kosong) dipengaruhi karakter data tersebut.

## Struktur Repositori

```
src/
  generate_dataset.py    pembuat dataset
  wordcount_pyspark.py   program utama WordCount + diagnostik
  benchmark.py           eksperimen partition, single machine vs Spark, skew
  extra.py               perbandingan reduceByKey vs groupByKey
  verify.py              validasi hasil Spark terhadap Python murni
  diagrams.py, charts.py, build_report.py   pembuat gambar dan laporan
results/                 hasil pengukuran (JSON), gambar, keluaran program
report/                  laporan PDF
data/                    lokasi dataset hasil generate
```

## Cara Menjalankan

Prasyarat: Python 3.10+ dan Java 17+. Jalankan semua perintah dari root repositori.

```bash
pip install -r requirements.txt

# 1. Buat dataset
python src/generate_dataset.py 100000

# 2. Jalankan WordCount (argumen: path data, jumlah partition)
python src/wordcount_pyspark.py data/bigdata.txt 8

# 3. (Opsional) Validasi dan eksperimen
python src/verify.py
python src/benchmark.py     # memakan waktu beberapa menit
python src/extra.py
```

Keluaran program mencakup 10 kata terbanyak, jumlah baris per partition, lineage RDD,
serta rincian Job, Stage, dan Task.

## Hasil Utama

Diukur pada mesin 1 core, Spark 4.2.0 mode local.

- **Top 10 kata** diawali *yang* (183.399), *dan* (97.727), *di* (67.919).
  Hasilnya identik dengan perhitungan Python murni (diverifikasi untuk P = 1, 8, 32).
- **Partition**: dengan P = 8, 100.000 baris terbagi merata (selisih terbesar-terkecil 0,2%).
  Jumlah task per stage sama dengan jumlah partition.
- **Pengaruh jumlah partition**: waktu naik dari 1,36 detik (P = 1) menjadi 56,95 detik (P = 256),
  sekitar 0,23 detik per partition tambahan, karena mesin uji hanya punya 1 core
  sehingga partition tambahan tidak bisa berjalan bersamaan.
- **Single machine vs Spark**: pada data sampai 41 MB di satu mesin, Python murni 3 sampai 32 kali
  lebih cepat. Biaya tetap Spark (JVM, penjadwalan, serialisasi) tidak sebanding pada data kecil.
- **Data skew**: tanpa agregasi lokal, reducer terbesar menerima 1,7 kali rata-rata (P = 8)
  dan 5,2 kali rata-rata (P = 32) karena kata *yang* mencakup 14,1% seluruh token.

## Keterbatasan

- Mesin uji hanya memiliki **1 core**, sehingga manfaat paralelisme (waktu turun lalu naik
  saat partition ditambah) tidak teramati. Yang terbukti adalah biaya kelebihan partition.
  Menjalankan `benchmark.py` pada mesin multi-core akan menunjukkan efek paralelisme sebenarnya.
- Dataset sintetis, mode local (bukan cluster sungguhan), dan 3 pengulangan per konfigurasi.
  Nilai absolut tidak dapat digeneralisasi; arah tren adalah temuan yang lebih kuat.

## Referensi

- Zaharia et al. (2012). *Resilient Distributed Datasets.* USENIX NSDI.
- Dean & Ghemawat (2004). *MapReduce: Simplified Data Processing on Large Clusters.* USENIX OSDI.
- Apache Spark Documentation: RDD Programming Guide dan Tuning Spark, https://spark.apache.org/docs/latest/
