USE base_data_apis;

# DROP TABLE IF EXISTS countries;

CREATE TABLE countries (
    id INT AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(2),
    flag VARCHAR(255),
    PRIMARY KEY (id)
);

# DROP TABLE IF EXISTS leagues;

CREATE TABLE leagues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    league_id INT,
    season_year INT,
    name VARCHAR(255),
    type VARCHAR(255),
    logo VARCHAR(255),
    country_name VARCHAR(255),
    country_code VARCHAR(255),
    country_flag VARCHAR(255),
    season_start DATE,
    season_end DATE,
    season_coverage_fixtures_events BOOLEAN,
    season_coverage_fixtures_lineups BOOLEAN,
    season_coverage_fixtures_statistics_fixtures BOOLEAN,
    season_coverage_fixtures_statistics_players BOOLEAN,
    season_coverage_standings BOOLEAN,
    season_coverage_players BOOLEAN,
    season_coverage_top_scorers BOOLEAN,
    season_coverage_top_assists BOOLEAN,
    season_coverage_top_cards BOOLEAN,
    season_coverage_injuries BOOLEAN,
    season_coverage_predictions BOOLEAN,
    season_coverage_odds BOOLEAN,
    UNIQUE KEY league_season_unique (league_id, season_year, season_start)
);

# DROP TABLE IF EXISTS teams;

CREATE TABLE teams (
    team_id INT PRIMARY KEY,
    name VARCHAR(255),
    country VARCHAR(255),
    logo VARCHAR(255),
    founded INT,
    national BOOLEAN,
    venue_id INT,
    venue_name VARCHAR(255),
    venue_address VARCHAR(255),
    venue_city VARCHAR(255),
    venue_capacity INT,
    venue_surface VARCHAR(255),
    venue_image VARCHAR(255)
);

# DROP TABLE IF EXISTS team_stats;

CREATE TABLE team_stats (
      team_id INTEGER,
      league_id INTEGER,
      season_year INTEGER,
      form TEXT,
      played_home INTEGER,
      played_away INTEGER,
      played_total INTEGER,
      wins_home INTEGER,
      wins_away INTEGER,
      wins_total INTEGER,
      draws_home INTEGER,
      draws_away INTEGER,
      draws_total INTEGER,
      loses_home INTEGER,
      loses_away INTEGER,
      loses_total INTEGER,
      goals_for_home INTEGER,
      goals_for_away INTEGER,
      goals_for_total INTEGER,
      goals_against_home INTEGER,
      goals_against_away INTEGER,
      goals_against_total INTEGER,
      biggest_wins_home varchar(5),
      biggest_wins_away varchar(5),
      biggest_loses_home varchar(5),
      biggest_loses_away varchar(5),
      penalty_scored INTEGER,
      penalty_missed INTEGER,
      clean_sheet_home INTEGER,
      clean_sheet_away INTEGER,
      clean_sheet_total INTEGER,
      failed_to_score_home INTEGER,
      failed_to_score_away INTEGER,
      failed_to_score_total INTEGER,
      yellow_cards_total INTEGER,
      red_cards_total INTEGER,
      goals_0_15 INTEGER,
      goals_16_30 INTEGER,
      goals_31_45 INTEGER,
      goals_46_60 INTEGER,
      goals_61_75 INTEGER,
      goals_76_90 INTEGER,
      goals_91_105 INTEGER,
      goals_106_120 INTEGER,
      yellow_cards_0_15 INTEGER,
      yellow_cards_16_30 INTEGER,
      yellow_cards_31_45 INTEGER,
      yellow_cards_46_60 INTEGER,
      yellow_cards_61_75 INTEGER,
      yellow_cards_76_90 INTEGER,
      yellow_cards_91_105 INTEGER,
      yellow_cards_106_120 INTEGER,
      red_cards_0_15 INTEGER,
      red_cards_16_30 INTEGER,
      red_cards_31_45 INTEGER,
      red_cards_46_60 INTEGER,
      red_cards_61_75 INTEGER,
      red_cards_76_90 INTEGER,
      red_cards_91_105 INTEGER,
      red_cards_106_120 INTEGER,
      PRIMARY KEY (team_id, league_id, season_year),
      FOREIGN KEY (team_id) REFERENCES teams (team_id),
     FOREIGN KEY (league_id) REFERENCES leagues (league_id)
);

