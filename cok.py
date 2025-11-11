import aiohttp
import asyncio
import json
from aiohttp import ClientSession

# Konfigurasi dasar
URL = "https://central.pophosting.com.br/index.php?rp=/domain/check"

HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://central.pophosting.com.br",
    "Referer": "https://central.pophosting.com.br/cart.php?a=add&domain=register",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

COOKIE_STRING = (
    "WHMCSBoeDIcc27D1B=2bcdfb5e7846f763f211d79c7b11dc09; "
    "__stripe_mid=76e8ee20-4e29-41c3-a4f8-7eb101f17ad9077b99; "
    "__stripe_sid=7ff9755a-8844-4bb3-925a-531d95b954a1098e77"
)
COOKIES = dict(pair.split("=", 1) for pair in COOKIE_STRING.split("; "))
TOKEN = "4802680f29c34fd31d50b9fffaf7d931275d879e"

# Batas request paralel (ubah kalau ingin lebih cepat)
MAX_CONCURRENT = 10


async def check_domain(session: ClientSession, domain: str, sem: asyncio.Semaphore):
    """Cek status domain secara async"""
    async with sem:
        data = {
            "token": TOKEN,
            "a": "checkDomain",
            "domain": domain.strip(),
            "type": "domain",
        }
        try:
            async with session.post(URL, data=data, cookies=COOKIES, timeout=15) as resp:
                text = await resp.text()
                try:
                    js = json.loads(text)
                except json.JSONDecodeError:
                    print(f"⚠️ {domain} → Respons bukan JSON valid")
                    return ("error", domain)

                info = js.get("result", [{}])[0]
                legacy_status = info.get("legacyStatus", "").lower()
                price = info.get("pricing", {}).get("1", {}).get("register", "N/A")

                if legacy_status == "available":
                    print(f"✅ {domain} → Available | Harga: {price}")
                    return ("available", domain)
                elif legacy_status == "unavailable":
                    print(f"❌ {domain} → Unavailable | Harga: {price}")
                    return ("unavailable", domain)
                else:
                    print(f"⚠️ {domain} → Status tidak diketahui ({legacy_status})")
                    return ("unknown", domain)

        except Exception as e:
            print(f"⚠️ {domain} → Error: {e}")
            return ("error", domain)


async def main():
    try:
        with open("domains.txt", "r", encoding="utf-8") as f:
            domains = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("❌ File 'domains.txt' tidak ditemukan!")
        return

    print(f"🔍 Mengecek {len(domains)} domain...\n")

    available, unavailable = [], []
    sem = asyncio.Semaphore(MAX_CONCURRENT)

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        tasks = [check_domain(session, domain, sem) for domain in domains]
        for task in asyncio.as_completed(tasks):
            status, domain = await task
            if status == "available":
                available.append(domain)
            elif status == "unavailable":
                unavailable.append(domain)

    # Simpan hasil
    if available:
        with open("available_domains.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(available))
    if unavailable:
        with open("unavailable_domains.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(unavailable))

    print("\n✅ Pemeriksaan selesai.")
    print(f"📁 {len(available)} domain tersedia → available_domains.txt")
    print(f"📁 {len(unavailable)} domain tidak tersedia → unavailable_domains.txt")


if __name__ == "__main__":
    asyncio.run(main())
