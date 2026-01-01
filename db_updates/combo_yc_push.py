import os
import sys
import mysql.connector
import requests
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

# Add parent dir
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from combo_png_data import get_db, pick_fixtures, get_fix_assets, get_top_yellow
from python_api.get_secrets import foul_bot, gold_channel

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(parent_dir, "assets")

TEMPLATE = "combo_work.html"
TELEGRAM_TOKEN = foul_bot
gold_channel = -5025317081 
CHANNELS = [gold_channel]


def render_png(html, out):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width":1080,"height":1080})
        page.set_content(html, wait_until="networkidle")
        page.screenshot(path=out, full_page=True)
        browser.close()


def send_telegram(path):
    for ch in CHANNELS:
        with open(path, "rb") as f:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
                data={"chat_id": ch},
                files={"photo": f}
            )


def main():
    db = get_db()
    cur = db.cursor(dictionary=True)

    fixtures = pick_fixtures(cur)
    games = []

    for fx in fixtures:
        fid = fx["fixture_id"]
        fix = get_fix_assets(cur, fid)
        yc = get_top_yellow(cur, fid)
        if not yc:
            continue

        games.append({
            "home_logo": fix["home_team_photo"],
            "away_logo": fix["away_team_photo"],
            "player": {
                "name": yc["name"],
                "team": yc["team_name"],
                "season_yc": yc["season_league_cards"],
                "avg_fouls": yc["avg_fouls"],
                "last5": yc["last5"],
                "photo": f"https://media.api-sports.io/football/players/{yc['player_id']}.png"
            }
        })

    env = Environment(loader=FileSystemLoader(ASSETS_DIR))
    html = env.get_template(TEMPLATE).render(games=games)

    out = os.path.join(ASSETS_DIR, "combo_yc.png")
    render_png(html, out)
    send_telegram(out)

    cur.close()
    db.close()


if __name__ == "__main__":
    main()