# DROP TABLE IF EXISTS team_league_season;

CREATE TABLE team_league_season (
    team_id INT,
    league_id INT,
    season_year INT,
    team_code VARCHAR(4),
    UNIQUE KEY team_league_season_unique (team_id, league_id, season_year)
);

# DROP TABLE IF EXISTS fixtures;

CREATE TABLE fixtures (
  `fixture_id` int NOT NULL,
  `referee` varchar(255) DEFAULT NULL,
  `fixture_date` date DEFAULT NULL,
  `venue_id` int DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  `elapsed` int DEFAULT NULL,
  `season_year` int DEFAULT NULL,
  `home_team_id` int DEFAULT NULL,
  `away_team_id` int DEFAULT NULL,
  `league_id` int DEFAULT NULL,
  `league_round` varchar(255) DEFAULT NULL,
  `total_home_goals` int DEFAULT NULL,
  `ht_home_goals` int DEFAULT NULL,
  `ft_home_goals` int DEFAULT NULL,
  `et_home_goals` int DEFAULT NULL,
  `total_away_goals` int DEFAULT NULL,
  `pt_home_goals` int DEFAULT NULL,
  `ht_away_goals` int DEFAULT NULL,
  `ft_away_goals` int DEFAULT NULL,
  `et_away_goals` int DEFAULT NULL,
  `pt_away_goals` int DEFAULT NULL,
  PRIMARY KEY (`fixture_id`),
  FOREIGN KEY (league_id, season_year) REFERENCES leagues(league_id, season_year)
);

UPDATE fixtures
SET ht_home_goals = total_home_goals
WHERE ht_home_goals > total_home_goals;

UPDATE fixtures
SET ht_away_goals = total_away_goals
WHERE ht_away_goals > total_away_goals;

# DROP TABLE IF EXISTS fixtures_stats;

CREATE TABLE IF NOT EXISTS fixtures_stats (
        fixture_id INT,
        team_id INT,
        team_name varchar(60),
        against_team_id INT,
        against_team_name varchar(60),
        is_home INT,
        shots_on_goal INT,
        shots_off_goal INT,
        total_shots INT,
        blocked_shots INT,
        shots_inside_box INT,
        shots_outside_box INT,
        fouls INT,
        corner_kicks INT,
        offsides INT,
        ball_possession INT,
        yellow_cards INT,
        red_cards INT,
        goalkeeper_saves INT,
        total_passes INT,
        passes_accurate INT,
        passes_percentage INT,
        against_shots_on_goal INT,
        against_shots_off_goal INT,
        against_total_shots INT,
        against_blocked_shots INT,
        against_shots_inside_box INT,
        against_shots_outside_box INT,
        against_fouls INT,
        against_corner_kicks INT,
        against_offsides INT,
        against_ball_possession INT,
        against_yellow_cards INT,
        against_red_cards INT,
        against_goalkeeper_saves INT,
        against_total_passes INT,
        against_passes_accurate INT,
        against_passes_percentage INT,
        expected_goals FLOAT,
        against_expected_goals FLOAT,
        PRIMARY KEY (fixture_id, is_home)
    );

# DROP TABLE IF EXISTS fixture_coach;

CREATE TABLE fixture_coach (
    fixture_id INT,
    team_id INT,
    is_home BOOLEAN,
    coach_id INT,
    coach_name VARCHAR(255),
    photo VARCHAR(255),
    formation VARCHAR(255),
    primary key (fixture_id, team_id)
);

