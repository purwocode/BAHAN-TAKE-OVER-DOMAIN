import requests
from bs4 import BeautifulSoup
import time
import re

# === Header HTTP ===
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.9,id;q=0.8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
}

BASE_URL = "https://rapiddns.io/sameip"

# === Baca daftar IP/domain dari file ===
with open("domain.txt", "r") as f:
    targets = [line.strip() for line in f if line.strip()]

# === Gunakan append agar hasil lama tidak terhapus ===
def save_line(text):
    """Menyimpan teks ke hasil.txt secara realtime (append mode)."""
    with open("hasil.txt", "a", encoding="utf-8") as file:
        file.write(text + "\n")
        file.flush()

def scrape_ip(ip):
    print(f"\n🔍 Memproses: {ip}")
    page = 1
    total_pages = 1
    total_count = None
    total_found = 0

    save_line(f"\n=== {ip} ===")

    while True:
        url = f"{BASE_URL}/{ip}?page={page}"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"⚠️ Gagal memuat halaman {page} untuk {ip}")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        # --- Ambil total hasil ---
        if total_count is None:
            total_span = soup.select_one("#result > div > div > div:nth-child(1) > div:nth-child(3) > span")
            total_count = total_span.text.strip() if total_span else "0"
            print(f"📊 Total hasil terdeteksi: {total_count}")
            save_line(f"Total (terdeteksi): {total_count}")

        # --- Ambil total halaman dari pagination ---
        if page == 1:
            pagination = soup.select("#result > div > div > nav > nav > ul li a")
            if pagination:
                page_numbers = []
                for a in pagination:
                    href = a.get("href", "")
                    match = re.search(r"\?page=(\d+)", href)
                    if match:
                        page_numbers.append(int(match.group(1)))
                if page_numbers:
                    total_pages = max(page_numbers)
            print(f"📄 Jumlah halaman terdeteksi: {total_pages}")
            save_line(f"Total halaman: {total_pages}")

        # --- Ambil domain dari selector utama ---
        table_wrap = soup.select_one("#result > div > div > div.progress-table-wrap.d-flex.align-items-left")
        if not table_wrap:
            print(f"⚠️ Tidak menemukan tabel hasil di halaman {page}")
            break

        tds = table_wrap.select("td")
        found = [td.text.strip() for td in tds if re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", td.text.strip())]

        if not found:
            print(f"⚠️ Tidak ada domain di halaman {page}")
            break

        total_found += len(found)
        print(f"📥 Halaman {page}: {len(found)} domain ditemukan")

        # Simpan hasil halaman ini secara realtime
        for domain in found:
            save_line(domain)

        if page >= total_pages:
            break

        page += 1
        time.sleep(1)

    print(f"✅ Total {total_found} domain berhasil disimpan untuk {ip}")
    save_line(f"Total domain disimpan: {total_found}")
    save_line("-" * 40)

# === Jalankan scraping untuk semua target ===
for target in targets:
    scrape_ip(target)

print("\n📁 Semua hasil telah disimpan (append mode) di 'hasil.txt'")
