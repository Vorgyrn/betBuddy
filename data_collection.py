import requests
from bs4 import BeautifulSoup
import pandas as pd
from pdb import set_trace
import os
import dataclasses
import json
from datetime import datetime
import pytz

positions = ['QB','TE','WR', 'RB']
headers = {'QB':['Rank','Team','Pass Att','Completions','Pass Yards','PTD','Int','Rate','Rush Att','Rushing Yards','AVG','RTD','FL','FPTS'],
                'TE':['Rank','Team','Att','RYd','RAvg','RTD', 'Targ','Receptions','Receiving Yards','CAvg','CTd','FL','FPTS'],
                'WR':['Rank','Team','Att','RYd','RAvg','RTD', 'Targ','Receptions','Receiving Yards','CAvg','CTd','FL','FPTS'],
                'RB':['Rank','Team','Rush Att','Rush Yards','RAvg','RTD', 'Targ','Receptions','Receiving Yards','CAvg','CTd','FL','FPTS'] }

# update based off where you live
reg_str = 'US/Arizona'
REIGION = pytz.timezone(reg_str)

def convertISOTime(iso_time):
    # input: iso_time - a string in iso time
    # returns: a string formatted to the region you are in
    dt_utc = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
    dt_region = dt_utc.astimezone(REIGION)
    formattedTime = dt_region.strftime('%m/%d/%y %I:%M %p')
    return formattedTime

class Match:
    name=''
    home=''
    away=''
    date=None
    week=''
    weather=None
    
    def __init__(self, data):
        self.name=data['name']
        self.away, self.home = data['name'].split(' at ')
        self.week=data['week']['number']
        self.date=datetime.fromisoformat(data['date'].replace("Z", "+00:00"))
        self.date_str= convertISOTime(data['date'])
        if 'weather' in data.keys(): self.weather=data['weather']
        
    def __repr__(self):
        return f'Week {self.week} match of {self.name} on {self.date_str}'
        
class NFLWeek:
    events=[]
    byes = []
    url = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard'
    def __init__(self):
        self.get_schedule()
    
    def get_schedule(self):
        # requests the weeks schedule from self.url and extracts the week number, matches and teams on bye
        response = requests.get(self.url)
        sched = response.json()
        self.week = sched['week']['number']
        self.set_byes(sched['week'])
        for i in sched['events']:
            self.events.append(Match(i))
        
        # sort by date 
        self.events = sorted(self.events, key=lambda obj: obj.date)
        
    def set_byes(self, data):
        # extract the teams on bye
        byes = data['teamsOnBye']
        for team in byes:
            self.byes.append(team['name'])
        
class WeakD:
    positions = ['QB','TE','WR', 'RB']
    headers = {'QB':['Rank','Team','Pass Att','Completions','Pass Yards','PTD','Int','Rate','Rush Att','Rushing Yards','AVG','RTD','FL','FPTS'],
                'TE':['Rank','Team','Att','RYd','RAvg','RTD', 'Targ','Receptions','Receiving Yards','CAvg','CTd','FL','FPTS'],
                'WR':['Rank','Team','Att','RYd','RAvg','RTD', 'Targ','Receptions','Receiving Yards','CAvg','CTd','FL','FPTS'],
                'RB':['Rank','Team','Rush Att','Rush Yards','RAvg','RTD', 'Targ','Receptions','Receiving Yards','CAvg','CTd','FL','FPTS'] }
    
    def __init__(self):
        self.schedule = NFLWeek()
    
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
                if i == 1 and td.text.split()[-1] in self.schedule.byes: onBye = True
                col.append(td.text)
            # if team on bye dont append
            if not onBye: rows.append(col)
            
        return rows
    
    def weakVsStat(self, stat):
        for pos in self.positions:
            header = self.headers[pos]
            # skip the position if the stat is not available
            if stat not in header: 

                continue
            stats = self.scrape(pos)
            df = pd.DataFrame(stats, columns=header)
            df.iloc[:,2:] = df.iloc[:,2:].apply(pd.to_numeric, errors='coerce')
            idx = header.index(stat)
            df.sort_values(by=df.columns[idx], inplace=True, ascending=False)
            bot3 = [i.split()[-1] for i in df.iloc[:3,1]]
            return bot3

def main():
    print("Searching for Some Stank D...")
    weak = WeakD()
    schedule = weak.schedule.events
    statsheet = pd.DataFrame(columns = ["Position","Stat","Defense"])
    
    # Table all bad defenses, stats, and Positions
    for pos in positions:
        if pos == "QB":
            stats = ('Pass Att','Completions','Pass Yards','Rush Att','Rush Yards')
        elif pos == "RB":
            stats == ('Rush Att','Rush Yards','Receptions','Receiving Yards')
        else:
            stats = ('Receptions','Receiving Yards')

        
        for stat in stats:
            bot3 = weak.weakVsStat(stat)
            for i in range(len(bot3)):
                statsheet.loc[len(statsheet)] = [pos, stat, bot3[i]]
    
    #Find All Matches
    matches = []
    for game in schedule:
        matches.append((game.away.split()[-1], game.home.split()[-1]))
    opponents = []
    for j in range(len(statsheet)):
        defense = statsheet.iloc[j,2]
        for m in range(len(matches)):
            matchup = matches[m]
            if defense in matchup:
                if matchup[0] == defense:
                    opponents.append(matchup[1])
                elif matchup[1] == defense:
                    opponents.append(matchup[0])
            else:
                continue
    
    #Add All Matches to StatSheet
    statsheet["Opp"] = opponents
    print(statsheet)
    
   
    
    csv_file = "NFL Bets.csv"
    statsheet.to_csv(csv_file,index = False)
    os.startfile(csv_file)
    
              
 
    
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
