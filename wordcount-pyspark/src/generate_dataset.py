"""Membuat dataset teks sintetis berbahasa Indonesia (distribusi kata ala Zipf).
Output: data/bigdata.txt  (satu kalimat/baris)
Pemakaian: python generate_dataset.py [jumlah_baris]
"""
import random, sys

N = int(sys.argv[1]) if len(sys.argv) > 1 else 100_000
random.seed(42)

# Kata fungsi (sering muncul) -> bobot tinggi, kata isi -> bobot rendah
fungsi = ["yang","dan","di","untuk","dengan","dalam","pada","ini","itu","dari",
          "adalah","akan","juga","ke","tidak","oleh","sebagai","dapat","atau","karena"]
isi = """data spark cluster node partition transformation action shuffle stage task job
executor driver memori disk jaringan proses paralel terdistribusi komputasi analisis
kata frekuensi teks baris berkas sistem aplikasi pengguna layanan server basis informasi
algoritma model pembelajaran mesin kecerdasan buatan penyimpanan kecepatan kinerja
efisiensi skalabilitas toleransi kegagalan replikasi pembagian beban kerja pekerja
hasil laporan evaluasi pengujian eksperimen perbandingan mesin tunggal tabel kolom
indeks kunci nilai pasangan peta reduksi gabung urutkan saring ambil kumpulkan
pemrosesan mahadata sumber daya penjadwalan antrean tugas sinkronisasi latensi
throughput bottleneck jaringan serialisasi kompresi cache lokalitas blok hadoop
pendidikan mahasiswa kampus dosen kuliah tugas praktikum jurnal penelitian metode
bisnis ekonomi pasar transaksi pelanggan produk penjualan kesehatan rumah sakit
transportasi kota jalan kendaraan energi lingkungan cuaca iklim pertanian panen
teknologi digital internet seluler pesan media sosial berita video musik film""".split()

kata = fungsi + isi
# bobot Zipf: w_i = 1/(i+1)^0.9 ; fungsi di depan -> paling sering
w = [1.0 / (i + 1) ** 0.9 for i in range(len(kata))]

import os; os.makedirs("data", exist_ok=True)
with open("data/bigdata.txt", "w", encoding="utf-8") as f:
    for _ in range(N):
        n = random.randint(8, 18)
        kal = random.choices(kata, weights=w, k=n)
        s = " ".join(kal)
        # variasi: huruf kapital & tanda baca agar preprocessing bermakna
        s = s.capitalize() + random.choice([".", ".", "!", "?", ","])
        f.write(s + "\n")
print(f"Dataset dibuat: {N} baris")
