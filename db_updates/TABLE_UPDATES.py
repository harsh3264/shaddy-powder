import mysql.connector
import sqlparse
import os
import sys
import re
import datetime

def TABLE_UPDATES(script_name, db_config):
    try:
        # Initialize the MySQL connection and cursor
        db_conn = mysql.connector.connect(**db_config)
        cursor = db_conn.cursor()
        
        default_db_name = 'base_data_apis'

        # Read SQL statements from the script
        with open(script_name, 'r') as sql_file:
            sql_script = sql_file.read()

        # Split the script into separate statements
        sql_statements = sqlparse.split(sql_script)

        # Get the current datetime in the desired format
        current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:00:00')

        for statement in sql_statements:
            # Check if the statement is not a commented line
            if not statement.strip().startswith('--') and not statement.strip().startswith('#'):
                # Check for "CREATE TABLE" statements
                create_table_match = re.search(r'(CREATE TABLE|TRUNCATE)( IF NOT EXISTS)? ((`?\w+`?\.)?`?(\w+)`?)', statement, re.IGNORECASE)
                if create_table_match:
                    full_table_name = create_table_match.group(3)
                    table_name = create_table_match.group(5) if create_table_match.group(5) else full_table_name

                    # Extract the database name if specified
                    database_name_match = re.search(r'`?(\w+)`?\.', full_table_name)
                    database_name = database_name_match.group(1) if database_name_match else default_db_name

                    # Insert a record into TABLE_UPDATES
                    cursor.execute("INSERT INTO TABLE_UPDATES (LOAD_DATETIME, DB_NAME, TABLE_NAME, NUM_ROWS) "
                                   "VALUES (%s, %s, %s, 0) "
                                   "ON DUPLICATE KEY UPDATE TABLE_NAME=TABLE_NAME", (current_datetime, database_name, table_name))

                    # Commit the changes immediately
                    db_conn.commit()

                    if create_table_match:
                        # Execute the SQL statement to update the table if it's a "CREATE TABLE" or "TRUNCATE TABLE" statement
                        cursor.execute(f"UPDATE TABLE_UPDATES SET NUM_ROWS = (SELECT COUNT(*) FROM {full_table_name}) "
                                       "WHERE LOAD_DATETIME = %s "
                                       "AND TABLE_NAME = %s "
                                       "AND DB_NAME = %s", (current_datetime, table_name, database_name))
                        db_conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        # Close the cursor and the database connection
        cursor.close()
        db_conn.close()
