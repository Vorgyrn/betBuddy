##ML Builder
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os

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
        print(f"Getting Data from Game {date[0]}-{date[1]}-{date[2]}")
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
    player = "LeBron James"
    df_all_games = get_game_logs(player)
    df_w_pts_trend = pts_trend_col(df_all_games)
    df_w_reb_trend = reb_trend_col(df_w_pts_trend)
    player_game_logs = ast_trend_col(df_w_reb_trend)
    clean_df = clean_team_name(player_game_logs)
    
    def_log = get_def_stats(clean_df)
    print(def_log)
    csv_file = f"{player} NBA Game Log.csv"
    def_log.to_csv(csv_file,index = False)
    os.startfile(csv_file)


   
if __name__ == "__main__":
    main()
