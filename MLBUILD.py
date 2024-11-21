import unicodedata
import pandas as pd
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamgamelog
import requests
from bs4 import BeautifulSoup
import os

class NBAPlayerLookup:
    def __init__(self, active_only=True):
        """
        Initializes the NBAPlayerLookup object.

        :param active_only: If True, only active players are considered.
        """
        self.active_only = active_only
        self.all_players = players.get_players()

    def normalize_text(self, text):
        """
        Normalize a string to remove special characters and accents.

        :param text: The input string to normalize.
        :return: A normalized string without special characters or accents.
        """
        return ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        ).lower()

    def get_player_ids(self, player_name):
        """
        Fetches the player IDs for all players matching the given name, ignoring special characters.

        :param player_name: Full name of the player (e.g., "Luka Doncic" without accents).
        :return: A list of dictionaries containing player IDs and details, or an empty list if no match is found.
        """
        normalized_input = self.normalize_text(player_name)
        matching_players = [
            p for p in self.all_players
            if self.normalize_text(p['full_name']) == normalized_input
            and (not self.active_only or p['is_active'])
        ]

        if matching_players:
            if len(matching_players) > 1:
                print(f"Warning: {len(matching_players)} players found with the name '{player_name}'.")
            return matching_players
        else:
            print(f"No players found with the name '{player_name}'.")
            return []

    def get_player_game_logs(self, player_id, szn):
        """
        Fetches the game logs for a given player using their ID.

        :param player_id: The player's unique ID.
        :return: A Pandas DataFrame containing game log data.
        """
        game_log = playergamelog.PlayerGameLog(player_id=player_id, season=szn)  # Specify the season you want
        game_log_data = game_log.get_data_frames()[0]  # Convert to Pandas DataFrame

        return game_log_data

    def calculate_rolling_stats(self, game_logs, window=5):
        """
        Calculates rolling statistics for key player stats (e.g., PTS, AST, REB) as a list of values
        from the previous n games, excluding the current game.

        :param game_logs: DataFrame of player game logs.
        :param window: The number of games for the rolling window (default is 5).
        :return: DataFrame with rolling stats, excluding the current game.
        """
        rolling_stats = game_logs.copy()

        # List of key stats to calculate rolling values for
        stats_columns = ['MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT',
                         'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'PLUS_MINUS']

        for stat in stats_columns:
            rolling_values = []  # To hold the rolling values for the stat

            for i in range(len(game_logs)):
                # Get the previous n games, excluding the current game
                previous_games = game_logs[stat].iloc[max(i-window, 0):i]  # Exclude current game, use max(i-window, 0) to avoid negative indexing
                rolling_values.append(list(previous_games))  # Append the previous game stats as a list

            rolling_stats[f'{stat}_ROLLING'] = rolling_values

        return rolling_stats

    def ret_id(self, player_name):
        """
        Displays the player matches for the given player name.

        :param player_name: The name of the player to search for.
        :return: A list of player IDs matching the name or an empty list if no match is found.
        """
        player_matches = self.get_player_ids(player_name)

        if player_matches:
            player_ids = [player['id'] for player in player_matches]
            print(player_ids)
            return player_ids
        else:
            return []

    def make_df(self, player_ids, szn):
        """
        Creates a DataFrame of the player's game logs and calculates rolling statistics.

        :param player_ids: The list of player IDs to fetch game logs for.
        """
        if player_ids:
            # Assuming the first match is the correct one
            player_id = player_ids[0]
            print(f"Fetching game logs for player with ID {player_id}...")

            # Fetch game logs
            game_logs = self.get_player_game_logs(player_id, szn)
            game_logs= game_logs.iloc[::-1].reset_index(drop=True)
            # Display the first few game logs
            #print(game_logs)  # Display the first few rows of the DataFrame

            # Calculate rolling stats for key player stats
            rolling_game_logs = self.calculate_rolling_stats(game_logs)
            rolling_game_logs = rolling_game_logs.iloc[5:, :]  # Skip the first 5 games (to get valid rolling stats)

            # Return the rolling game logs
            return rolling_game_logs
        else:
            print("No player found.")

 
        """
        Fetches the team game logs for each opponent based on the game logs of the player.

        :param game_logs_df: DataFrame containing player game logs.
        :param szn: Season year.
        """

        for i in range(len(game_logs_df)):
            # Extract the matchup column
            matchup_column = game_logs_df.iloc[i, 4]  # Matchup is typically in the 5th column (index 4)
            print("MATCHUP:", matchup_column)

            # Get the opponent team abbreviation
            team_abbreviation = matchup_column.split()[-1].strip()

            team_id = self.get_team_id_from_abbreviation(team_abbreviation)

            if team_id:
                # Fetch team game logs for the opponent
                game_log = teamgamelog.TeamGameLog(team_id=team_id, season=szn)
                team_game_log_data = game_log.get_data_frames()[0]  # Convert to Pandas DataFrame

                # Store the opponent team game logs
                #print(team_game_log_data.head())  # For simplicity, append the first few rows
            else:
                print(f"Invalid team abbreviation {team_abbreviation}. Skipping...")

    def get_def_stats(self, game_logs_df):
        pts_per_game_def = []
        pts_l3_game_def = []
        def_eff = []
        def_eff_l3 = []
        opp_fp = []
        opp_fp_l3 = []
        opp_fb_pts = []
        opp_fb_pts_l3 = []
        opp_fb_eff = []
        opp_fb_eff_l3 = []
        opp_2pt = []
        opp_2pt_l3 = []
        opp_3pt = []
        opp_3pt_l3 = []

        abbr_to_team_name = {"ATL": "Atlanta",
                            "BOS": "Boston",
                            "BKN": "Brooklyn",
                            "CHA": "Charlotte",
                            "CHI": "Chicago",
                            "CLE": "Cleveland",
                            "DAL": "Dallas",
                            "DEN": "Denver",
                            "DET": "Detroit",
                            "GSW": "Golden State",
                            "HOU": "Houston",
                            "IND": "Indiana",
                            "LAC": "LA Clippers",
                            "LAL": "LA Lakers",
                            "MEM": "Memphis",
                            "MIA": "Miami",
                            "MIL": "Milwaukee",
                            "MIN": "Minnesota",
                            "NOP": "New Orleans",
                            "NYK": "New York",
                            "OKC": "Okla City",
                            "ORL": "Orlando",
                            "PHI": "Philadelphia",
                            "PHX": "Phoenix",
                            "POR": "Portland",
                            "SAC": "Sacramento",
                            "SAS": "San Antonio",
                            "TOR": "Toronto",
                            "UTA": "Utah",
                            "WAS": "Washington"
                        }

        month_map = { "JAN": "01",
                      "FEB": "02",
                      "MAR": "03",
                      "APR": "04",
                      "MAY": "05",
                      "JUN": "06",
                      "JUL": "07",
                      "AUG": "08",
                      "SEP": "09",
                      "OCT": "10",
                      "NOV": "11",
                      "DEC": "12"
                  }

        for i in range(len(game_logs_df)):

            opp = game_logs_df.iloc[i,4].split()[-1].strip()
            opp_full = abbr_to_team_name[opp]
            date = game_logs_df.iloc[i,3].split(' ')
            date[0] = month_map[date[0]]
            date[1] = date[1].strip(',')


            # Print current progress in text
            os.system('cls')
            print(f"Getting Data from Game {i+1} of {len(game_logs_df)}\r")

            url1 = f"https://www.teamrankings.com/nba/stat/opponent-points-per-game?date={date[2]}-{date[0]}-{date[1]}"
            url2 = f"https://www.teamrankings.com/nba/stat/defensive-efficiency?date={date[2]}-{date[0]}-{date[1]}"
            url3 = f"https://www.teamrankings.com/nba/stat/opponent-floor-percentage?date={date[2]}-{date[0]}-{date[1]}"
            url4 = f"https://www.teamrankings.com/nba/stat/opponent-fastbreak-points-per-game?date={date[2]}-{date[0]}-{date[1]}"
            url5 = f"https://www.teamrankings.com/nba/stat/opponent-fastbreak-efficiency?date={date[2]}-{date[0]}-{date[1]}"
            url6 = f"https://www.teamrankings.com/nba/stat/opponent-points-from-2-pointers?date={date[2]}-{date[0]}-{date[1]}"
            url7 = f"https://www.teamrankings.com/nba/stat/opponent-points-from-3-pointers?date={date[2]}-{date[0]}-{date[1]}"
            urls = [url1, url2, url3, url4, url5,url6,url7]
            for url in urls:



                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                table = soup.find('table')
                if table:
                    headers = [th.get_text().strip() for th in table.find_all('th')]
                    rows = [[td.get_text().strip() for td in tr.find_all('td')] for tr in table.find_all('tr')[1:]]
                    df = pd.DataFrame(rows, columns=headers)
                index = df.loc[df["Team"] == opp_full].index
                if url == url1:
                    pts_per_game_def.append(df.iloc[index[0],2])
                    pts_l3_game_def.append(df.iloc[index[0],3])
                elif url == url2:
                    def_eff.append(df.iloc[index[0],2])
                    def_eff_l3.append(df.iloc[index[0],3])
                elif url == url3:
                    opp_fp.append(df.iloc[index[0],2].strip('%'))
                    opp_fp_l3.append(df.iloc[index[0],3].strip('%'))
                elif url == url4:
                    opp_fb_pts.append(df.iloc[index[0],2])
                    opp_fb_pts_l3.append(df.iloc[index[0],3])
                elif url == url5:
                    opp_fb_eff.append(df.iloc[index[0],2])
                    opp_fb_eff_l3.append(df.iloc[index[0],3])
                elif url == url6:
                    opp_2pt.append(df.iloc[index[0],2])
                    opp_2pt_l3.append(df.iloc[index[0],3])
                elif url == url7:
                    opp_3pt.append(df.iloc[index[0],2])
                    opp_3pt_l3.append(df.iloc[index[0],3])
        os.system('cls')
        print("All Game Data Found Successfully!")


        
        df_w_def_stats = game_logs_df
        df_w_def_stats["AVG D PTS ALLOWED"] = pts_per_game_def
        df_w_def_stats["AVG D PTS ALLOWED L3"] = pts_l3_game_def
        df_w_def_stats["OPP DEF EFF"] = def_eff
        df_w_def_stats["OPP DEF EFF L3"] = def_eff_l3
        df_w_def_stats["OPP F%"] = opp_fp
        df_w_def_stats["OPP F% L3"] = opp_fp_l3
        df_w_def_stats["OPP FB PTS"] = opp_fb_pts
        df_w_def_stats["OPP FB PTS L3"] = opp_fb_pts_l3
        df_w_def_stats["OPP FB EFF"] = opp_fb_eff
        df_w_def_stats["OPP FB EFF L3"] = opp_fb_eff_l3
        df_w_def_stats["OPP 2PTS"] = opp_2pt
        df_w_def_stats["OPP 2PTS L3"] = opp_2pt_l3
        df_w_def_stats["OPP 3PTS"] = opp_3pt
        df_w_def_stats["OPP 3PTS L3"] = opp_3pt_l3
    
        # Assuming df is your DataFrame
        df_w_def_stats.iloc[:, 6:26] = df_w_def_stats.iloc[:, 6:26].apply(pd.to_numeric, errors='coerce')
        df_w_def_stats.iloc[:, 47:] = df_w_def_stats.iloc[:, 47:].apply(pd.to_numeric, errors='coerce')
        return df_w_def_stats


def main():
    global defensive_stats
    player_name = input("Input Player Name (e.g. Lebron James): ")
    szn = input("Enter Season (e.g. 2023): ")
    nba_lookup = NBAPlayerLookup(active_only=True)
    player_id = nba_lookup.ret_id(player_name)
    game_logs_df = nba_lookup.make_df(player_id, szn)
    defensive_stats = nba_lookup.get_def_stats(game_logs_df)


    # If you want to inspect the defensive stats
    print(defensive_stats)

    csv_file = f"{player_name.lower()} NBA Game Log.csv"
    defensive_stats.to_csv(csv_file,index = False)
if __name__ == "__main__":
    main()
