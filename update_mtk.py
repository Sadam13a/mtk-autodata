import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

URLS = [
    "https://www.eredmenyek.com/foci/magyarorszag/nb-i/eredmenyek/",
    "https://www.eredmenyek.com/foci/magyarorszag/nb-i/meccsek/"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36",
    "Accept-Language": "hu-HU,hu;q=0.9"
}

matches = []

for url in URLS:
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Az oldal teljes szövege
    text = soup.get_text(" ", strip=True)

    # MTK-t tartalmazó szövegrészek keresése
    for match in re.finditer(
        r'(\d{1,2}\.\d{1,2}\.\s+\d{1,2}:\d{2})\s+'
        r'(MTK Budapest|[^|]+?)\s+'
        r'(MTK Budapest|[^|]+?)',
        text,
        re.IGNORECASE
    ):
        date_time = match.group(1)
        home = match.group(2).strip()
        away = match.group(3).strip()

        if "mtk" not in (home + " " + away).lower():
            continue

        matches.append({
            "date": date_time,
            "home": home,
            "away": away,
            "source": url
        })

# Duplikációk eltávolítása
unique = {}

for m in matches:
    key = (m["date"], m["home"], m["away"])
    unique[key] = m

matches = list(unique.values())

data = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "source": "https://www.eredmenyek.com/",
    "matches": matches
}

with open("data/mtk.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"{len(matches)} MTK mérkőzés elmentve.")
