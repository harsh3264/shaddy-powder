# Shaddy Powder

Shaddy Powder is a project focused on building a data-driven application for analyzing sports data, with a specific focus on football matches. Our goal is to identify data-driven betting opportunities in ongoing and upcoming matches, providing valuable insights for informed betting decisions. We aim to enhance the betting experience by leveraging data analytics and statistical analysis.

"Betting but better!" (18+ Gamble Responsibly)

## Project Structure

The project is organized into the following folders:

- `database`: Contains scripts and configurations related to the database setup and management.
- `python_api`: Includes Python scripts for fetching data from APIs and processing it.
- `.retro_python_scripts`: Hidden folder containing previous versions of Python scripts and sensitive API credentials.
- `db_updates`: Contains scripts for updating existing data tables.

## Data Sources

We utilize the following data sources for our analysis:

- Rapid APIs: We make use of Rapid APIs, specifically the API-Football service, to fetch real-time sports data, including fixture details, player information, and fixture events. Our subscription includes the paid version with 7500 API calls per day.

## Database

We have set up a MySQL database using Amazon RDS within our AWS account. The database configuration details are as follows:

- Database Engine: MySQL (RDS)
- AWS Account: Shaddy Powder
- AWS Cloud9: We are utilizing AWS Cloud9 as our development environment for backend design and implementation.

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
- `league_standings`: Stores league standings for each season and league.
- `players_sidelined`: Stores information about players who are sidelined or injured.

## Project Management Steps

To achieve our goal of having the project up and running, we are following the following steps:

1. Backend Creation: Develop the backend architecture for the application, including the database building and setup. (Timeline: Started on 4th June, to be completed by 20th June)

2. Analysis and Data Modeling: Perform in-depth analysis of sports data, develop data models, and design algorithms for generating betting tips and predictions. (Timeline: 21st June - 30th June)

3. UI Design: Create an intuitive and visually appealing user interface for the web application, incorporating data visualizations and easy navigation. (Timeline: 1st July - 10th July)

4. Integration and Testing: Integrate the backend with the UI, perform thorough testing to ensure the functionality and accuracy of the application. (Timeline: 11th July - 14th July)

5. Deployment: Deploy the application to a suitable hosting environment and make it accessible to users. (Timeline: 15th July)

Please note that these timelines are approximate and subject to change based on project requirements and progress.

## Contributing

Contributions to Shaddy Powder are welcome! If you have any ideas, suggestions, or improvements, feel free to submit a pull request or open an issue.

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer

Please note that betting and gambling involve financial risk, and it's important to gamble responsibly. Shaddy Powder does not guarantee the accuracy of the provided data, predictions, or betting recommendations. Users should make informed decisions and exercise caution while engaging in any form of betting or gambling. Users must be 18 years of age or older to use this application.
