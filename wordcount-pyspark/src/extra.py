import json, time, statistics, urllib.request, random
from pyspark.sql import SparkSession
spark = (SparkSession.builder.master("local[*]").config("spark.ui.showConsoleProgress","false").getOrCreate())
sc = spark.sparkContext; sc.setLogLevel("ERROR")
def sw():
    time.sleep(2)
    u = sc.uiWebUrl + "/api/v1/applications/" + sc.applicationId + "/stages?length=1000"
    return sum(s.get("shuffleWriteBytes",0) for s in json.load(urllib.request.urlopen(u)))
out = {}
for card, K in [("rendah (148 kunci)", 148), ("tinggi (200.000 kunci)", 200000)]:
    base = sc.parallelize(range(1_000_000), 8).map(lambda i, K=K: (i * 2654435761 % K, 1)).cache()
    base.count()
    for name, fn in [("reduceByKey", lambda: base.reduceByKey(lambda a,b:a+b, 8).count()),
                     ("groupByKey", lambda: base.groupByKey(8).mapValues(sum).count())]:
        fn(); b0 = sw(); ts=[]
        for _ in range(3):
            t=time.perf_counter(); fn(); ts.append(time.perf_counter()-t)
        b1 = sw()
        out[f"{card}|{name}"] = {"time": statistics.median(ts), "shuffle_mb": (b1-b0)/3/1e6}
        print(card, name, out[f"{card}|{name}"], flush=True)
    base.unpersist()
json.dump(out, open("results/extra.json","w"), indent=1)
spark.stop()
