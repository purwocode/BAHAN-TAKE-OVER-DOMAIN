import tldextract

input_file = "hasil.txt"
domain_file = "domain.txt"
subdomain_file = "subdomain.txt"

# Baca semua domain dari hasil.txt
with open(input_file, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip() and not line.startswith("=")]

# Hilangkan duplikat
unique_domains = list(set(lines))

domains = set()
subdomains = set()

for item in unique_domains:
    extracted = tldextract.extract(item)
    if extracted.domain and extracted.suffix:
        full_domain = f"{extracted.domain}.{extracted.suffix}"
        if extracted.subdomain:
            subdomains.add(item)
        else:
            domains.add(full_domain)

# Simpan domain utama
with open(domain_file, "w", encoding="utf-8") as d:
    for dom in sorted(domains):
        d.write(dom + "\n")

# Simpan subdomain
with open(subdomain_file, "w", encoding="utf-8") as s:
    for sub in sorted(subdomains):
        s.write(sub + "\n")

print(f"✅ Ekstraksi selesai!")
print(f"- Domain utama: {len(domains)} disimpan di {domain_file}")
print(f"- Subdomain   : {len(subdomains)} disimpan di {subdomain_file}")
