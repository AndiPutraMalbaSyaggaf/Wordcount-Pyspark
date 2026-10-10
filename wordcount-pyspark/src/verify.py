import re
from collections import Counter
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[*]").config("spark.ui.enabled","false").getOrCreate()
sc = spark.sparkContext; sc.setLogLevel("ERROR")
prep = lambda l: [w for w in re.sub(r"[^\w\s]", " ", l.lower()).split() if w and not w.isdigit()]
c = Counter()
for line in open("data/bigdata.txt", encoding="utf-8"): c.update(prep(line))
ref = c.most_common(10); print("python:", ref[:3], "total", sum(c.values()), "unik", len(c))
for P in [1, 8, 32]:
    r = (sc.textFile("data/bigdata.txt", P).flatMap(prep).map(lambda w:(w,1)).reduceByKey(lambda a,b:a+b, P)
           .sortBy(lambda kv: kv[1], False).take(10))
    print(P, "sama dengan Python murni:", r == ref)
spark.stop()
