import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

RESULTS_URL = "https://www.eredmenyek.com/foci/magyarorszag/nb-i/eredmenyek/"
FIXTURES_URL = "https://www.eredmenyek.com/foci/magyarorszag/nb-i/meccsek/"

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/143.0 Mobile Safari/537.36"
}


def get_matches(url):
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    matches = []

    for link in soup.find_all("a", href=True):
        href = link["href"]

        # Csak valódi mérkőzéslinkek
        if "/merkozes/foci/" not in href:
            continue

        text = " ".join(link.stripped_strings)

        full_url = href

        if not full_url.startswith("http"):
            full_url = "https://www.eredmenyek.com" + full_url

        # Csak olyan mérkőzés kell, ahol MTK szerepel
        combined = (text + " " + full_url).lower()

        if "mtk" not in combined:
            continue

        stats_url = (
            full_url.rstrip("/")
            + "/osszefoglalas/statisztika/"
        )

        matches.append({
            "text": text,
            "url": full_url,
            "stats_url": stats_url
        })

    return matches


matches = []

# Lejátszott mérkőzések
matches.extend(get_matches(RESULTS_URL))

# Következő mérkőzések
matches.extend(get_matches(FIXTURES_URL))


# Duplikációk eltávolítása
unique = {}

for match in matches:
    unique[match["url"]] = match

matches = list(unique.values())


data = {
    "updated": datetime.utcnow().isoformat() + "Z",
    "source": RESULTS_URL,
    "matches": matches
}


with open("data/mtk.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)


print(f"{len(matches)} MTK mérkőzés elmentve.")
