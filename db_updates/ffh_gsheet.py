import os
import gspread
import boto3
import sys
from apiclient import discovery
import mysql.connector
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle
from decimal import Decimal
from datetime import date
import pandas as pd

# Check if the script is running on Cloud9 (you might need to adjust this check based on your specific environment)
if "C9_PORT" in os.environ:
    # Your Cloud9 environment
    environment_name = "Cloud9"
    user_home = os.path.expanduser("~")
    project_directory = "environment/shaddypowder"
else:
    # Your EC2 environment
    environment_name = "EC2"
    user_home = os.path.expanduser("~")
    project_directory = "shaddy-powder"  # Adjust this to the EC2 directory name

# Common directory structure
script_directory = "python_api"

# Construct the absolute path
script_path = os.path.abspath(os.path.join(user_home, project_directory, script_directory))

# Your S3 bucket and object key
s3_bucket_name = 'sp-gsheet'
s3_object_key = 'sp-ac-gsheet.json'

# Local path to save the downloaded JSON file
local_json_path = os.path.join(script_path, 'secrets', 'gsheet.json')

# Ensure the directory exists before attempting to download
os.makedirs(os.path.dirname(local_json_path), exist_ok=True)

# Download the JSON file from S3
s3 = boto3.client('s3')
s3.download_file(s3_bucket_name, s3_object_key, local_json_path)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import db_parameters


# SQL statements to execute
sql_statements = [
    '''
    SELECT
    CONCAT(fixt, rnk) AS vlk,
    base1.*
    FROM temp.raw_ffh AS base1;
    ''',
    '''
    SELECT 
    CONCAT(fixt, rnk) AS vlk,
    base2.*
    FROM temp.raw_sfh AS base2;
    ''',
    '''
    SELECT 
    CONCAT(fixt, rnk) AS vlk,
    base3.*
    FROM temp.raw_fld AS base3;
    ''',
    '''
    SELECT * 
    FROM temp.referee_q;
    ''',
    '''
    SELECT * FROM temp.player_q;
    ''',
    '''
    SELECT * FROM temp.csv_upload;
    '''
]

# MySQL connection
db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'
}
db_conn = mysql.connector.connect(**db_config)
cursor = db_conn.cursor()

# ...

# Google Sheets
for i, sql in enumerate(sql_statements):
    sheet_name = ["raw_ffh", "raw_sfh", "raw_fld", "raw_tf", "raw_pq", "csv_format"][i]
    
    cursor.execute(sql)
    result = cursor.fetchall()

    # Convert Decimal values to float for JSON serialization
    rows = []
    header_row = [column[0] for column in cursor.description]  # Extract header from cursor description

    for row in result:
        row_values = []
        for value in row:
            if isinstance(value, Decimal):
                row_values.append(float(value))
            elif isinstance(value, date):
                row_values.append(value.strftime('%Y-%m-%d'))
            elif isinstance(value, pd.Timestamp):
                row_values.append(str(value))
            else:
                row_values.append(value)
        rows.append(row_values)

    # Use service account credentials
    creds = service_account.Credentials.from_service_account_file(local_json_path)

    # Build Sheets API service
    service = discovery.build('sheets', 'v4', credentials=creds)

    # Spreadsheet ID and range
    spreadsheet_id = '1FFoDXRwJYVrYITLxCE-ODJxsostJM5UOFHixIctyg5M'
    range_name = f'{sheet_name}!A1'  # Adjust the range based on your data

    # Prepare the values to update
    values = [header_row] + rows  # Include header row

    # Prepare the update data
    data = {
        'values': values,
    }

    # Clear the existing sheet
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=sheet_name,
    ).execute()

    # Perform the update
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        body=data,
        range=range_name,
        valueInputOption='RAW',  # Use 'RAW' for non-formatted values
    ).execute()

# Close MySQL connection
cursor.close()
db_conn.close()

# Delete the JSON file after use
os.remove(local_json_path)