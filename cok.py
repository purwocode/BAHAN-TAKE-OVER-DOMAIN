import aiohttp
import asyncio
import json
from aiohttp import ClientSession
from bs4 import BeautifulSoup

# === KONFIGURASI DASAR === #
BASE_URL = "https://central.pophosting.com.br"
CHECK_URL = f"{BASE_URL}/index.php?rp=/domain/check"
TOKEN_PAGE = f"{BASE_URL}/cart.php?a=add&domain=register"

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": BASE_URL,
    "priority": "u=1, i",
    "referer": TOKEN_PAGE,
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}

COOKIE_STRING = (
    "__stripe_mid=76e8ee20-4e29-41c3-a4f8-7eb101f17ad9077b99; "
    "_ga=GA1.1.1248964013.1761856247; "
    "_ga_QEQ27X2HXJ=GS2.1.s1761856247$o1$g0$t1761856331$j60$l0$h0; "
    "WHMCSBoeDIcc27D1B=557453e7a095db205c9dcbb284f42924; "
    "__stripe_sid=cd3d804b-d9bb-431b-bd96-70abf5ffca5bb1f7f8"
)
COOKIES = dict(pair.split("=", 1) for pair in COOKIE_STRING.split("; "))

MAX_CONCURRENT = 10


async def get_token(session: ClientSession) -> str:
    """Ambil token dari halaman form"""
    async with session.get(TOKEN_PAGE, cookies=COOKIES, timeout=15) as resp:
        html = await resp.text()
        soup = BeautifulSoup(html, "html.parser")

        token_input = soup.select_one("#frmDomainChecker > input[type=hidden]:nth-child(1)")
        if token_input and token_input.get("value"):
            token = token_input["value"]
            print(f"🔑 Token ditemukan: {token}")
            return token
        else:
            raise ValueError("Tidak dapat menemukan token dari halaman.")


async def check_domain(session: ClientSession, token: str, domain: str, sem: asyncio.Semaphore):
    """Cek status domain secara async (mengikuti format cURL)"""
    async with sem:
        payload = {
            "token": token,
            "a": "checkDomain",
            "domain": domain.strip(),
            "type": "spotlight",  # sesuai data cURL
        }

        try:
            async with session.post(CHECK_URL, data=payload, cookies=COOKIES, timeout=20) as resp:
                text = await resp.text()

                try:
                    js = json.loads(text)
                except json.JSONDecodeError:
                    print(f"⚠️ {domain} → Respons bukan JSON valid")
                    return ("error", domain)

                result_list = js.get("result", [])
                if not result_list:
                    print(f"⚠️ {domain} → Tidak ada data di 'result'")
                    return ("unknown", domain)

                # 🔍 Cari domain yang persis sama
                target = next((r for r in result_list if r.get("domainName", "").lower() == domain.lower()), None)
                if not target:
                    print(f"🚫 {domain} → Tidak ditemukan di response")
                    return ("unknown", domain)

                legacy_status = target.get("legacyStatus", "").lower()
                price = target.get("shortestPeriod", {}).get("register", "N/A")

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
        with open("domain.txt", "r", encoding="utf-8") as f:
            domains = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("❌ File 'domain.txt' tidak ditemukan!")
        return

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        print("🔍 Mengambil token dari halaman...")
        token = await get_token(session)

        print(f"\n🔍 Mengecek {len(domains)} domain...\n")

        sem = asyncio.Semaphore(MAX_CONCURRENT)
        tasks = [check_domain(session, token, domain, sem) for domain in domains]

        for task in asyncio.as_completed(tasks):
            status, domain = await task
            if status == "available":
                with open("domain_available.txt", "a", encoding="utf-8") as f:
                    f.write(domain + "\n")
            elif status == "unavailable":
                with open("domain_unavailable.txt", "a", encoding="utf-8") as f:
                    f.write(domain + "\n")

    print("\n✅ Pemeriksaan selesai.")
    print("📁 Domain tersedia → domain_available.txt")
    print("📁 Domain tidak tersedia → domain_unavailable.txt")


if __name__ == "__main__":
    asyncio.run(main())
