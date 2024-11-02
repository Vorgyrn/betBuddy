import requests
from bs4 import BeautifulSoup
import pandas as pd
from pdb import set_trace

class PlayerStats:
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
    table = soup.find('table', {'class': 'TableBase-table'})
    
    players = []
    
    # Debugging: Print the entire table HTML to see the structure
    # print(table.prettify())  # Uncomment this line to debug the HTML structure

    # Parse the table rows
    #
    for row in table.find_all('tr')[1:]:  # Skip the header row
        columns = row.find_all('td')
        if len(columns) > 0:
            set_trace()
            # Safely extract player name
            player_link = columns[1].find('a')
            name = player_link.text.strip() if player_link else 'N/A'  # Default to 'N/A' if not found
            
            team = columns[2].text.strip()  # Team abbreviation
            games_played = columns[3].text.strip()
            receptions = columns[4].text.strip()
            receiving_yards = columns[5].text.strip()
            touchdowns = columns[6].text.strip()

            player = PlayerStats(name, team, games_played, receptions, receiving_yards, touchdowns)
            players.append(player.to_dict())
    
    return players

def main():
    url = 'https://www.cbssports.com/fantasy/football/stats/WR/2023/ytd/stats/nonppr/'
    stats = scrape_stats(url)
    
    # Organize data into a DataFrame
    df = pd.DataFrame(stats)
    
    # Save to CSV file
    df.to_csv('fantasy_football_wr_stats_2023.csv', index=False)
    print("Data has been scraped and saved to fantasy_football_wr_stats_2023.csv")

if __name__ == "__main__":
    main()
