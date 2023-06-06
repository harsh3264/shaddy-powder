# Shaddy Powder

Shaddy Powder is a project focused on building a data-driven application for analyzing sports data, with a specific focus on football matches. 
Our goal is to identify data-driven betting opportunities in ongoing and upcoming matches, providing valuable insights for informed betting decisions. 
We aim to enhance the betting experience by leveraging data analytics and statistical analysis. 

"Betting but better!" (18+ Gamble Responsibly)


## Project Structure

The project is organized into the following folders:

- `database`: Contains scripts and configurations related to the database setup and management.
- `python_api`: Includes Python scripts for fetching data from APIs and processing it.
- `.retro_python_scripts`: Hidden folder containing previous versions of Python scripts and sensitive API credentials.

## Data Sources

We utilize the following data sources for our analysis:

- Rapid APIs: We make use of Rapid APIs, specifically the API-Football service, to fetch real-time sports data, including fixture details, player information, and fixture events. Our subscription includes the paid version with 7500 API calls per day.

## Python Scripts

We have implemented several Python scripts for different functionalities:

- `fetch_fixture_events.py`: Fetches fixture events from Rapid APIs and stores them in the database.
- `fetch_players_info.py`: Retrieves player information from Rapid APIs based on player IDs and season years.

## Database Tables

We have designed the following tables to store our data:

- `leagues`: Stores information about different leagues.
- `fixtures`: Contains details about fixtures, including fixture IDs, dates, and league associations.
- `fixture_stats`: Stores statistical information for each fixture.
- `fixture_lineups`: Holds lineup information for fixtures.
- `fixture_coach`: Stores coach information for fixtures.
- `fixture_player_stats`: Stores player statistics for fixtures.
- `fixture_events`: Stores detailed information about events that occur during fixtures.
- `players`: Stores player information, including player IDs, names, nationality, age, height, weight, and photos.

## Getting Started

To get started with the project, follow these steps:

1. Set up the database: Execute the necessary SQL scripts in the `database` folder to create the required tables and configure the database connection.

2. Configure API credentials: Obtain the necessary API credentials from Rapid APIs and update the corresponding variables in the Python scripts.

3. Run the Python scripts: Execute the Python scripts in the `python_api` folder to fetch data from the APIs and store it in the database.

4. Analyze the data: Utilize the data stored in the database for further analysis, insights, and identifying betting opportunities.

## Roadmap

Our future plan for Shaddy Powder includes the following milestones:
1. Developing the backend architecture for the web application.
2. Implementing data processing and analysis algorithms to generate betting tips and predictions.
3. Designing an intuitive user interface for easy navigation and accessing betting insights.
4. Incorporating real-time match updates and live betting features to provide the latest information to users.
5. Enhancing the application with additional sports data analysis capabilities beyond football.

## Contributing

Contributions to Shaddy Powder are welcome! If you have any ideas, suggestions, or improvements, feel free to submit a pull request or open an issue.

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer

Please note that betting and gambling involve financial risk, and it's important to gamble responsibly. Shaddy Powder does not guarantee the accuracy of the provided data, predictions, or betting recommendations. Users should make informed decisions and exercise caution while engaging in any form of betting or gambling. Users must be 18 years of age or older to use this application.

