import sys
import os
import subprocess

# Other necessary imports

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)


# Specify the relative path to 'live_fixtures.py' from the current directory
live_fixtures_script_path = '/home/ec2-user/environment/shaddypowder/database/live_fixtures.py'

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
    SELECT DISTINCT f.fixture_id
    FROM live_updates.live_fixtures f
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
