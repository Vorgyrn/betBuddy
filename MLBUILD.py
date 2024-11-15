##ML Builder
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os
import sys
import tkinter as tk
from tkinter import simpledialog

# Dictionary for full team name to abbreviation
team_name_to_abbr = {
    'Atlanta': 'ATL',
    'Boston': 'BOS',
    'Brooklyn': 'BKN',
    'Charlotte': 'CHA',
    'Chicago': 'CHI',
    'Cleveland': 'CLE',
    'Dallas': 'DAL',
    'Denver': 'DEN',
    'Detroit': 'DET',
    'Golden State': 'GSW',
    'Houston': 'HOU',
    'Indiana': 'IND',
    'LA Clippers': 'LAC',
    'LA Lakers': 'LAL',
    'Memphis': 'MEM',
    'Miami': 'MIA',
    'Milwaukee': 'MIL',
    'Minnesota': 'MIN',
    'New Orleans': 'NOP',
    'New York': 'NYK',
    'Okla City': 'OKC',
    'Orlando': 'ORL',
    'Philadelphia': 'PHI',
    'Phoenix': 'PHX',
    'Portland': 'POR',
    'Sacramento': 'SAC',
    'San Antonio': 'SAS',
    'Toronto': 'TOR',
    'Utah': 'UTA',
    'Washington': 'WAS'
}

# Dictionary for abbreviation to full team name
abbr_to_team_name = {abbreviation: team for team, abbreviation in team_name_to_abbr.items()}

def get_player_name():
     # Create a simple Tkinter root window (hidden)
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Create a dialog box to prompt for player name
    player_name = simpledialog.askstring("Player Search", "Enter NBA Player Name:")

    # Handle the user input
    if player_name:
        print(f"Player selected: {player_name}")
        return player_name
    else:
        print("No player name entered. Exiting...")
        return None
    
def check_file_existence(player):
    # Convert player name to lowercase and construct the file name
    file_name = f"{player.lower()} NBA Game Log.csv"
    
    # Check if the file exists in the current directory
    if os.path.exists(file_name):
        # Prompt the user for confirmation
        response = input(f"The file '{file_name}' already exists. Are you sure you want to overwrite it? (Y/N): ").strip().lower()
        if response == 'y':
            print("Proceeding to overwrite the file...")
            return True  # Allow the program to continue
        else:
            print("Terminating the program to avoid overwriting the file.")
            sys.exit(0)  # Terminate the program
    else:
        print(f"No existing file named '{file_name}' found. Proceeding to create a new file.")
        return True  # Allow the program to continue
# Function to get abbreviation from full team name
def get_abbreviation(team_name):
    return team_name_to_abbr.get(team_name, "Team not found")

# Function to get full team name from abbreviation
def get_team_name(abbreviation):
    return abbr_to_team_name.get(abbreviation, "Abbreviation not found")


def get_game_logs(player):
    #Choose what years to include in ML algorithm
    years = [2025,2024,2023,2022,2021,2020,2019,2018,2017]

    
    df_all_games = pd.DataFrame()
    for year in years:
        url = f"https://www.statmuse.com/nba/ask?q={player.split()[0].lower()}+{player.split()[1].lower()}+regular+season+game+log+{year-1}-{year}+season"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')    
        if table:
            headers = [th.get_text().strip() for th in table.find_all('th')]
            rows = [[td.get_text().strip() for td in tr.find_all('td')] for tr in table.find_all('tr')[1:]]
            df = pd.DataFrame(rows, columns=headers)
            df = df.iloc[:len(df)-3,2:]
            df.iloc[:,0] = df.iloc[0,0].split()[0] + ' ' + df.iloc[0,0].split()[1]
            df.iloc[:, 5:] = df.iloc[:, 5:].apply(pd.to_numeric, errors='coerce')
            df_all_games = pd.concat([df_all_games,df], axis = 0, ignore_index=True)
    df_all_games = df_all_games.iloc[::-1].reset_index(drop=True)  # Reverse for recent games
    return df_all_games

