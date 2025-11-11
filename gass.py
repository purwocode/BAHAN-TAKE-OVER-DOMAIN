import requests
import json

# === CONFIG ===
INPUT_FILE = "domains.txt"         # daftar domain, 1 per baris
API_URL = "https://sfbff.newfold.com/api/v1/domain-search"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "if-none-match": 'W/"c933-FXUlIHJ2c8geHTliaHMK6FD6dX0"',
    "origin": "https://www.bluehost.com",
    "priority": "u=1, i",
    "referer": "https://www.bluehost.com/",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/141.0.0.0 Safari/537.36"
    ),
    "x-api-key": "yneujmorzfuezfwrczobxjr5jdg",
    "x-client-id": "NSI"
}

TLD_ORDER = [
    ".com", ".net", ".org", ".store", ".online",
    ".site", ".tech", ".info", ".biz", ".us", ".ca"
]


# === FUNGSI CEK DOMAIN ===
def check_domain(domain):
    params = {
        "brand": "BLUEHOST",
        "domains": domain,
        "useConfigTlds": "true",
        "spinSearch": "true",
        "aftermarketDomainsReq": "true",
        "registryPremium": "true",
        "includePremiumDomainsInTopTlds": "true",
        "spinDomainsWithoutTldsReq": "true",
        "env": "prod",
        "flowId": "domainFirstFlow",
        "aftermarket": "true",
        "client": "UPP",
        "currencyCode": "USD",
        "tldOrder": TLD_ORDER
    }

    try:
        r = requests.get(API_URL, headers=HEADERS, params=params, timeout=30)
        if r.status_code != 200:
            print(f"⚠️ Gagal memeriksa {domain} (status: {r.status_code})")
            return None

        data = r.json()
        data_section = data.get("response", {}).get("data", {})

        # Ambil semua kategori domain
        searched = data_section.get("searchedDomains", [])
        spin = data_section.get("spinDomains", [])
        top_tld = data_section.get("topTldDomains", [])
        aftermarket = data_section.get("aftermarketDomains", [])

        all_domains = searched + spin + top_tld + aftermarket

        # Cari domain utama
        main_domain_info = next(
            (d for d in all_domains if d.get("domainName") == domain),
            None
        )

        if not main_domain_info:
            print(f"⚠️ Domain {domain} tidak ditemukan di hasil respon.")
            return None

        available = main_domain_info.get("available", False)
        return available

    except Exception as e:
        print(f"❌ Error saat memeriksa {domain}: {e}")
        return None


# === MAIN ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    domains = [line.strip() for line in f if line.strip()]

print(f"🚀 Memulai pemeriksaan {len(domains)} domain...\n")

for i, domain in enumerate(domains, start=1):
    available = check_domain(domain)

    if available is True:
        print(f"[{i}/{len(domains)}] ✅ {domain} tersedia")
        with open("available_domains.txt", "a", encoding="utf-8") as fa:
            fa.write(domain + "\n")
    elif available is False:
        print(f"[{i}/{len(domains)}] ❌ {domain} tidak tersedia")
        with open("unavailable_domains.txt", "a", encoding="utf-8") as fu:
            fu.write(domain + "\n")
    else:
        print(f"[{i}/{len(domains)}] ⚠️ Tidak dapat menentukan status {domain}")

print("\n✅ Pemeriksaan selesai!")
print("📗 Hasil tersimpan di available_domains.txt dan unavailable_domains.txt")
