import mysql.connector
import os

def sql_script_runner(sql_script_path, db_config):
    try:
        # Read SQL statements from the script file
        with open(sql_script_path, 'r') as sql_file:
            sql_script = sql_file.read()

        # Split the script into individual SQL statements
        sql_statements = [statement.strip() for statement in sql_script.split(';') if statement.strip()]

        # Initialize database connection
        db_conn = mysql.connector.connect(**db_config)
        cursor = db_conn.cursor()

        # Execute each SQL statement
        for sql in sql_statements:
            cursor.execute(sql)

        db_conn.commit()
        cursor.close()
        db_conn.close()
        print(f"SQL script '{sql_script_path}' executed successfully.")
    except Exception as e:
        print(f"Error executing SQL script '{sql_script_path}': {str(e)}")

