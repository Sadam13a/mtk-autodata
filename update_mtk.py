import json
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

URL = "https://www.eredmenyek.com/foci/magyarorszag/nb-i/eredmenyek/"

matches = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        locale="hu-HU",
        timezone_id="Europe/Budapest"
    )

    page.goto(URL, wait_until="networkidle", timeout=60000)

    # Betöltés után még várunk egy kicsit
    page.wait_for_timeout(5000)

    # Minden mérkőzéshez tartozó link
    links = page.locator('a[href*="/merkozes/"]')

    count = links.count()

    for i in range(count):
        link = links.nth(i)

        try:
            text = " ".join(link.inner_text().split())
            href = link.get_attribute("href")

            if not href or not text:
                continue

            # Csak MTK-s mérkőzések
            if "mtk" not in text.lower():
                continue

            if href.startswith("/"):
                href = "https://www.eredmenyek.com" + href

            stats_url = href.rstrip("/") + "/osszefoglalas/statisztika/"

            matches.append({
                "text": text,
                "url": href,
                "stats_url": stats_url
            })

        except Exception:
            continue

    browser.close()

# Duplikációk eltávolítása
unique = {}

for match in matches:
    unique[match["url"]] = match

matches = list(unique.values())

data = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "source": URL,
    "matches": matches
}

with open("data/mtk.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"{len(matches)} MTK mérkőzés elmentve.")
