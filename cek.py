import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---- Fungsi bantu ----
def normalize_url(domain):
    domain = domain.strip()
    if not domain:
        return None
    if not domain.startswith("http://") and not domain.startswith("https://"):
        domain = "http://" + domain
    return domain

def load_domains(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return [normalize_url(line) for line in f if normalize_url(line)]

# ---- Fungsi cek domain ----
def check_domain(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/141.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            print(f"🟢 {url} → Aktif (Status {response.status_code})")
            return None  # aktif
        else:
            print(f"🟡 {url} → Respon {response.status_code} (Dianggap mati)")
            return url
    except requests.exceptions.RequestException:
        print(f"🔴 {url} → Tidak aktif / gagal diakses")
        return url

# ---- Simpan hasil ----
def save_results(mati, filename="hasil.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("=== DOMAIN CAN TAKEOVER ===\n")
        for url in mati:
            f.write(f"{url}\n")
    print(f"\n✅ Selesai! {len(mati)} TAKEOVER mati tersimpan di '{filename}'")

# ---- Main Program ----
if __name__ == "__main__":
    try:
        domains = load_domains("list.txt")
        mati = []

        print(f"🚀 Mengecek {len(domains)} domain...\n")

        # ubah jumlah threads sesuai kebutuhan (default 20)
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(check_domain, url): url for url in domains}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    mati.append(result)

        save_results(mati)

    except FileNotFoundError:
        print("❌ File 'list.txt' tidak ditemukan. Pastikan file ada di folder yang sama dengan script ini.")
