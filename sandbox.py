import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np

def find_game_data():
    print('Loading Schedule...')
    url_teams_lineups = "https://www.rotowire.com/basketball/nba-lineups.php"
    response = requests.get(url_teams_lineups)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    lineups = soup.find_all('div', class_='lineup__box')
    return lineups

def find_matchups(lineups):
    matches = []
    active_teams = []
    for lineup in lineups:
        matchup = lineup.find('div', class_='lineup__matchup')
        if matchup:
            matchup_text = matchup.get_text(strip=True)
            teams = re.findall(r'\b[A-Za-z0-9]+\b(?=\()', matchup_text)
            matches.append(teams)
            if len(teams) == 2:
                active_teams.append(teams[0])
                active_teams.append(teams[1])
    return active_teams, matches

def find_d_stats(positions, headers):
    print('Loading Weak Defenses...')
    url_defense = "https://www.fantasypros.com/daily-fantasy/nba/fanduel-defense-vs-position.php"
    response = requests.get(url_defense)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    position_dataframes = {}
    for pos in positions:
        all_data = []
        rows = soup.find_all('tr', class_=f"GC-0 {pos}")
        for row in rows:
            cells = row.find_all('td')
            row_data = [cell.get_text(strip=True) for cell in cells]
            all_data.append(row_data)
            row_data[0] = row_data[0].split()[-1]
        position_dataframes[pos] = pd.DataFrame(all_data, columns=headers)
    return position_dataframes

def sort_bad_d(positions, headers, stats, active_teams, d_stats):
    pos_list = []
    stat_list = []
    defense_list = []
    for pos in positions:
        data = d_stats[f'{pos}']
        data.iloc[:, 1:] = data.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
        for stat in stats:
            idx = headers.index(stat)
            data.sort_values(by=data.columns[idx], inplace=True, ascending=False)
            for i in range(5):
                if data.iloc[i, 0] in active_teams:
                    pos_list.append(pos)
                    stat_list.append(stat)
                    defense_list.append(data.iloc[i, 0])
    boi = list(zip(pos_list, stat_list, defense_list))
    boi3 = pd.DataFrame(boi, columns=["POS", "STAT", "DEFENSE"])
    return boi3

def fill_opps(boi3, matches):
    opp_list = []
    for i in range(len(boi3)):
        for match in matches:
            if boi3.iloc[i, 2] in match:
                if boi3.iloc[i, 2] == match[0]:
                    opp_list.append(match[1])
                    break
                elif boi3.iloc[i, 2] == match[1]:
                    opp_list.append(match[0])
                    break
    boi3["OPP"] = opp_list
    return boi3

def fill_players(boi4, lineups):
    print('Loading Opposing Players...')
    opp_player_list = []
    for i in range(len(boi4)):
        team_players = []
        opp_team = boi4.iloc[i, 3]
        for lineup in lineups:
            matchup = lineup.find('div', class_='lineup__matchup')
            if matchup:
                matchup_text = matchup.get_text(strip=True)
                teams = re.findall(r'\b[A-Za-z0-9]+\b(?=\()', matchup_text)
                if opp_team in teams:
                    team_ind = teams.index(f'{opp_team}')
                    team_type = "is-visit" if team_ind == 0 else "is-home"
                    break
            else:
                print("No Matchup")
        lineup_list = lineup.find('ul', class_=f'lineup__list {team_type}')
        if lineup_list:
            players = lineup_list.find_all('li', class_='lineup__player')
            for player in players:
                name_tag = player.find('a')
                if name_tag:
                    name = name_tag.get('title', name_tag.get_text(strip=True))
                    team_players.append(name)
        if boi4.iloc[i, 0] == "PG":
            opp_player_list.append(team_players[0])
        elif boi4.iloc[i, 0] == "SG":
            opp_player_list.append(team_players[1])
        elif boi4.iloc[i, 0] == "SF":
            opp_player_list.append(team_players[2])
        elif boi4.iloc[i, 0] == "PF":
            opp_player_list.append(team_players[3])
        elif boi4.iloc[i, 0] == "C":
            opp_player_list.append(team_players[4])
    boi4["OPP PLAYER"] = opp_player_list
    return boi4

