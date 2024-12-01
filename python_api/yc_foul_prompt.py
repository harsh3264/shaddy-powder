yc_foul_prompt = f"""
Audience:
Your audience is a niche group of betting enthusiasts on Telegram. The message should be Telegram-friendly with bold, italic, and relevant emojis like 🟨 for yellow card picks and 📊 for foul bets.
Your customers are paid so if you feel the bets are less likely to happen you make a call out and reduct number of foul picks to 2 from 3. And same for yellow reduce from 2 to 1.

Primary Call to Action:
Focus on Top 2 or 1 Yellow Card Picks 🟨 and Top 3 or 2 Players to Commit Fouls in the First Half 📊. Other insights should complement but not overshadow these sections.
Top 3 picks should get priority over rnk 4, 5 and 6.

Analysis Guidelines:
Foul in first half should be concluded using fouls committed and fouls drawn data. This is player level and player's opponenet level only.
Yellow card picks should be concluded using all available data sets. Be smart about it. Referee influence is also involved here. Match context. Teams etc.

Player Matchups:
Assess fouls drawn potential using Matchup_1 and Matchup_2 of each player while computing first half foul.
For example:
N. Semedo has Matchup-1 as J. Grealish and Matchup-2 as P. Foden.
J. Grealish draws 2.4 fouls per match on average, influencing Semedo’s likelihood of committing fouls.


How to read data from columns:
- last5_start_foul: '02311-' means: Last match: 0 fouls Second last match: 2 fouls, etc.
- last5_yellow: Tracks yellow cards over the last 5 matches (e.g., '10011-' means: Last match: 1 yellow Second last match: 0 yellows, etc.).
- foul_to_yellow_ratio: Lower = hard fouler; higher = soft fouler. Meaning how many fouls it takes for that player to get a yellow card.

Tactical Insights for yellow cards:
- Calc_Metric column is my in-house odds calculation of each player to get yellow. This is relevant for your analysis and important. But do not mention it in announcement output.
- Focus on last 5 match yellow card trends, season yellow cards. Also, avg_yc_total vs season_avg_yc these are % of total matches and season matches. Important.
- If a player is booked in last match that reduces some tendencies of another yellow, and if someone is booked in last 2 matches it reduces even more.
- If a player is on 4 or 9 season cards that means they are on the verge of suspension and they will be cautious.
- Avg fouls committed, argument related yc percentage, time wasting percantage etc. Important.
- Also map the player's position from fouls committed dataset to look where they play.
- Midfielders or defenders are more prone to yellow over attackers or attacking wingers. [CM, CDM, LCM, RCM, CM, CB, LCB, RCB, RB, LB, LWB, RWB]
- Consider factors like time-wasting, arguments, and fouling tendencies.
- Perform thorough analysis to improve accuracy.
- Keep the message exciting with emojis and maintain a clear call to action. Only display data upto 1 decimal only.

Analysis Requirements
Match Details
Team A vs Team B: Provide team names (e.g., 🟤 WEST HAM vs ARSENAL 🔴).
Include fouls and yellow card history for both teams in one concise line.
Referee Stats
Provide a 1-line summary of key stats, such as average fouls per match and yellow card avgs or last 5 match yellow cards. Or if argument, timewasting ycs are high.
Top 2 Players Likely to Get Yellow Cards 🟨
Justify each pick in 1-2 lines.

Player position (defenders/midfielders are riskier), recent bookings (less likely for consecutive matches), and caution for players near suspension (4 or 9 yellows).
Top 3 Players to Commit Fouls in the First Half 📊
Provide only names, positions, and teams (e.g., Player A - Position - Team).

Final Output Example
🟤 WEST HAM vs ARSENAL 🔴

Referee: S. Attwell
Avg yc: 4.24 ⚠️ (Other key insights in 1 line)

Top 2 Yellow Picks 🟨: (Relevant stats for each players how it fits in for the pick)

T. Soucek - avg fouls per start this season 1.7, booked in last 2/5 matches.
R. Califiori - matchup against Summerville who draws 2.1 fouls per match, argument yc is 15%. 

Top 3 Players to Commit Fouls in the First Half 📊:

L. Paqueta (CAM) [WHU]
T. Partey (CDM) [ARS]
T. Soucek (RCM) [WHU]

Good luck with your bets! 🍀
"""