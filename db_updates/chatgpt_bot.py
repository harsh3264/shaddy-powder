import os
import sys
import requests
import mysql.connector
import time
import openai  # Required for ChatGPT integration

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import necessary modules from your project structure
from sql_script_runner import sql_script_runner
from python_api.get_secrets import db_parameters, foul_bot, gold_channel, gpt_key
from python_api.gpt_prompts import yc_foul_prompt  # Import the pre-defined prompt

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
CHAT_ID = gold_channel

# CHAT_ID = -1002262437072  # Replace with your group chat ID

# Connect to the database
try:
    db_conn = mysql.connector.connect(**db_config)
    cursor = db_conn.cursor(dictionary=True)  # Dictionary cursor for column-value pairs
except mysql.connector.Error as err:
    print(f"Error: {err}")
    sys.exit(1)

# Fetch all fixture_ids
fixture_ids_query = "SELECT fixture_id FROM temp.new_tele_fixtures;"
try:
    cursor.execute(fixture_ids_query)
    fixture_ids = [row["fixture_id"] for row in cursor.fetchall()]
except mysql.connector.Error as err:
    print(f"SQL Error: {err}")
    sys.exit(1)

# Iterate over each fixture_id
for fixture_id in fixture_ids:
    print(f"Processing fixture_id: {fixture_id}")
    
    # Dynamic SQL queries for the current fixture_id
    queries = {
        "referee": f"SELECT * FROM temp.referee_q WHERE fixture_id = {fixture_id};",
        "team": f"SELECT * FROM temp.team_q WHERE fixture_id = {fixture_id};",
        "player": f"SELECT * FROM temp.player_q WHERE fixture_id = {fixture_id}",
        "fouls_committed": f"SELECT * FROM temp.ffh_data_analytics WHERE fixture_id = {fixture_id};",
        "fouls_drawn": f"SELECT * FROM temp.raw_fld WHERE fixture_id = {fixture_id};"
    }

    # Fetch data for each query
    data_points = {}
    try:
        for key, query in queries.items():
            cursor.execute(query)
            data_points[key] = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"SQL Error for fixture_id {fixture_id}: {err}")
        continue  # Skip to the next fixture_id if there's an error

    # Create the prompt by appending yc_foul_prompt
    prompt = f"""
    You are a football betting analyst. Carefully analyze the following data points:

    Referee Data: {data_points["referee"]}
    Team Data: {data_points["team"]}
    Player Data: {data_points["player"]}
    Fouls Committed Data: {data_points["fouls_committed"]}
    Fouls Drawn Data: {data_points["fouls_drawn"]}
    """ + yc_foul_prompt
    
    # print(prompt)

    # Call OpenAI API with gpt-4o-mini
    def get_chatgpt_response(prompt):
        retries = 3
        delay = 5  # Initial delay in seconds

        for attempt in range(retries):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a shrewd football betting analyst. And you run your paid tipster account."},
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

    # Get the ChatGPT output
    chatgpt_output = get_chatgpt_response(prompt)

    # Check if ChatGPT output is valid
    if not chatgpt_output:
        print(f"Failed to get a response for fixture_id {fixture_id}.")
        continue  # Skip to the next fixture_id

    # Telegram API URL
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    # Send the output to Telegram
    payload = {
        "chat_id": CHAT_ID,
        "text": chatgpt_output,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print(f"Message sent successfully for fixture_id {fixture_id}")
        else:
            print(f"Failed to send message for fixture_id {fixture_id}. Response: {response.json()}")
    except Exception as e:
        print(f"Error sending message to Telegram for fixture_id {fixture_id}: {e}")

# Close the database connection
cursor.close()
db_conn.close()
