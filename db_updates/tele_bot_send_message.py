import os
import sys
import requests
import mysql.connector
from decimal import Decimal
import time

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import necessary modules from your project structure
from sql_script_runner import sql_script_runner
from TABLE_UPDATES import TABLE_UPDATES
from python_api.get_secrets import rapid_api_key, db_parameters, foul_bot, gold_channel

# Determine the environment (Cloud9 or EC2)
if "C9_PORT" in os.environ:
    environment_name = "Cloud9"
    user_home = os.path.expanduser("~")
    project_directory = "environment/shaddypowder"
else:
    environment_name = "EC2"
    user_home = os.path.expanduser("~")
    project_directory = "shaddy-powder"  # Adjust for EC2 directory name

# Directories for SQL scripts
script_directory = "sql_scripts"
directory_path = os.path.abspath(os.path.join(user_home, project_directory, script_directory))


db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'
}


sorted_script_files = sorted(os.listdir(directory_path))

for filename in sorted_script_files:
    if filename.startswith("in_play"):
        script_path = os.path.join(directory_path, filename)
        print(f"Running script: {script_path}")
        sql_script_runner(script_path, db_config)
        # TABLE_UPDATES(script_path, db_config)
        print(f"Finished script: {script_path}\n")

# Telegram bot configuration
TOKEN = foul_bot  # Replace with your bot token
CHAT_ID = -1002262437072

# CHAT_ID = gold_channel  # Replace with your group chat ID

# SQL query to fetch data
sql_query = '''
SELECT
    *
FROM temp.new_in_play_subs;
'''

# Database connection configuration
db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'
}

# Connect to the database
try:
    db_conn = mysql.connector.connect(**db_config)
    cursor = db_conn.cursor()
except mysql.connector.Error as err:
    print(f"Error: {err}")
    sys.exit(1)

# Execute the query and fetch results
try:
    cursor.execute(sql_query)
    result = cursor.fetchall()
    if not result:  # Check if result is empty
        print("No new data to process. Exiting...")
        sys.exit(0)  # Exit the script if no data is returned
    header_row = [column[0] for column in cursor.description]  # Get column headers
except mysql.connector.Error as err:
    print(f"SQL Error: {err}")
    sys.exit(1)

# Helper function to format foul and card stats
def format_stats(stats):
    return "-".join(stats)

# Message template
MESSAGE_TEMPLATE = (
    "🚨 Alert! New player subbed in *{match}* for *{team}*.\n"
    "Here is their data:\n"
    " "
    "- Average fouls: `{avg_fouls}`\n"
    "- Total fouls in last 5 subs: `{fouls_last5}`\n"
    "- Yellow cards in last 5 subs: `{yellow_cards}`\n"
    "- Fouls in last 5 subs while {situation}: `{fouls_situation}`\n"
    " "
    "- Current situation: *{team}* is {situation} *{score}*."
)

# Function to format and send a message
def send_message(data):
    # Determine the match situation
    score = data.get('score', 'N/A')
    team = data.get('name', 'N/A')
    
    if ">" in score:
        situation = "winning"
        fouls_situation = format_stats(data.get('last5_win_sub_foul', '00000'))
    elif "=" in score:
        situation = "drawing"
        fouls_situation = format_stats(data.get('last5_draw_sub_foul', '00000'))
    else:
        situation = "losing"
        fouls_situation = format_stats(data.get('last5_loss_sub_foul', '00000'))

    # Format foul and yellow card stats
    fouls_last5 = format_stats(data['last5_sub_foul'])
    yellow_cards = format_stats(data['last5_sub_yc'])
    avg_fouls = round(data['avg_fouls_total'], 2)

    # Format the message
    message = MESSAGE_TEMPLATE.format(
        match=data.get('fixt', 'N/A'),
        team=team,
        score=score,
        situation=situation,
        fouls_situation=fouls_situation,
        fouls_last5=fouls_last5,
        avg_fouls=avg_fouls,
        yellow_cards=yellow_cards
    )

    # Telegram API URL
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    # Payload for Telegram API
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"  # Enable Markdown formatting
    }

    # Send the message
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print(f"Message sent: {message}")
        else:
            print(f"Failed to send message. Response: {response.json()}")
    except Exception as e:
        print(f"Error sending message: {e}")

# Iterate through query results and send messages
for row in result:
    # Map row values to header names
    data = dict(zip(header_row, row))

    # Convert Decimal to float for JSON serialization if necessary
    for key, value in data.items():
        if isinstance(value, Decimal):
            data[key] = float(value)

    # Send the message
    send_message(data)

    # Throttle to avoid hitting Telegram API rate limits
    time.sleep(0.2)  # 100ms delay between messages

# Close the database connection
cursor.close()
db_conn.close()