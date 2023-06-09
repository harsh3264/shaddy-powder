import pandas as pd
import mysql.connector
import sys
import os

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import db_parameters

def calculate_probability():
    # MySQL database configuration
    db_config = {
        'user': db_parameters['username'],
        'password': db_parameters['password'],
        'host': db_parameters['host'],
        'database': 'base_data_apis'
    }

    # Connect to MySQL database
    conn = mysql.connector.connect(**db_config)

    # SQL query to retrieve the data from the database table
    sql = """
       SELECT * FROM team_level_dataset
    """

    # Assuming you have retrieved the data from the database and stored it in a dataframe named "data"
    data = pd.read_sql(sql, conn)

    # Get unique teams from the data
    teams = data['team_name'].unique()
    
    # print(teams)

    # Define the columns (metrics) for which you want to generate thresholds
    columns = data.columns[6:]  # Assuming the metric columns start from column number 6
    
    # print(columns)

    # Create a results table to store the probabilities
    results_table = pd.DataFrame(columns=['team_name', 'metric', 'scenario', 'threshold', 'probability'])

    # Calculate the thresholds and probabilities for each team, metric, and scenario
    for team in teams:
        for column in columns:
            for scenario in ['overall', 'home', 'away']:
                team_data = data[(data['team_name'] == team) & (data['is_home'] == (1 if scenario == 'home' else 0))][column]
                percentile = 10  # Adjust the percentile value based on your requirements
                threshold = team_data.quantile(percentile / 100)
                matches_with_threshold = data[(data[column] >= threshold) & (data['team_name'] == team) & (data['is_home'] == (1 if scenario == 'home' else 0))]
                total_matches = len(data[(data['team_name'] == team) & (data['is_home'] == (1 if scenario == 'home' else 0))])
                matches_meeting_threshold = len(matches_with_threshold)
                 # Calculate probability only if total_matches is non-zero
                if total_matches > 0:
                    probability = matches_meeting_threshold / total_matches
                else:
                    probability = 0 

                # Store the results in the results table
                results_table = results_table.append({
                    'team_name': team,
                    'metric': column,
                    'scenario': scenario,
                    'threshold': threshold,
                    'probability': probability
                }, ignore_index=True)
                
                # Handle NaN values in the results_table DataFrame
                results_table = results_table.fillna('')

    # Insert the results into the database table
    cursor = conn.cursor()
    insert_query = "INSERT INTO probability_results (team_name, metric, scenario, threshold, probability) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE threshold = VALUES(threshold), probability = VALUES(probability)"
    for _, row in results_table.iterrows():
        cursor.execute(insert_query, (row['team_name'], row['metric'], row['scenario'], row['threshold'], row['probability']))

    # Commit the changes and close the database connection
    conn.commit()
    cursor.close()
    conn.close()

# Call the function to calculate the probability and store the results in the database
calculate_probability()
