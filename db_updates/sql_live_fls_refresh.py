# Import the MySQL connector
import mysql.connector
# from mysql.connector import errorcode
import os
import sys
from sql_script_runner import sql_script_runner
from TABLE_UPDATES import TABLE_UPDATES

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import db_parameters

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
script_directory = "sql_scripts"
# script_name = "master_referee_view.sql"

# # Construct the absolute path
# sql_script_path = os.path.abspath(os.path.join(user_home, project_directory, script_directory, script_name))

# Construct the absolute path
directory_path = os.path.abspath(os.path.join(user_home, project_directory, script_directory))

db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'
}


sorted_script_files = sorted(os.listdir(directory_path))

# print(sorted_script_files)
        
for filename in sorted_script_files:
    if filename.startswith("live"):
        script_path = os.path.join(directory_path, filename)
        print(f"Running script: {script_path}")
        sql_script_runner(script_path, db_config)
        # TABLE_UPDATES(script_path, db_config)
        print(f"Finished script: {script_path}\n")
        

#Gsheet Push

gsheet_directory = "db_updates"
fouls_script_name = "live_fls_gsheet.py"

# Construct the absolute path
fouls_script_path = os.path.abspath(os.path.join(user_home, project_directory, gsheet_directory, fouls_script_name))


# Run the fixtures script using exec
with open(fouls_script_path) as f:
    code = compile(f.read(), fouls_script_path, 'exec')
    exec(code)