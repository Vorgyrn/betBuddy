import requests
from bs4 import BeautifulSoup
import pandas as pd
from pdb import set_trace
import os
import dataclasses

class TeamStats:
    def __init__(self, name, team, games_played, receptions, receiving_yards, touchdowns):
        self.name = name
        self.team = team
        self.games_played = games_played
        self.receptions = receptions
        self.receiving_yards = receiving_yards
        self.touchdowns = touchdowns

    def to_dict(self):
        return {
            'Name': self.name,
            'Team': self.team,
            'Games Played': self.games_played,
            'Receptions': self.receptions,
            'Receiving Yards': self.receiving_yards,
            'Touchdowns': self.touchdowns
        }

def scrape_stats(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table containing the stats
    table = soup.find('table')
    players = []
    
    # Debugging: Print the entire table HTML to see the structure

    # Parse the table rows

    rows = []
    for tr in table.find_all('tr')[3:]:  # Skip the header row
        col = []
        for i, td in enumerate(tr.find_all('td')):
            val = td.text
            #if i != 1: val = pd.to_numeric(td.text)
            col.append(val)
        rows.append(col)
        
    return rows

def main():
    positions = ['QB'] # 'TE','WR', 
    for pos in positions:
        url = f"https://www.cbssports.com/fantasy/football/stats/posvsdef/{pos}/ALL/avg/standard"
        stats = scrape_stats(url)
        headers = ['Rank','Team','PAtt','Cmp','PYd','TD','Int','Rate','RAtt','RYd','AVG','TD','FL','FPTS']
        df = pd.DataFrame(stats,columns = headers)
        df.iloc[:,2:] = df.iloc[:,2:].apply(pd.to_numeric,errors = 'coerce')
        df.sort_values(by=df.columns[4],inplace = True,ascending=False)
        [print(i.split()[-1]) for i in df.iloc[:3,1]]
        
        '''
        file_name = ''
        df.to_csv('fantasy_football_wr_stats_2024.csv', index=False)
        print("Data has been scraped and saved to fantasy_football_wr_stats_2023.csv") '''
        
        
    #url = "https://www.cbssports.com/fantasy/football/stats/posvsdef/QB/ALL/avg/standard"
    #stats = scrape_stats(url)
    
    # Organize data into a DataFrame
    #df = pd.DataFrame(stats)
    
    # Save to CSV file
    '''
    file_name = ''
    df.to_csv('fantasy_football_wr_stats_2024.csv', index=False)
    print("Data has been scraped and saved to fantasy_football_wr_stats_2023.csv") '''
  
    #print(df)

if __name__ == "__main__":
    main()
