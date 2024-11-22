import requests
import sys
import os
import mysql
# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import rapid_api_key, db_parameters, foul_bot, gold_channel

# Replace with your bot token and group chat ID
TOKEN = foul_bot
CHAT_ID = gold_channel
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

response = requests.get(url)
print(response.json())