def pts_trend_col(df_all_games):
    pts_trend = []
    for i in range(len(df_all_games)):
        if i<=5:
            pts_trend.append('-')
        else:
            pts_avg_l5 = np.mean(df_all_games.iloc[i-6:i-1,6])
            pts_trend.append(pts_avg_l5)
        
    df_all_games['L5 PTS AVG'] = pts_trend
    df_w_pts_trend = df_all_games
    return df_w_pts_trend

def reb_trend_col(df_w_pts_trend):
    reb_trend = []
    for i in range(len(df_w_pts_trend)):
        if i<=5:
            reb_trend.append('-')
        else:
            reb_avg_l5 = np.mean(df_w_pts_trend.iloc[i-6:i-1,7])
            reb_trend.append(np.mean(reb_avg_l5))
    df_w_pts_trend['L5 REB AVG'] = reb_trend
    df_w_reb_trend = df_w_pts_trend
    return df_w_reb_trend

def ast_trend_col(df_w_reb_trend):
    ast_trend = []
    for i in range(len(df_w_reb_trend)):
        if i<=5:
            ast_trend.append('-')
        else:
            ast_avg_l5 = np.mean(df_w_reb_trend.iloc[i-6:i-1,8])
            ast_trend.append(np.mean(ast_avg_l5))
    df_w_reb_trend['L5 AST AVG'] = ast_trend
    df_w_ast_trend = df_w_reb_trend.iloc[6:,:]
    return df_w_ast_trend

def clean_team_name(player_game_logs):
    team_list = []
    opp_list = []
    for i in range(len(player_game_logs)):
        team_abbrev = player_game_logs.iloc[i,2]
        opp_abbrev = player_game_logs.iloc[i,4]
        team_name = get_team_name(team_abbrev)
        opp_name = get_team_name(opp_abbrev)
        team_list.append(team_name)
        opp_list.append(opp_name)
    clean_df = player_game_logs
    clean_df['TM'] = team_list
    clean_df['OPP'] = opp_list

    return clean_df


def get_def_stats(clean_df):
    pts_per_game_def = []
    pts_l3_game_def = []
    for i in range(len(clean_df)):
        date = clean_df.iloc[i,1].split('/')
        os.system('cls')
        # Calculate progress ratio and how many bars to show
        progress_ratio = i / len(clean_df)
        progress_bar_length = 100  # Number of bars (|) to show
        
        # Calculate number of bars based on progress
        num_bars = int(progress_ratio * progress_bar_length)
        
        # Print the progress bar
        print(100 * "-")
        print("|" * num_bars + " " * (progress_bar_length - num_bars))  # Display bars
        print(100 * "-")
        
        # Print current progress in text
        print(f"Getting Data from Game {i} of {len(clean_df)}\r")
        url = f"https://www.teamrankings.com/nba/stat/opponent-points-per-game?date={date[2]}-{date[0]}-{date[1]}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')
        if table:
            headers = [th.get_text().strip() for th in table.find_all('th')]
            rows = [[td.get_text().strip() for td in tr.find_all('td')] for tr in table.find_all('tr')[1:]]
            df = pd.DataFrame(rows, columns=headers)
        index = df.loc[df["Team"] == f'{clean_df.iloc[i,4]}'].index
        pts_per_game_def.append(df.iloc[index[0],2])
        pts_l3_game_def.append(df.iloc[index[0],3])
    df_w_def_stats = clean_df
    df_w_def_stats["AVG D PTS ALLOWED"] = pts_per_game_def
    df_w_def_stats["AVG D PTS ALLOWED L3"] = pts_l3_game_def

    return df_w_def_stats


def main():
    #Choose player
    player = get_player_name()
    check_file_existence(player)
    df_all_games = get_game_logs(player)
    df_w_pts_trend = pts_trend_col(df_all_games)
    df_w_reb_trend = reb_trend_col(df_w_pts_trend)
    player_game_logs = ast_trend_col(df_w_reb_trend)
    clean_df = clean_team_name(player_game_logs)
    
    def_log = get_def_stats(clean_df)
    csv_file = f"{player.lower()} NBA Game Log.csv"
    def_log.to_csv(csv_file,index = False)
    os.startfile(csv_file)


   
if __name__ == "__main__":
    main()
