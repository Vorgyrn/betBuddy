import requests
from bs4 import BeautifulSoup
import pandas as pd
from pdb import set_trace
import os
import dataclasses

positions = ['QB','TE','WR', 'RB'] #  'TE','WR', 'RB'
headers = {'QB':['Rank','Team','PAtt','Cmp','PYd','PTD','Int','Rate','RAtt','RYd','AVG','RTD','FL','FPTS'],
            'TE':['Rank','Team','Att','RYd','RAvg','RTD', 'Targ','Recpt','CYd','CAvg','CTd','FL','FPTS'],
            'WR':['Rank','Team','Att','RYd','RAvg','RTD', 'Targ','Recpt','CYd','CAvg','CTd','FL','FPTS'],
            'RB':['Rank','Team','Att','RYd','RAvg','RTD', 'Targ','Recpt','CYd','CAvg','CTd','FL','FPTS']
        }

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

class WeakD:
    positions = ['QB','TE','WR', 'RB'] #  'TE','WR', 'RB'
    headers = {'QB':['Rank','Team','PAtt','Cmp','PYd','PTD','Int','Rate','RAtt','RYd','AVG','RTD','FL','FPTS'],
                'TE':['Rank','Team','Att','RYd','RAvg','RTD', 'Targ','Recpt','CYd','CAvg','CTd','FL','FPTS'],
                'WR':['Rank','Team','Att','RYd','RAvg','RTD', 'Targ','Recpt','CYd','CAvg','CTd','FL','FPTS'],
                'RB':['Rank','Team','Att','RYd','RAvg','RTD', 'Targ','Recpt','CYd','CAvg','CTd','FL','FPTS'] }
    
    def __init__(self, byes=[]):
        self.byes = byes
    
    def scrape(self, pos):
        url = f"https://www.cbssports.com/fantasy/football/stats/posvsdef/{pos}/ALL/avg/standard"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table containing the stats
        table = soup.find('table')

        # Parse the table rows
        rows = []
        for tr in table.find_all('tr')[3:]:  # Skip the header rows
            col = []
            onBye = False
            for i, td in enumerate(tr.find_all('td')):
                if i == 1 and td.text.split()[-1] in self.byes: onBye = True
                col.append(td.text)
            # if team on bye dont append
            if not onBye: rows.append(col)
            
        return rows
    
    def weakVsStat(self, stat):
        for pos in self.positions:
            header = self.headers[pos]
            # skip the position if the stat is not available
            if stat not in header: 
                print(f"Stat {stat} is not available for {pos}s.")
                continue
            print(f"Searching for stanky D versus {pos} {stat}...")
            stats = self.scrape(pos)
            df = pd.DataFrame(stats, columns=header)
            df.iloc[:,2:] = df.iloc[:,2:].apply(pd.to_numeric, errors='coerce')
            idx = header.index(stat)
            df.sort_values(by=df.columns[idx], inplace=True, ascending=False)
            [print(i.split()[-1]) for i in df.iloc[:3,1]]  
            print('')
            
def scrape_stats(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table containing the stats
    table = soup.find('table')

    # Parse the table rows
    rows = []
    for tr in table.find_all('tr')[3:]:  # Skip the header row
        col = []
        for i, td in enumerate(tr.find_all('td')):
            # if i == 1: if team name in bye list set skip flag to true
            col.append(td.text)
        # if team on bye dont append
        rows.append(col)
        
    return rows

def main():
    
    weak = WeakD()
    weak.weakVsStat('PTD')
    
    '''
    param = 'RYd'
    for pos in positions:
        header = headers[pos]
        idx = header.index(param)
        print(f"Searching for stanky D versus {pos} {param}...")
        url = f"https://www.cbssports.com/fantasy/football/stats/posvsdef/{pos}/ALL/avg/standard"
        stats = scrape_stats(url)
        
        df = pd.DataFrame(stats, columns=header)
        df.iloc[:,2:] = df.iloc[:,2:].apply(pd.to_numeric, errors='coerce')
        df.sort_values(by=df.columns[idx], inplace=True, ascending=False)
        [print(i.split()[-1]) for i in df.iloc[:3,1]]  
        print('') 
        
        file_name = ''
        df.to_csv('fantasy_football_wr_stats_2024.csv', index=False)
        print("Data has been scraped and saved to fantasy_football_wr_stats_2023.csv") '''

if __name__ == "__main__":
    main()
