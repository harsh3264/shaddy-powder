import os
import sys
import mysql.connector
import requests
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

# Add parent dir
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Data access
from png_data_access import (
    get_db, pick_fixture, get_ref_info, get_fix_assets,
    get_top_foulers, get_top_foul_drawers, get_top_shooters, get_top_yellows
)

# Secrets
from python_api.get_secrets import foul_bot, gold_channel

TOKEN = foul_bot
CHAT_ID = -5025317081  # your group

ASSETS_DIR = os.path.join(parent_dir, "assets")
HTML_TEMPLATE = "stat_card.html"
CSS_FILE = "stat_card.css"


def render_html_to_png(html_output, output_path):
    """Render HTML string to PNG using Playwright Chromium."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1080})
        
        # Load HTML directly as content
        page.set_content(html_output, wait_until="networkidle")
        
        page.screenshot(path=output_path)
        browser.close()


def main():
    # Prepare DB
    try:
        db = get_db()
        cur = db.cursor(dictionary=True)
    except Exception as e:
        print(f"DB Error: {e}")
        sys.exit(1)

    # Load Jinja
    env = Environment(loader=FileSystemLoader(ASSETS_DIR))
    template = env.get_template(HTML_TEMPLATE)

    fixtures = pick_fixture(cur)

    for row in fixtures:
        fixture_id = row["fixture_id"]
        print(f"Processing fixture_id: {fixture_id}")

        try:
            ref = get_ref_info(cur, fixture_id)
            fix = get_fix_assets(cur, fixture_id)

            foulers = get_top_foulers(cur, fixture_id, limit=5)
            drawers = get_top_foul_drawers(cur, fixture_id, limit=5)
            shots = get_top_shooters(cur, fixture_id, limit=5)
            yellows = get_top_yellows(cur, fixture_id, limit=3)

            # Add photo URLs + format metrics
            for p in foulers + drawers + shots + yellows:
                pid = p.get("player_id")
                if pid:
                    p["photo"] = f"https://media.api-sports.io/football/players/{pid}.png"
                p["metric"] = format_last5(p.get("metric"))


            # Prepare fixture names
            fixt = fix.get("fixt") or ""
            if " vs " in fixt:
                home_name, away_name = [s.strip() for s in fixt.split(" vs ", 1)]
            else:
                home_name, away_name = fixt, ""

            # Data object for template
            data = {
                "league_logo": fix.get("league_photo"),
                "home_team": {"name": home_name, "logo": fix.get("home_team_photo")},
                "away_team": {"name": away_name, "logo": fix.get("away_team_photo")},
                "referee": {
                    "name": ref.get("cleaned_referee_name"),
                    "avg_yellows": round(float(ref.get("avg_yc_total") or 0), 1),
                    "last5": ref.get("last5_yc"),
                },
                "panels": {
                    "fouls": foulers,
                    "drawers": drawers,      # NEW
                    "shots": shots,
                    "yellows": yellows
                }
            }

            # Render HTML
            html_output = template.render(**data)

            # Output path
            output_path = os.path.join(ASSETS_DIR, f"{fixture_id}.png")

            # Convert to PNG
            render_html_to_png(html_output, output_path)
            print(f"PNG generated: {output_path}")

            # Send to Telegram
            with open(output_path, "rb") as f:
                url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
                resp = requests.post(
                    url,
                    data={"chat_id": CHAT_ID},
                    files={"photo": f}
                )

            if resp.status_code == 200:
                print("Posted to Telegram")
            else:
                print(f"Telegram error: {resp.text}")

        except Exception as e:
            print(f"Error processing fixture {fixture_id}: {e}")
            continue

    cur.close()
    db.close()


if __name__ == "__main__":
    main()
