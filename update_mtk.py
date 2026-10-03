import json
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

URL = "https://www.eredmenyek.com/foci/magyarorszag/nb-i/eredmenyek/"

matches = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    context = browser.new_context(
        locale="hu-HU",
        timezone_id="Europe/Budapest"
    )

    page = context.new_page()

    page.goto(URL, wait_until="domcontentloaded", timeout=60000)

    # Várunk, hogy az első eredmények megjelenjenek
    page.wait_for_timeout(5000)

    # Többször lefelé görgetünk, hogy az összes meccs betöltődjön
    for _ in range(12):
        page.mouse.wheel(0, 5000)
        page.wait_for_timeout(1500)

    # Minden linket átnézünk
    links = page.locator("a")
    count = links.count()

    for i in range(count):
        try:
            link = links.nth(i)

            text = " ".join(link.inner_text().split())
            href = link.get_attribute("href")

            if not href:
                continue

            if "mtk" not in text.lower():
                continue

            if "/merkozes/" not in href:
                continue

            if href.startswith("/"):
                href = "https://www.eredmenyek.com" + href

            stats_url = (
                href.rstrip("/")
                + "/osszefoglalas/statisztika/"
            )

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
