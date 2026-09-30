import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.eredmenyek.com/csapat/mtk-budapest/ppX6bEHk/eredmenyek/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

matches = []

for link in soup.find_all("a", href=True):
    href = link["href"]

    if "/merkozes/foci/" not in href:
        continue

    text = " ".join(link.stripped_strings)

    if not text:
        continue

    if not href.startswith("http"):
        href = "https://www.eredmenyek.com" + href

    stats_url = href.rstrip("/") + "/osszefoglalas/statisztika/"

    matches.append({
        "text": text,
        "url": href,
        "stats_url": stats_url
    })

# Duplikációk eltávolítása
unique = {}
for match in matches:
    unique[match["url"]] = match

matches = list(unique.values())

data = {
    "updated": datetime.utcnow().isoformat() + "Z",
    "source": URL,
    "matches": matches
}

with open("data/mtk.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"{len(matches)} mérkőzés elmentve.")
