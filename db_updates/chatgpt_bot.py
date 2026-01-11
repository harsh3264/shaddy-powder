# SELECT fixture_id FROM temp.tele_fixtures WHERE fixture_id = 1490806 GROUP BY 1;

import os
import sys
import requests
import mysql.connector
import time
from openai import OpenAI
import html  # For safe escaping

# Add parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import modules
from sql_script_runner import sql_script_runner
from python_api.get_secrets import db_parameters, foul_bot, gold_channel, gpt_key
from python_api.gpt_prompts import yc_foul_prompt

# Initialize OpenAI client
client = OpenAI(api_key=gpt_key)

# DB config
db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'
}

# Telegram
TOKEN = foul_bot
CHAT_ID = -1002262437072


# ---------- GPT FUNCTION ----------
def get_chatgpt_response(prompt):
    retries = 3
    delay = 5

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-5.1",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a concise football betting analyst. Keep responses short and sharp."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"GPT API Error attempt {attempt+1}: {e}")
            time.sleep(delay)
            delay *= 2

    return None


# ---------- TELEGRAM SINGLE MESSAGE SENDER ----------
def send_telegram_message(chat_id, text):
    # Escape HTML entirely → safe plain text
    safe_text = html.escape(text)

    # Replace line breaks with actual newline characters
    safe_text = safe_text.replace("\\n", "\n")

    # Ensure message fits Telegram's 4096 char limit
    if len(safe_text) > 4000:
        safe_text = safe_text[:4000] + "\n...\n[Message truncated]"

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": safe_text,    # plain text only
        "parse_mode": None    # no HTML or Markdown
    }

    response = requests.post(url, data=payload)

    if response.status_code != 200:
        print("Telegram Error:", response.json())
    else:
        print("Message sent successfully.")


# ---------- DB CONNECTION ----------
try:
    db_conn = mysql.connector.connect(**db_config)
    cursor = db_conn.cursor(dictionary=True)
except Exception as err:
    print("DB Error:", err)
    sys.exit(1)


# Fetch fixture_id
cursor.execute("SELECT fixture_id FROM temp.tele_fixtures WHERE fixture_id = 1490806 GROUP BY 1;")
fixture_ids = [row["fixture_id"] for row in cursor.fetchall()]


# ---------- MAIN LOOP ----------
for fixture_id in fixture_ids:
    print(f"\nProcessing fixture_id: {fixture_id}")

    queries = {
        "referee": f"SELECT * FROM temp.referee_q WHERE fixture_id = {fixture_id};",
        "team": f"SELECT * FROM temp.team_q WHERE fixture_id = {fixture_id};",
        "player": f"SELECT * FROM temp.player_q WHERE fixture_id = {fixture_id};",
        "fouls_committed": f"SELECT * FROM temp.ffh_data_analytics WHERE fixture_id = {fixture_id};",
        "fouls_drawn": f"SELECT * FROM temp.raw_fld WHERE fixture_id = {fixture_id};"
    }

    data = {}
    for key, q in queries.items():
        cursor.execute(q)
        data[key] = cursor.fetchall()

    # Short, crisp output prompt
    prompt = f"""
Give a short, sharp football analytics prediction.

FORMAT STRICTLY LIKE THIS:

DATA:
Referee: {data["referee"]}
Teams: {data["team"]}
Players: {data["player"]}
Fouls Committed: {data["fouls_committed"]}
Fouls Drawn: {data["fouls_drawn"]}

FH FOUL RANGE: X–Y
FH CARD LIKELIHOOD: High / Medium / Low

Guidelines:
{yc_foul_prompt}
"""

    output = get_chatgpt_response(prompt)

    if not output:
        print("No GPT output.")
        continue

    send_telegram_message(CHAT_ID, output)


cursor.close()
db_conn.close()
