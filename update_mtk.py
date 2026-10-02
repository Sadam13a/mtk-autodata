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

    # Megvárjuk, hogy az eredmények megjelenjenek
    page.get_by_text("MTK Budapest", exact=True).first.wait_for(
        state="visible",
        timeout=30000
    )

    # Az MTK-t tartalmazó elemek keresése
    mtk_elements = page.get_by_text("MTK Budapest", exact=True)

    count = mtk_elements.count()

    for i in range(count):
        try:
            element = mtk_elements.nth(i)

            # Megkeressük a mérkőzéshez tartozó legközelebbi linket
            link = element.locator("xpath=ancestor::a[1]")

            if link.count() == 0:
                link = element.locator("xpath=ancestor::*[self::div or self::article][1]")

            text = " ".join(element.inner_text().split())

            href = None

            if link.count() > 0:
                href = link.first.get_attribute("href")

            if href:
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
    if match.get("url"):
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
