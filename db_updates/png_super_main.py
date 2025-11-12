# main.py
import sys
import os
import mysql.connector
import requests
import time

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# project path already fine if files are colocated
from png_data_access import (
    get_db, pick_fixture, get_ref_info, get_fix_assets,
    get_top_foulers, get_top_shooters, get_top_yellows
)
from png_render_card import render_stat_pack, format_last5

# Secrets (bot token / channels) from your module
from python_api.get_secrets import foul_bot, gold_channel

TOKEN = foul_bot
# CHAT_ID = gold_channel
CHAT_ID = -5025317081

def main():
    project_directory = "environment/shaddypowder" if "C9_PORT" in os.environ else "shaddy-powder"

    try:
        db = get_db()
        cur = db.cursor(dictionary=True)
    except Exception as e:
        print(f"DB Error: {e}")
        sys.exit(1)

    fixtures = pick_fixture(cur)  # change to 39 for EPL
    for row in fixtures:
        fixture_id = row["fixture_id"]
        print(f"Processing fixture_id: {fixture_id}")
        try:
            ref = get_ref_info(cur, fixture_id)
            fix = get_fix_assets(cur, fixture_id)

            fouls = get_top_foulers(cur, fixture_id, limit=5)
            shots = get_top_shooters(cur, fixture_id, limit=5)
            yellows = get_top_yellows(cur, fixture_id, limit=3)

            # photos + last-5 formatting
            for p in fouls + shots + yellows:
                pid = p.get("player_id")
                if pid is not None and str(pid).strip() != "":
                    p["photo"] = f"https://media.api-sports.io/football/players/{pid}.png"

            for p in fouls:   p["metric"] = format_last5(p.get("metric"))
            for p in shots:   p["metric"] = format_last5(p.get("metric"))
            for p in yellows:
                raw = str(p.get("metric") or "").rstrip("-")
                p["metric"] = format_last5(raw)

            fixt = str(fix.get("fixt") or "").strip()
            if " vs " in fixt:
                home_name, away_name = [s.strip() for s in fixt.split(" vs ", 1)]
            else:
                home_name, away_name = (fixt or "Home"), "Away"

            data = {
                "league_logo": fix.get("league_photo"),
                "home_team": {"name": home_name, "logo": fix.get("home_team_photo")},
                "away_team": {"name": away_name, "logo": fix.get("away_team_photo")},
                "referee": {
                    "name": ref.get("cleaned_referee_name"),
                    "avg_yellows": ref.get("avg_yc_total"),
                    "last5": ref.get("last5_yc"),
                },
                "panels": {"fouls": fouls, "shots": shots, "yellows": yellows}
            }

            out_dir = f"/home/ec2-user/{project_directory}/generated_cards"
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, f"{fixture_id}.png")

            render_stat_pack(data, out_path)
            print(f"Generated {out_path}")

            with open(out_path, "rb") as photo_file:
                url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
                resp = requests.post(url, data={"chat_id": CHAT_ID}, files={"photo": photo_file})
                if resp.status_code == 200:
                    print(f"Posted to Telegram for fixture_id {fixture_id}")
                else:
                    print(f"Telegram error for {fixture_id}: {resp.text}")

        except Exception as e:
            print(f"Error processing fixture {fixture_id}: {e}")
            continue

    cur.close()
    db.close()

if __name__ == "__main__":
    main()