def get_player_avg(boi5, n):
    headers = ["Name", "Date", "TEAM", " ", "OPP", "MIN", "PTS", "REB", "AST", "STL", "BLK", "FGM", "FGA", "FG%", "3PM", "3PA", "3P%", "FTM", "FTA", "FT%", "TS%", "OREB", "DREB", "TOV", "PF", "+/-"]
    player_stats = {}
    for i in range(len(boi5)):
        all_data = []
        player = boi5.iloc[i, 4]
        player = re.sub(r'[éèêë]', 'e', player)
        player = re.sub(r'[áàâäã]', 'a', player)
        player = re.sub(r'[íìîï]', 'i', player)
        player = re.sub(r'[óòôöõ]', 'o', player)
        player = re.sub(r'[úùûü]', 'u', player)
        player = re.sub(r'[ç]', 'c', player)
        player_names = player.split()
        stat = boi5.iloc[i, 1]
        print(f'Loading {stat} Data for {player}...')
        if len(player_names) == 2:
            player_url = f"https://www.statmuse.com/nba/ask/{player_names[0].lower()}-{player_names[1].lower()}-last-{n}-games"
        elif len(player_names) == 3:
            player_url = f"https://www.statmuse.com/nba/ask/{player_names[0].lower()}-{player_names[1].lower()}-{player_names[2].lower()}-last-{n}-games"
        else:
            print(player, 'is an unknown format')

        response = requests.get(player_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('tr')
        n_rows = rows[1:n+3]
        for row in n_rows:
            cells = row.find_all('td')
            row_data = [cell.get_text(strip=True) for cell in cells]
            all_data.append(row_data)
        if len(all_data) == n+2:
            player_df = pd.DataFrame(all_data)
            player_df = player_df.iloc[:, 2:]
            for j in range(n):
                player_df.iloc[j, 0] = player
            player_df.columns = headers
            player_stats[player] = player_df
        else:
            print("Not Enough Player Data")
    return player_stats

def fill_stats(boi5, player_stats, n):
    stat_avg_list = []
    for i in range(len(boi5)):
        player = boi5.iloc[i, 4]
        stat = boi5.iloc[i, 1]
        df = player_stats[player]
        df.replace("None", np.nan, inplace=True)
        df.dropna(inplace=True)
        z = len(df) - 2
        if stat == "PTS":
            fill_stat = df.iloc[z, 6]
        elif stat == "REB":
            fill_stat = df.iloc[z, 7]
        elif stat == "AST":
            fill_stat = df.iloc[z, 8]
        stat_avg_list.append(fill_stat)

    boi5["SZN AVG"] = stat_avg_list
    boi6 = boi5
    return boi6


def main():
    positions = ["PG", "SG", "SF", "PF", "C"]
    stats = ["PTS", "REB", "AST"]
    headers = ["TEAM", "GP", "PTS", "REB", "AST", "3PM", "STL", "BLK", "TO", "FD PTS"]
    
    # Step 1: Load game data
    lineups = find_game_data()
    active_teams, matches = find_matchups(lineups)
    
    # Step 2: Load defensive stats
    d_stats = find_d_stats(positions, headers)
    
    # Step 3: Identify weak defenses
    boi3 = sort_bad_d(positions, headers, stats, active_teams, d_stats)
    
    # Step 4: Find opposing teams
    boi4 = fill_opps(boi3, matches)
    
    # Step 5: Find opposing players
    boi5 = fill_players(boi4, lineups)
    
    # Step 6: Get player averages
    n = 10
    player_stats = get_player_avg(boi5, n)
    boi6 = fill_stats(boi5, player_stats, n)
    
    # Step 7: Fetch player lines
    all_lines = fetch_lines()
    
    # Step 8: Fill in player lines
    boi7 = fill_lines(boi6, all_lines)
    
    # Step 9: Save to CSV and open the file
    print(boi7)
    csv_file = "NBA_Bets.csv"
    boi7.to_csv(csv_file, index=False)
    os.startfile(csv_file)

if __name__ == "__main__":
    main()
