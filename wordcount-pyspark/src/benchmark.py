"""Eksperimen performa: partition, single-machine vs Spark, shuffle, skew.
Output: results/benchmark.json
"""
import json, re, time, statistics, os, urllib.request, subprocess, sys
from collections import Counter
from pyspark.sql import SparkSession

DATA = "data/bigdata.txt"
spark = (SparkSession.builder.appName("benchmark").master("local[*]")
         .config("spark.ui.showConsoleProgress", "false").getOrCreate())
sc = spark.sparkContext; sc.setLogLevel("ERROR")
CORES = os.cpu_count()
res = {"cores": CORES, "spark": spark.version}

def prep(line): return re.sub(r"[^\w\s]", " ", line.lower()).split()

def wc_spark(path, n):
    rdd = sc.textFile(path, minPartitions=n)
    real = rdd.getNumPartitions()
    out = (rdd.flatMap(prep).map(lambda w: (w, 1))
              .reduceByKey(lambda a, b: a + b, numPartitions=n)
              .sortBy(lambda kv: kv[1], ascending=False, numPartitions=n).take(10))
    return real, out

def timeit(fn, rep=3):
    ts = []
    for _ in range(rep):
        t = time.perf_counter(); fn(); ts.append(time.perf_counter() - t)
    return ts

# ---------- warm-up JVM (agar run pertama tidak dihukum)
wc_spark(DATA, 4); wc_spark(DATA, 4)

# ---------- 1. Pengaruh jumlah partition
part = []
for n in [1, 2, 4, 8, 16, 32, 64, 128, 256]:
    ts = timeit(lambda: wc_spark(DATA, n))
    real, _ = wc_spark(DATA, n)
    part.append({"n": n, "real_input_partitions": real, "median": statistics.median(ts),
                 "min": min(ts), "max": max(ts), "runs": ts})
    print("partisi", n, "median %.2f" % statistics.median(ts), flush=True)
res["partition"] = part

# ---------- 2. Single machine (Python murni) vs Spark, beda ukuran data
sizes = []
for N in [5000, 100000, 500000]:
    p = f"data/bench_{N}.txt"
    subprocess.run([sys.executable, "-c",
        f"import sys; sys.argv=['x','{N}']; exec(open('src/generate_dataset.py').read().replace('data/bigdata.txt','{p}'))"],
        capture_output=True)
    def py():
        c = Counter()
        with open(p, encoding="utf-8") as f:
            for line in f: c.update(prep(line))
        return c.most_common(10)
    t_py = timeit(py, 3)
    wc_spark(p, 4)  # warm
    t_sp = timeit(lambda: wc_spark(p, 4), 3)
    mb = os.path.getsize(p) / 1e6
    sizes.append({"lines": N, "mb": mb, "python": statistics.median(t_py), "spark": statistics.median(t_sp)})
    print("ukuran", N, sizes[-1], flush=True)
res["sizes"] = sizes

# ---------- 3. reduceByKey vs groupByKey: waktu + volume shuffle (REST API Spark UI)
def shuffle_totals():
    time.sleep(1.5)
    base = sc.uiWebUrl + "/api/v1/applications/" + sc.applicationId + "/stages"
    st = json.load(urllib.request.urlopen(base))
    return (sum(s.get("shuffleWriteBytes", 0) for s in st), sum(s.get("shuffleWriteRecords", 0) for s in st))

pairs = lambda: sc.textFile(DATA, minPartitions=8).flatMap(prep).map(lambda w: (w, 1))
cmp = {}
for name, fn in [("reduceByKey", lambda: pairs().reduceByKey(lambda a, b: a + b, 8).collect()),
                 ("groupByKey",  lambda: pairs().groupByKey(8).mapValues(sum).collect())]:
    fn()  # warm
    b0 = shuffle_totals()
    t = timeit(fn, 3)
    b1 = shuffle_totals()
    cmp[name] = {"time": statistics.median(t), "shuffle_write_mb": (b1[0] - b0[0]) / 3 / 1e6,
                 "shuffle_records": (b1[1] - b0[1]) // 3}
    print(name, cmp[name], flush=True)
res["shuffle_cmp"] = cmp

# ---------- 4. Data skew: record yang diterima tiap reducer TANPA combiner (groupByKey)
skew = {}
for n in [8, 32]:
    sizes_ = (pairs().partitionBy(n).mapPartitionsWithIndex(lambda i, it: [(i, sum(1 for _ in it))]).collect())
    v = [c for _, c in sorted(sizes_)]
    skew[n] = {"records": v, "max": max(v), "mean": sum(v) / len(v), "empty": sum(1 for x in v if x == 0)}
    print("skew", n, skew[n]["max"], round(skew[n]["mean"]), skew[n]["empty"], flush=True)
# partisi kosong setelah reduceByKey (hanya 148 kata unik)
empty = {}
for n in [8, 64, 128, 256]:
    sz = pairs().reduceByKey(lambda a, b: a + b, n).glom().map(len).collect()
    empty[n] = {"empty": sum(1 for x in sz if x == 0), "total": n}
res["skew"] = skew; res["empty_after_reduce"] = empty
print(empty)

json.dump(res, open("results/benchmark.json", "w"), indent=1)
spark.stop()
