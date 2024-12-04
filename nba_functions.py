def fetch_nba_props():
    '''

    This function fetches the daily player prop bet lines from Rotowire.com. It is configured to specifically find
    the lines and odds from FanDuel. It will find lines and odds for player points, rebounds, assists, three pointers
    made, blocks, steals, points+rebounds+assists, points+rebounds, points+assists, and rebounds+assists. If a player
    does not have an offered line for the specific stat, the row is dropped from the dataframe.
    
    '''
    # Import Required libraries for this function
    import requests
    from bs4 import BeautifulSoup
    import json
    import pandas as pd

    # URL with Daily Lines
    url = "https://www.rotowire.com/betting/nba/player-props.php"
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # List of stats to be extracted
    stats = ["PTS", "REB", "AST","THREES","BLK","STL","PTSREBAST","PTSREB","PTSAST","REBAST"]

    # Create empty dictionary
    all_lines = {}

    for stat in stats:
        # Find the div with the given class and data-prop attribute matching the input stat
        table = soup.find('div', class_='prop-table', attrs={'data-prop': stat})

        # Initialize an empty dictionary to store the data
        data = {}

        if table:
            # Get the data-prop attribute for the current prop_table
            data_prop = table.get('data-prop')

            # Ensure that the script tag exists
            if table.script:
                # Extract the data from the script tag
                raw_javascript = [
                    line.strip()
                    for line in table.script.text.splitlines()
                    if line.strip().startswith('data')
                ]

                if raw_javascript:
                    # [0]: there's only one line starting with "data" per script
                    # [6:-1]: remove the "data: " part and the trailing comma
                    json_string = raw_javascript[0][6:-1]

                    # Add the data to the dictionary using the data-prop attribute
                    data[data_prop] = json.loads(json_string)

        # Convert the collected data to a pandas DataFrame
        if data:
            combined_data = []
            for key, value in data.items():
                combined_data.extend(value)

            df = pd.DataFrame(combined_data)
            headers = ['name', f'fanduel_{stat.lower()}', f'fanduel_{stat.lower()}Under', f'fanduel_{stat.lower()}Over']
            df = df[headers]
            df = df.dropna()
            # Add DataFrame to all_data dictionary
            all_lines[stat] = df
            # Display the DataFrame
            #print(f"Data for {stat}:")
            #print(df)
        else:
            print(f"No data found for stat: {stat}")

    return all_lines