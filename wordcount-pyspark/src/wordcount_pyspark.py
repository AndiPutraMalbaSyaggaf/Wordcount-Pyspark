"""
Tugas Individu - Analisis Pemrosesan Data Paralel
Implementasi WordCount dengan PySpark (RDD API) + bukti eksekusi paralel.

Alur:  textFile -> flatMap -> map -> reduceByKey -> sortBy -> take
       [narrow]   [narrow]  [narrow]  [WIDE/shuffle]  [WIDE/shuffle]  [ACTION]

Pemakaian:
    python wordcount_pyspark.py [path_data] [num_partitions]
"""
import re, sys, time
from pyspark.sql import SparkSession

path = sys.argv[1] if len(sys.argv) > 1 else "data/bigdata.txt"
NUM_PART = int(sys.argv[2]) if len(sys.argv) > 2 else 8

# ---------------------------------------------------------------- 1. Inisialisasi
spark = (SparkSession.builder
         .appName("WordCount-Analisis-Partition")
         .master("local[*]")                       # semua core mesin ini = "executor" lokal
         .config("spark.sql.shuffle.partitions", NUM_PART)
         .config("spark.default.parallelism", NUM_PART)
         .config("spark.ui.showConsoleProgress", "false")
         .getOrCreate())
sc = spark.sparkContext
sc.setLogLevel("ERROR")
print(f"Spark {spark.version} | master={sc.master} | defaultParallelism={sc.defaultParallelism}")

# ---------------------------------------------------------------- 2. Data masuk
# textFile(minPartitions) -> Spark membagi file menjadi >= NUM_PART split (blok)
text = sc.textFile(path, minPartitions=NUM_PART)
# repartition menjamin jumlah partition TEPAT NUM_PART (untuk eksperimen terkontrol)
text = text.repartition(NUM_PART)
print(f"Jumlah partition awal : {text.getNumPartitions()}")

# Distribusi baris per partition (membuktikan data benar-benar terbagi)
sc.setJobGroup("A_diagnosa", "Hitung baris per partition")
dist = (text.mapPartitionsWithIndex(lambda i, it: [(i, sum(1 for _ in it))])
            .collect())                                          # ACTION (hanya utk diagnosa)
print("Baris per partition   :", dict(dist))

# ---------------------------------------------------------------- 3. Transformation (LAZY)
# 3a. Preprocessing: lowercase + hapus tanda baca + split  -> NARROW (flatMap)
words = text.flatMap(lambda line: re.sub(r"[^\w\s]", " ", line.lower()).split())
# 3b. Filter token kosong / angka murni                     -> NARROW (filter)
words = words.filter(lambda w: w and not w.isdigit())
# 3c. Bentuk pasangan (kata, 1)                              -> NARROW (map)
pairs = words.map(lambda w: (w, 1))
# 3d. Agregasi per kata. Ada combiner di sisi map            -> WIDE (shuffle)
word_counts = pairs.reduceByKey(lambda a, b: a + b, numPartitions=NUM_PART)
# 3e. Urutkan menurun berdasarkan frekuensi                  -> WIDE (shuffle, range partition)
# CATATAN: sortBy membuat RangePartitioner yang MENGAMBIL SAMPEL data -> memicu job kecil
#          saat baris ini dieksekusi (tidak 100% lazy). Kita beri label grup tersendiri.
sc.setJobGroup("B_sortBy_sampling", "Sampling RangePartitioner untuk sortBy")
sorted_counts = word_counts.sortBy(lambda kv: kv[1], ascending=False)

print("\n--- Lineage (DAG) RDD ---")
print(sorted_counts.toDebugString().decode())   # garis batas indentasi = batas Stage (shuffle)

# ---------------------------------------------------------------- 4. Action (TRIGGER eksekusi)
sc.setJobGroup("C_take10", "Action take(10): job utama WordCount")
t0 = time.perf_counter()
top10 = sorted_counts.take(10)                  # ACTION -> Spark Job dibuat & dijalankan
elapsed = time.perf_counter() - t0

print("\n=== 10 KATA TERBANYAK ===")
for rank, (w, c) in enumerate(top10, 1):
    print(f"{rank:>2}. {w:<12} {c:>8}")
print(f"\nWaktu eksekusi action : {elapsed:.2f} detik")

# ---------------------------------------------------------------- 5. Bukti Job -> Stage -> Task
tr = sc.statusTracker()
for grp in ["A_diagnosa", "B_sortBy_sampling", "C_take10"]:
    for jid in tr.getJobIdsForGroup(grp):
        j = tr.getJobInfo(jid)
        print(f"[{grp}] Job {jid}: status={j.status}")
        for sid in j.stageIds:
            st = tr.getStageInfo(sid)
            tag = "SKIPPED (shuffle dipakai ulang)" if st.numCompletedTasks == 0 else "dijalankan"
            print(f"     Stage {sid}: {st.numTasks} task, selesai={st.numCompletedTasks}  -> {tag}")

print(f"\nTotal token : {words.count()}")          # ACTION tambahan
print(f"Kata unik   : {word_counts.count()}")      # ACTION tambahan

spark.stop()