# DROP TABLE IF EXISTS fixture_lineups;

CREATE TABLE fixture_lineups (
    fixture_id INT,
    team_id INT,
    player_id INT,
    player_number INT,
    player_pos VARCHAR(255),
    grid VARCHAR(255),
    is_substitute BOOLEAN,
    PRIMARY KEY (fixture_id, player_id)
);

CREATE INDEX idx_fixture_lineups_player_fixture ON fixture_lineups (player_id, fixture_id);

# DROP TABLE IF EXISTS fixture_player_stats;

CREATE TABLE fixture_player_stats (
  player_id INT,
  fixture_id INT,
  team_id INT,
  minutes_played INT,
  rating DECIMAL(3, 1),
  captain BOOLEAN,
  offsides INT,
  shots_total INT,
  shots_on_target INT,
  goals_total INT,
  goals_conceded INT,
  assists INT,
  saves INT,
  passes_total INT,
  passes_key INT,
  passes_accuracy DECIMAL(4, 2),
  tackles_total INT,
  tackles_blocks INT,
  tackles_interceptions INT,
  duels_total INT,
  duels_won INT,
  dribbles_attempts INT,
  dribbles_success INT,
  dribbles_past INT,
  fouls_drawn INT,
  fouls_committed INT,
  cards_yellow INT,
  cards_red INT,
  penalty_won INT,
  penalty_committed INT,
  penalty_scored INT,
  penalty_missed INT,
  penalty_saved INT,
  PRIMARY KEY (player_id, fixture_id),
#   FOREIGN KEY (player_id, fixture_id) REFERENCES fixture_lineups (player_id, fixture_id),
  FOREIGN KEY (team_id) REFERENCES teams (team_id),
  FOREIGN KEY (fixture_id) REFERENCES fixtures (fixture_id)
);

# DROP TABLE IF EXISTS fixture_events;

CREATE TABLE IF NOT EXISTS fixture_events (
  event_id INT PRIMARY KEY,
  fixture_id INT,
  team_id INT,
  player_id INT,
  type VARCHAR(50),
  detail VARCHAR(50),
  comments VARCHAR(100),
  minute INT,
  extra_minute INT,
  result VARCHAR(50),
  assist_id INT,
#   assist_name VARCHAR(50),
  FOREIGN KEY (fixture_id) REFERENCES fixtures(fixture_id),
  FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

# DROP TABLE IF EXISTS players;

CREATE TABLE players (
    player_id INT PRIMARY KEY,
    name VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    nationality VARCHAR(255),
    age INT,
    height INT,
    weight INT,
    photo VARCHAR(255)
);

# DROP TABLE IF EXISTS players_sidelined

CREATE TABLE players_sidelined (
  player_id INT,
  event_type VARCHAR(255),
  start_date DATE,
  end_date DATE,
  PRIMARY KEY (player_id, event_type, start_date)
);

DROP TABLE IF EXISTS league_standings;

CREATE TABLE league_standings (
    league_id INT,
    season_year INT,
    team_id INT,
    rank_t INT,
    points INT,
    goals_diff INT,
    group_name VARCHAR(255),
    form VARCHAR(255),
    status_t VARCHAR(255),
    description_t VARCHAR(255),
    played INT,
    win INT,
    draw INT,
    lose INT,
    goals_for INT,
    goals_against INT,
    home_played INT,
    home_win INT,
    home_draw INT,
    home_lose INT,
    home_goals_for INT,
    home_goals_against INT,
    away_played INT,
    away_win INT,
    away_draw INT,
    away_lose INT,
    away_goals_for INT,
    away_goals_against INT,
    last_update DATETIME,
    PRIMARY KEY (league_id, season_year, team_id)
);


DROP TABLE IF EXISTS injuries;

CREATE TABLE injuries (
  player_id INT,
  fixture_id INT,
  league_id INT,
  team_id INT,
  type VARCHAR(255),
  reason TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (player_id, fixture_id)
);