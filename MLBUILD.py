import unicodedata
import pandas as pd
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players

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

    def get_player_game_logs(self, player_id,szn):
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


    def display_player_matches(self, player_name):
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
            game_logs = self.get_player_game_logs(player_id,szn)

            # Display the first few game logs
            print(game_logs.head())  # Display the first few rows of the DataFrame

            # Calculate rolling stats for key player stats
            rolling_game_logs = self.calculate_rolling_stats(game_logs)
            rolling_game_logs = rolling_game_logs.iloc[5:,:]
            # Display the rolling stats DataFrame
            print("\nRolling Stats for the Last 5 Games:")
            return rolling_game_logs
        else:
            print("No player found.")


def main():
    player_name = input("Input Player Name: ")
    szn = input("Enter Season:")
    nba_lookup = NBAPlayerLookup(active_only=True)
    player_ids = nba_lookup.display_player_matches(player_name)
    rolling_game_logs_df = nba_lookup.make_df(player_ids,szn)

    if rolling_game_logs_df is not None:
        # You can now manipulate the rolling_game_logs_df DataFrame as needed
        print(rolling_game_logs_df)  # Display first few rows with rolling stats
    else:
      print("WARNING: No game logs found for this season.")


if __name__ == "__main__":
    main()
