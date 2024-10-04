import sys
import os
import subprocess

# Other necessary imports

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

import os

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
script_directory = "database"
script_name = "live_fixtures.py"

# Construct the absolute path
live_fixtures_script_path = os.path.abspath(os.path.join(user_home, project_directory, script_directory, script_name))



# Specify the relative path to 'live_fixtures.py' from the current directory
# live_fixtures_script_path = '/home/ec2-user/environment/shaddypowder/database/live_fixtures.py'

# Run the live_fixtures script using exec
with open(live_fixtures_script_path) as f:
    code = compile(f.read(), live_fixtures_script_path, 'exec')
    exec(code)

# Import the load_fixture_stats function from fixture_stats module
from database.live_fixture_stats import load_fixture_stats
from database.live_fixture_events import load_fixture_events
from database.live_fixture_lineups import load_fixture_lineups
from database.live_fixture_player_stats import load_fixture_player_stats

# Modify the query dynamically
query = '''
    SELECT DISTINCT fixture_id
    FROM live_updates.live_fixtures f
    WHERE
        (
            DAYOFWEEK(FROM_UNIXTIME(f.timestamp)) = 7  -- Saturday
            AND f.timestamp = 1727532000  -- 3 PM kickoff for PL matches
            AND f.league_id = 39  -- Only focus on Premier League matches
        )
        OR
        (
            -- For other days, or if it is Saturday but outside the restricted time
            DAYOFWEEK(FROM_UNIXTIME(f.timestamp)) != 7  -- For other days, no restrictions
            OR
            (
                DAYOFWEEK(FROM_UNIXTIME(f.timestamp)) = 7
                AND (
                    TIME(FROM_UNIXTIME(f.timestamp)) NOT BETWEEN '13:20:00' AND '14:10:00'  -- Exclude other leagues in this time
                )
            )
        )
    ;
'''
    
# Call the function to update fixture stats and store the fixture IDs
load_fixture_stats(query)

# Call the function to update fixture events and pass the fixture IDs
load_fixture_events(query)

# Call the function to update fixture lineups and pass the fixture IDs
load_fixture_lineups(query)

# Call the function to update fixture player stats and pass the fixture IDs
load_fixture_player_stats(query)
