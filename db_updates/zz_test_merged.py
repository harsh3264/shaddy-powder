import os
import sys
import time
import requests
import mysql.connector
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
import tweepy
import html
from openai import OpenAI  # NEW API CLIENT

# ====================================================
#  PATH & ENV SETUP
# ====================================================
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

ASSETS_DIR = os.path.join(parent_dir, "assets")
HTML_TEMPLATE = "stat_card.html"
CSS_FILE = "stat_card.css"

# ====================================================
#  IMPORT PROJECT HELPERS AND SECRETS
# ====================================================
from png_data_access import (
    get_db, pick_fixture, get_ref_info, get_fix_assets,
    get_top_foulers, get_top_foul_drawers,
    get_top_shooters, get_top_yellows
)

from python_api.get_secrets import (
    foul_bot, gold_channel, gpt_key,
    x_app_api_key, x_app_api_key_secret,
    x_app_access_token, x_app_access_token_secret
)

# OpenAI Client Init (NEW VERSION)
client = OpenAI(api_key=gpt_key)

TELEGRAM_TOKEN = foul_bot
TELEGRAM_CHANNELS = [gold_channel]


# ====================================================
#  UTILS
# ====================================================
def format_last5(val):
    if val is None:
        return ""
    s = str(val).strip().replace(" ", "")
    if "-" in s:
        return s
    if not s.isdigit():
        return s
    return "-".join(list(s))


# ====================================================
#  HTML → PNG RENDER
# ====================================================
def render_html_to_png(html_output, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1080})
        page.set_content(html_output, wait_until="networkidle")

        canvas = page.locator(".canvas")
        canvas.wait_for(state="visible")
        canvas.screenshot(path=output_path)

        browser.close()


# ====================================================
#  TELEGRAM SENDER
# ====================================================
def send_png_to_telegram(image_path, channels):
    for ch in channels:
        with open(image_path, "rb") as f:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            resp = requests.post(
                url,
                data={"chat_id": ch},
                files={"photo": f}
            )
        if resp.status_code == 200:
            print(f"PNG posted to Telegram: {ch}")
        else:
            print(f"Telegram error: {resp.text}")


# ====================================================
#  TWITTER CLIENTS
# ====================================================
def create_media_api():
    auth = tweepy.OAuth1UserHandler(
        x_app_api_key,
        x_app_api_key_secret,
        x_app_access_token,
        x_app_access_token_secret
    )
    return tweepy.API(auth)

def create_v2_client():
    return tweepy.Client(
        consumer_key=x_app_api_key,
        consumer_secret=x_app_api_key_secret,
        access_token=x_app_access_token,
        access_token_secret=x_app_access_token_secret
    )


# ====================================================
#  POST TO X/TWITTER
# ====================================================
def post_to_x(image_path, tweet_text):
    media_api = create_media_api()
    media = media_api.media_upload(image_path)
    media_id = media.media_id_string

    client_v2 = create_v2_client()
    client_v2.create_tweet(text=tweet_text, media_ids=[media_id])
    print("Tweet posted successfully.")


