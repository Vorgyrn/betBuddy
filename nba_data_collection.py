import requests
from bs4 import BeautifulSoup
import pandas as pd
from pdb import set_trace
import os
import dataclasses
import json
from datetime import datetime
import pytz
import re

def find_matchups():
    active_teams = []
    url_teams_lineups = "https://www.rotowire.com/basketball/nba-lineups.php"
    response = requests.get(url_teams_lineups)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Get all lineup boxes
    lineups = soup.find_all('div', class_='lineup__box')
    for lineup in lineups:
        # Get the matchup text
        matchup = lineup.find('div', class_='lineup__matchup')
        if matchup:
            matchup_text = matchup.get_text(strip=True)
            teams = re.findall(r'\b[A-Za-z0-9]+\b(?=\()', matchup_text)
            if len(teams) == 2:
                active_teams.append(teams[0])
                active_teams.append(teams[1])
    return active_teams

def find_d_stats(positions,headers):
    
    url_defense = "https://www.fantasypros.com/daily-fantasy/nba/fanduel-defense-vs-position.php"
    response = requests.get(url_defense)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    position_dataframes = {}  # Dictionary to hold DataFrame for each position
    
    for pos in positions:
        all_data = []  # List to hold each row of data for the current position
        
        # Find all rows with the specific class for each position
        rows = soup.find_all('tr', class_=f"GC-0 {pos}")
        
        for row in rows:
            # Get all `td` elements in the row
            cells = row.find_all('td')
            row_data = [cell.get_text(strip=True) for cell in cells]  # Extract text from each cell
            all_data.append(row_data)  # Append the row data to all_data
            row_data[0] = row_data[0].split()[-1]
        # Convert the data to a DataFrame and store it in the dictionary
        position_dataframes[pos] = pd.DataFrame(all_data, columns = headers)

    return position_dataframes
        
def sort_bad_d(positions,headers,stats,active_teams,d_stats):
    for pos in positions:
        data = d_stats[f'{pos}']
        data.iloc[:,1:] = data.iloc[:,1:].apply(pd.to_numeric, errors='coerce')
        for stat in stats:
            idx = headers.index(stat)
            data.sort_values(by=data.columns[idx], inplace=True, ascending=False)
            for i in range(3):
                if data.iloc[i,0] in active_teams:
                    print(data.iloc[i,0])



def main():
    positions = ["PG", "SG","SF","PF","C"]
    stats =  ["PTS"]
    headers = ["TEAM","GP","PTS","REB","AST","3PM","STL","BLK","TO","FD PTS"]
    active_teams= find_matchups()
    d_stats = find_d_stats(positions,headers)
    bets_of_interest = sort_bad_d(positions,headers,stats,active_teams,d_stats)
    

if __name__ == "__main__":
    main()