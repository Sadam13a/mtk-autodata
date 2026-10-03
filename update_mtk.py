import json
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit

from playwright.sync_api import sync_playwright


URL = "https://www.eredmenyek.com/csapat/mtk-budapest/ppX6bEHk/eredmenyek/"
MTK_ID = "ppX6bEHk"


def make_stats_url(url):
    parts = urlsplit(url)

    path = parts.path.rstrip("/") + "/osszefoglalas/statisztika/"

    return urlunsplit((
        parts.scheme,
        parts.netloc,
        path,
        parts.query,
        parts.fragment
    ))


def team_name_from_slug(slug):
    parts = slug.rsplit("-", 1)

    if len(parts) == 2:
        name = parts[0]
    else:
        name = slug

    return name.replace("-", " ").title()


matches = []


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    context = browser.new_context(
        locale="hu-HU",
        timezone_id="Europe/Budapest"
    )

    page = context.new_page()

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(5000)

    # Több mérkőzés betöltése
    for _ in range(10):
        try:
            buttons = page.get_by_text(
                "További meccsek",
                exact=True
            )

            if buttons.count() == 0:
                break

            clicked = False

            for i in range(buttons.count()):
                try:
                    button = buttons.nth(i)

                    if button.is_visible():
                        button.click()
                        page.wait_for_timeout(1500)
                        clicked = True

                except Exception:
                    pass

            if not clicked:
                break

        except Exception:
            break

    # Mérkőzéslinkek
    links = page.locator('a[href*="/merkozes/foci/"]')
    count = links.count()

    for i in range(count):
        try:
            link = links.nth(i)

            href = link.get_attribute("href")

            if not href:
                continue

            if MTK_ID not in href:
                continue

            if href.startswith("/"):
                href = "https://www.eredmenyek.com" + href

            # URL feldarabolása
            parts = urlsplit(href)
            path_parts = [
                x for x in parts.path.split("/")
                if x
            ]

            if len(path_parts) < 4:
                continue

            home_slug = path_parts[-2]
            away_slug = path_parts[-1]

            home = team_name_from_slug(home_slug)
            away = team_name_from_slug(away_slug)

            # MTK nevének helyes megjelenítése
            if MTK_ID in home_slug:
                home = "MTK Budapest"

            if MTK_ID in away_slug:
                away = "MTK Budapest"

            text = f"{home} - {away}"

            stats_url = make_stats_url(href)

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


with open(
    "data/mtk.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        data,
        f,
        ensure_ascii=False,
        indent=2
    )


print(f"{len(matches)} MTK mérkőzés elmentve.")
