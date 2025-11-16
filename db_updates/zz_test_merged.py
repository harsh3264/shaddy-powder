import os
import sys
import time
import requests
import mysql.connector
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
import tweepy
import openai

# ================================
#  PATHS & ENV SETUP
# ================================
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

ASSETS_DIR = os.path.join(parent_dir, "assets")
HTML_TEMPLATE = "stat_card.html"
CSS_FILE = "stat_card.css"

# ================================
#   IMPORT PROJECT HELPERS
# ================================
from v2_png_data_access import (
    get_db, pick_fixture, get_ref_info, get_fix_assets,
    get_top_foulers, get_top_foul_drawers, get_top_shooters, get_top_yellows
)

from python_api.get_secrets import (
    foul_bot, gold_channel, gpt_key,
    x_app_api_key, x_app_api_key_secret,
    x_app_access_token, x_app_access_token_secret
)

from python_api.gpt_prompts import yc_foul_prompt

gold_channel = -5025317081

# ================================
#   CONSTANTS
# ================================
TELEGRAM_TOKEN = foul_bot
TELEGRAM_CHANNELS = [gold_channel]
openai.api_key = gpt_key


# ================================
#  UTILS
# ================================
def format_last5(val):
    if val is None:
        return ""
    s = str(val).strip().replace(" ", "")
    if "-" in s:
        return s
    if not s.isdigit():
        return s
    return "-".join(list(s))


# ================================
#  HTML → PNG RENDER
# ================================
def render_html_to_png(html_output, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1080})
        page.set_content(html_output, wait_until="networkidle")
        page.screenshot(path=output_path)
        browser.close()


# ================================
#   TELEGRAM POSTER
# ================================
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


# ================================
#   TWITTER CLIENTS
# ================================
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


# ================================
#   POST TWEET WITH IMAGE
# ================================
def post_to_x(image_path, tweet_text):
    media_api = create_media_api()
    media = media_api.media_upload(image_path)
    media_id = media.media_id_string

    client = create_v2_client()
    client.create_tweet(
        text=tweet_text,
        media_ids=[media_id]
    )
    print("Tweet posted successfully.")


# ================================
#  LLM TWEET GENERATOR
# ================================
def generate_llm_tweet(fixture_string, teamA, teamB, league):
    prompt = f"""
You are generating a Twitter/X post (<160 chars) for a football stat sheet.

Fixture: {fixture_string}
Teams: {teamA}, {teamB}
League: {league}

Output MUST follow this 3-line format:
1. The fixture exactly.
2. ONE fun stat only.
3. Join us on Telegram. (Link in bio)
4. Hashtags: #DataPitch + team hashtags + league hashtag + relevant catchy hashtags.

Rules:
- Max 160 chars total.
- Hashtags must be short, correct, impression generating & relevant.
- Add catchy emojis.
- No markdown.
- No unnecessary text.
- Fun stat must be 1 short line, and something cool from the data I shared. Not generic.
- Few examples of fun stats
1- Arsenal to have 4 or more offsides. 
2- Tierney to draw 3 or more fouls.
3- Westham to have 8 or more corners.
4- More than 30% probability of a red card.

Return ONLY the final tweet text.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a precise football analyst that crafts short tweets."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )

    tweet = response["choices"][0]["message"]["content"].strip()
    return tweet


# ================================
#  MAIN WORKFLOW
# ================================
def process_fixture(fixture_id, db_cursor):

    print(f"\n=== Processing Fixture {fixture_id} ===")

    # ========================
    # Fetch all stats
    # ========================
    ref = get_ref_info(db_cursor, fixture_id)
    fix = get_fix_assets(db_cursor, fixture_id)

    foulers = get_top_foulers(db_cursor, fixture_id, limit=5)
    drawers = get_top_foul_drawers(db_cursor, fixture_id, limit=5)
    shots = get_top_shooters(db_cursor, fixture_id, limit=5)
    yellows = get_top_yellows(db_cursor, fixture_id, limit=3)

    for p in foulers + drawers + shots + yellows:
        pid = p.get("player_id")
        if pid:
            p["photo"] = f"https://media.api-sports.io/football/players/{pid}.png"
        p["metric"] = format_last5(p.get("metric"))

    fixt = fix.get("fixt") or ""
    if " vs " in fixt:
        home_name, away_name = [s.strip() for s in fixt.split(" vs ", 1)]
    else:
        home_name, away_name = fixt, ""

    # ========================
    # Prepare template data
    # ========================
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

    # ========================
    # Render → PNG
    # ========================
    html_output = template.render(**data)
    png_path = os.path.join(ASSETS_DIR, f"{fixture_id}.png")
    render_html_to_png(html_output, png_path)
    print(f"PNG generated: {png_path}")

    # ========================
    # Send to Telegram
    # ========================
    send_png_to_telegram(png_path, TELEGRAM_CHANNELS)

    # ========================
    # Generate Tweet (LLM)
    # ========================
    tweet_text = generate_llm_tweet(
        fixture_string=fixt,
        teamA=home_name,
        teamB=away_name,
        league=fix.get("league_name", "")
    )

    print("Generated Tweet:", tweet_text)

    # ========================
    # Post to X/Twitter
    # ========================
    post_to_x(png_path, tweet_text)


# ================================
#  ENTRY POINT
# ================================
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
