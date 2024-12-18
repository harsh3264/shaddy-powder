import os
import sys
import requests
import mysql.connector
import time
import openai

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import necessary modules from your project structure
from sql_script_runner import sql_script_runner
from python_api.get_secrets import db_parameters, foul_bot, gold_channel, gpt_key
from python_api.gpt_prompts import train_prompt

# OpenAI API setup
openai.api_key = gpt_key

# Determine the environment (Cloud9 or EC2)
if "C9_PORT" in os.environ:
    environment_name = "Cloud9"
    user_home = os.path.expanduser("~")
    project_directory = "environment/shaddypowder"
else:
    environment_name = "EC2"
    user_home = os.path.expanduser("~")
    project_directory = "shaddy-powder"

# Database connection config
db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'
}

# Telegram bot configuration
TOKEN = foul_bot  # Replace with your bot token
CHAT_ID = -1002262437072  # Replace with your group chat ID

# Connect to the database
try:
    db_conn = mysql.connector.connect(**db_config)
    cursor = db_conn.cursor(dictionary=True)  # Dictionary cursor for column-value pairs
except mysql.connector.Error as err:
    print(f"Error: {err}")
    sys.exit(1)

# Fetch all fixture_ids for the current date
try:
    fixture_ids_query = "SELECT fixture_id FROM temp.new_tele_fixtures;"
    cursor.execute(fixture_ids_query)
    fixture_ids = [row["fixture_id"] for row in cursor.fetchall()]
    if not fixture_ids:
        print("No fixtures found for today.")
        sys.exit(0)
except mysql.connector.Error as err:
    print(f"SQL Error: {err}")
    sys.exit(1)

# Aggregate all team and referee data
all_team_data = []
all_referee_data = []

try:
    # Fetch team data for all fixtures
    team_query = f"SELECT * FROM temp.team_q WHERE fixture_id IN ({','.join(map(str, fixture_ids))});"
    cursor.execute(team_query)
    # print(team_query)
    all_team_data = cursor.fetchall()

    # Fetch referee data for all fixtures
    referee_query = f"SELECT * FROM temp.referee_q WHERE fixture_id IN ({','.join(map(str, fixture_ids))});"
    cursor.execute(referee_query)
    all_referee_data = cursor.fetchall()
except mysql.connector.Error as err:
    print(f"SQL Error during data aggregation: {err}")
    sys.exit(1)

# Function to call OpenAI API
def get_chatgpt_response(prompt):
    retries = 3
    delay = 5  # Initial delay in seconds

    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a shrewd football betting analyst running a paid tipster account."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response["choices"][0]["message"]["content"].strip()

        except openai.error.RateLimitError:
            print(f"Rate limit exceeded. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff

        except openai.error.ServiceUnavailableError:
            print("OpenAI service temporarily unavailable. Retrying...")
            time.sleep(delay)

        except openai.error.OpenAIError as e:
            print(f"Unexpected OpenAI API Error: {e}")
            break

    print("Failed to get a response after retries.")
    return None

# Validate data availability
if not all_team_data or not all_referee_data:
    print("Insufficient data to generate a prediction.")
    sys.exit(1)

# Create a single prompt for ChatGPT
prompt = f"""
**Input Data for All Fixtures:**
Team Data: {all_team_data if all_team_data else 'No team data available'}
Referee Data: {all_referee_data if all_referee_data else 'No referee data available'}

You are tasked with analyzing this data and identifying ONE high-confidence betting opportunity for the day as part of a £10 to £500 challenge. Provide a concise and actionable betting tip.
""" + train_prompt

# Get the prediction using ChatGPT
chatgpt_output = get_chatgpt_response(prompt)

# Validate the output
if not chatgpt_output:
    print("Failed to generate betting prediction.")
    sys.exit(1)

# Telegram API URL
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# Send the final message to Telegram
payload = {
    "chat_id": CHAT_ID,
    "text": f"{time.strftime('%d-%b-%Y')} £10 to £500 Challenge:\n\n{chatgpt_output}",
    "parse_mode": "Markdown"
}

try:
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Betting suggestion sent successfully!")
    else:
        print(f"Failed to send the message. Response: {response.json()}")
except Exception as e:
    print(f"Error sending the message to Telegram: {e}")

# Close the database connection
cursor.close()
db_conn.close()