# ====================================================
#  GENAI TWEET GENERATOR (UPDATED FOR NEW OPENAI API)
# ====================================================
def generate_llm_tweet(fixture_string, teamA, teamB, league, yc_data, fun_stat):

    prompt = f"""
You create football analytics tweets. Follow the exact required format.

Fixture: {fixture_string}
Team A: {teamA}
Team B: {teamB}
League: {league}

Player Data:
Name: {yc_data.get("player_name")}
Team: {yc_data.get("team_name")}
Position: {yc_data.get("position")}
Last 5 Metric: {yc_data.get("metric")}
Season YC: {yc_data.get("season_league_cards")}
Avg Fouls/Game: {yc_data.get("avg_fouls_total")}
Argument YC %: {yc_data.get("argument_related_yc")}
Time-Wasting YC %: {yc_data.get("time_wasting_related_yc")}

Fun Stat: {fun_stat}

STRICT REQUIREMENTS:
- Output ONLY the tweet text.
- MUST include team-specific colored circle emojis based on real kits.
- MAX 2 sentences before hashtags.
- EXACTLY 6 hashtags.
- No markdown formatting.
"""

    response = client.chat.completions.create(
        model="gpt-5.1",  # NEW MODEL
        messages=[
            {"role": "system", "content": "You write sharp, clean football betting tweets."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.45
    )

    return response.choices[0].message.content.strip()


# ====================================================
#  MAIN FIXTURE PROCESSOR
# ====================================================
def process_fixture(fixture_id, db_cursor):

    print(f"\n=== Processing Fixture {fixture_id} ===")

    # Fetch data
    ref = get_ref_info(db_cursor, fixture_id)
    fix = get_fix_assets(db_cursor, fixture_id)
    foulers = get_top_foulers(db_cursor, fixture_id, limit=5)
    drawers = get_top_foul_drawers(db_cursor, fixture_id, limit=5)
    shots = get_top_shooters(db_cursor, fixture_id, limit=5)
    yellows = get_top_yellows(db_cursor, fixture_id, limit=3)

    # Add photo URLs + formatted metrics
    for p in foulers + drawers + shots + yellows:
        pid = p.get("player_id")
        if pid:
            p["photo"] = f"https://media.api-sports.io/football/players/{pid}.png"
        p["metric"] = format_last5(p.get("metric"))


    # Fixture names
    fixt = fix.get("fixt") or ""
    if " vs " in fixt:
        home_name, away_name = [s.strip() for s in fixt.split(" vs ", 1)]
    else:
        home_name, away_name = fixt, ""


    # Prepare YC data
    yc = yellows[0] if yellows else {}

    yc_data = {
        "player_name": yc.get("name", ""),
        "team_name": yc.get("team_name", ""),
        "metric": yc.get("metric", ""),
        "season_league_cards": yc.get("season_league_cards", ""),
        "avg_fouls_total": yc.get("avg_fouls_total", ""),
        "argument_related_yc": yc.get("argument_related_yc", ""),
        "time_wasting_related_yc": yc.get("time_wasting_related_yc", ""),
        "position": yc.get("pos", ""),
        "player_id": yc.get("player_id", "")
    }

    # Fun stat
    fun_stat = "Team to have 4 or more offsides."


    # Render PNG card
    env = Environment(loader=FileSystemLoader(ASSETS_DIR))
    template = env.get_template(HTML_TEMPLATE)

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
            "drawers": drawers,
            "shots": shots,
            "yellows": yellows
        }
    }

    html_output = template.render(**data)
    png_path = os.path.join(ASSETS_DIR, f"{fixture_id}.png")
    render_html_to_png(html_output, png_path)
    print(f"PNG generated: {png_path}")

    # Send to Telegram
    send_png_to_telegram(png_path, TELEGRAM_CHANNELS)

    # Generate tweet text using GPT
    tweet_text = generate_llm_tweet(
        fixture_string=fixt,
        teamA=home_name,
        teamB=away_name,
        league=fix.get("league_name", ""),
        yc_data=yc_data,
        fun_stat=fun_stat
    )

    # Post to Twitter
    post_to_x(png_path, tweet_text)


# ====================================================
#  ENTRY POINT
# ====================================================
def main():

    try:
        db = get_db()
        cur = db.cursor(dictionary=True)
    except Exception as e:
        print(f"DB Error: {e}")
        sys.exit(1)

    fixtures = pick_fixture(cur)

    for row in fixtures:
        fixture_id = row["fixture_id"]
        try:
            process_fixture(fixture_id, cur)
        except Exception as e:
            print(f"Error processing {fixture_id}: {e}")
            continue

    cur.close()
    db.close()


if __name__ == "__main__":
    main()
