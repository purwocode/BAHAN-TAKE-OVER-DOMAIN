import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===== KONFIGURASI =====
URL = "https://fenix.svdns.com.br:2083/cpsess5800991227/json-api/cpanel"

HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://fenix.svdns.com.br:2083",
    "Referer": "https://fenix.svdns.com.br:2083/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

COOKIES = {
    "cpsession": "adcampon%3aFWhcfi_Ak49d4mJ2%2c359cfb16decc30c43893ac3c7ef467a7"
}

# ===== BACA DOMAIN DARI FILE =====
try:
    with open("domain.txt", "r", encoding="utf-8") as f:
        domains = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print("❌ File 'domain.txt' tidak ditemukan!")
    exit()

if not domains:
    print("⚠️ File 'domain.txt' kosong!")
    exit()

print(f"📄 Ditemukan {len(domains)} domain di domain.txt\n")

# ===== BUKA FILE SUKSES UNTUK MENYIMPAN =====
sukses_file = open("sukses.txt", "a", encoding="utf-8")

# ===== LOOP PROSES PARK DOMAIN =====
for domain in domains:
    print(f"🌐 Mem-park domain: {domain} ...")

    data = {
        "cpanel_jsonapi_apiversion": "2",
        "cpanel_jsonapi_module": "Park",
        "cpanel_jsonapi_func": "park",
        "domain": domain
    }

    try:
        res = requests.post(URL, headers=HEADERS, cookies=COOKIES, data=data, verify=False, timeout=15)
        if res.status_code != 200:
            print(f"❌ HTTP Error: {res.status_code}\n")
            continue

        result = res.json().get("cpanelresult", {})
        data_section = (result.get("data") or [{}])[0]
        success = data_section.get("result", 0)
        reason = data_section.get("reason") or result.get("error")

        if success == 1:
            print(f"✅ BERHASIL: {domain}\n")
            sukses_file.write(domain + "\n")
        else:
            print(f"❌ GAGAL: {domain}")
            if reason:
                print(f"   Alasan: {reason}\n")

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error koneksi pada {domain}: {e}\n")
    except Exception as e:
        print(f"⚠️ Kesalahan tidak terduga: {e}\n")

sukses_file.close()
print("✅ Semua proses selesai! Hasil sukses tersimpan di 'sukses.txt'.")
