import requests
import time

# ===== KONFIGURASI =====
base_url = "https://fenix.svdns.com.br:2083/cpsess5800991227/execute/DNS/mass_edit_zone"

headers = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://fenix.svdns.com.br:2083",
    "Referer": "https://fenix.svdns.com.br:2083/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

cookies = {
    "cpsession": "adcampon:qwuqoZNroFE2co2X,df3dd0113b7c2da5149ba06a820f61e6"
}

# ===== TEMPLATE DATA =====
remove_template = "zone={domain}&serial=2025103105&remove=13"

add_template = (
    "zone={domain}&serial=2025103106"
    "&add=%7B%22dname%22%3A%22{domain}.%22%2C%22ttl%22%3A14400%2C%22record_type%22%3A%22MX%22%2C%22line_index%22%3Anull%2C%22data%22%3A%5B1%2C%22smtp.google.com%22%5D%7D"
    "&add=%7B%22dname%22%3A%22{domain}.%22%2C%22ttl%22%3A14400%2C%22record_type%22%3A%22MX%22%2C%22line_index%22%3Anull%2C%22data%22%3A%5B1%2C%22aspmx.l.google.com%22%5D%7D"
    "&add=%7B%22dname%22%3A%22{domain}.%22%2C%22ttl%22%3A14400%2C%22record_type%22%3A%22MX%22%2C%22line_index%22%3Anull%2C%22data%22%3A%5B5%2C%22alt1.aspmx.l.google.com%22%5D%7D"
    "&add=%7B%22dname%22%3A%22{domain}.%22%2C%22ttl%22%3A14400%2C%22record_type%22%3A%22MX%22%2C%22line_index%22%3Anull%2C%22data%22%3A%5B5%2C%22alt2.aspmx.l.google.com%22%5D%7D"
    "&add=%7B%22dname%22%3A%22{domain}.%22%2C%22ttl%22%3A14400%2C%22record_type%22%3A%22MX%22%2C%22line_index%22%3Anull%2C%22data%22%3A%5B10%2C%22alt3.aspmx.l.google.com%22%5D%7D"
    "&add=%7B%22dname%22%3A%22{domain}.%22%2C%22ttl%22%3A14400%2C%22record_type%22%3A%22MX%22%2C%22line_index%22%3Anull%2C%22data%22%3A%5B10%2C%22alt4.aspmx.l.google.com%22%5D%7D"
)

# ===== BACA DOMAIN DARI FILE =====
with open("sukses.txt", "r") as file:
    domains = [line.strip() for line in file if line.strip()]

print(f"🔍 Ditemukan {len(domains)} domain di sukses.txt\n")

# ===== PROSES SETIAP DOMAIN =====
for domain in domains:
    print(f"🧾 Memproses domain: {domain}")

    # -- Hapus record lama --
    remove_data = remove_template.format(domain=domain)
    remove_res = requests.post(base_url, headers=headers, cookies=cookies, data=remove_data, verify=False)
    print(f"   🧹 Hapus record -> {remove_res.status_code}")

    # -- Tambah MX baru --
    add_data = add_template.format(domain=domain)
    add_res = requests.post(base_url, headers=headers, cookies=cookies, data=add_data, verify=False)
    print(f"   ⚙️ Tambah MX -> {add_res.status_code}")

    # Coba tampilkan hasil singkat
    try:
        print("   Hasil:", add_res.json())
    except:
        print("   Hasil:", add_res.text[:120], "...\n")

    # Delay ringan biar server tidak overload
    time.sleep(1)

print("\n✅ Semua domain telah diproses.")
