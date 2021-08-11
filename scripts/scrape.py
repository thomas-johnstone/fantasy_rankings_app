import os
import os.path as osp
import hashlib
import argparse
import requests
import json
from bs4 import BeautifulSoup

# EITHER LOAD OR CREATE THE CACHE
def get_url_contents(cache_dir, url, use_cache=True):

    name = hashlib.sha1(url.encode('utf-8')).hexdigest()
    path = osp.join(cache_dir, name)

    contents = None

    if osp.exists(path) and use_cache is True:
        print ('Loading from the Cache...')
    else:
        print ('Loading from the Source...')
        r = requests.get(url)
        contents = r.text
        with open (path, 'w') as fh:
            fh.write(contents)
    
    return path

# EXTRACT JUST THE INFORMATION AT THE 'TR' CLASS
def extract(filename, url):
    
    data = []
    players = []

    print('Parsing HTML Data...')

    soup = BeautifulSoup(open(filename, 'r'), 'html.parser')
    field_content = soup.find_all('tr')

    for content in field_content:
        for player in content.find_all('td'):
            data.append(player.getText())

    i = 0
    while i < len(data):
        players.append((data[i:i+29]))
        i = i + 29

    return players

# FORMAT THE PLAYER DATA FOR PROPER DATABASE USABILITY
def to_json(players):

    print('Formatting to JSON for Database...')

    data = {}
    key_values = ['Player', 'Position', 'Age', 'Team', 'Games', 'Games Started', 'Minutes Played', 'Field Goals',
    'Field Goals Attempted', 'Field Goal %', '3 Pointers', '3 Pointers Attempted', '3 Point %', '2 Pointers', '2 Pointers Attempted',
    '2 Point %', 'EFG%', 'Free Throws', 'Free Throws Attempted', 'Free Throw %', 'O Rebound', 'D Rebounds', 'Total Rebounds',
    'Assists', 'Steals', 'Blocks', 'Turnovers', 'Personal Fouls', 'Points']

    # CREATE A DICT OF KEY/VALUE PAIRS WITH CORRESPONDING STATS
    i = 0
    while i < len(players):
        j = 0
        data['Player #' + str(i + 1)] = {}
        while j < 29:
            if players[i][j] != "":
                data['Player #' + str(i + 1)][key_values[j]] = players[i][j]
            else:
               data['Player #' + str(i + 1)][key_values[j]] = '0' 
            j = j + 1
        i = i + 1

    # EMPTY THE REPEAT PLAYER DICTS (NOTE: HARD CODED TO ALLOW ONLY UP TO 5 TEAMS IN ONE SEASON AT THE MOMENT)
    i = 0
    while i < len(data):
        k = 0
        if (data['Player #' + str(i + 1)]['Team']) == "TOT":
            if (data['Player #' + str(i + 1)]['Player']) == (data ['Player #' + str(i + 2)]['Player']):
                j = 0
                while j < 29:
                    del (data['Player #' + str(i + 2)][key_values[j]])
                    j = j + 1
                k = k + 1        
            if (data['Player #' + str(i + 1)]['Player']) == (data ['Player #' + str(i + 3)]['Player']):
                j = 0
                while j < 29:
                    del (data['Player #' + str(i + 3)][key_values[j]])
                    j = j + 1
                k = k + 1
            if (data['Player #' + str(i + 1)]['Player']) == (data ['Player #' + str(i + 4)]['Player']):
                j = 0
                while j < 29:
                    del (data['Player #' + str(i + 4)][key_values[j]])
                    j = j + 1
                k = k + 1
            if (data['Player #' + str(i + 1)]['Player']) == (data ['Player #' + str(i + 5)]['Player']):
                j = 0
                while j < 29:
                    del (data['Player #' + str(i + 5)][key_values[j]])
                    j = j + 1
                k = k + 1
            if (data['Player #' + str(i + 1)]['Player']) == (data ['Player #' + str(i + 6)]['Player']):
                j = 0
                while j < 29:
                    del (data['Player #' + str(i + 6)][key_values[j]])
                    j = j + 1
                k = k + 1           
        i = i + k + 1

    
    # DELETE THE EMPTY PLAYER DICTS
    length = (len(data))
    i = 0
    while i < length:
        if not(data['Player #' + str(i + 1)]):
            del(data['Player #' + str(i + 1)])
        i = i + 1

    # RE-ORDER THE DICT (NOTE: O(n) SINCE WE NEED TO MAKE A NEW DICT, NOT WORK IN PLACE)
    final = {}
    i = 0
    for key in data:
        final['Player #' + str(i + 1)] = data[key]
        i = i + 1

    return(final)

# SAMPLE INPUT: python3 scrape.py -c ../cache -y 2021
def main():
    
    print ('Parsing Arguments...')
    #LOAD THE INPUTS FROM THE SCRIPT
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', help='path to cache directory', required=True)
    parser.add_argument('-y', help='year', required=True)
    
    #PARSE ARGS, AND CREATE THE CACHE DIR IF IT DOES NOT EXIST ALREADY
    args = parser.parse_args()

    if not osp.exists(args.c):
        os.makedirs(args.c)

    #LOAD THE URL & APPEND THE DESIRED YEAR
    boxScore = {}
    url = 'https://www.basketball-reference.com/leagues/NBA_'+ args.y +'_per_game.html'

    # CHECK CACHE & CREATE THE FILE
    cache_data = get_url_contents(args.c, url, True)
    boxScore = extract(cache_data, url)
    final = to_json(boxScore)

    # WRITE TO FILE
    with open('../data/data_' + args.y + '.json', "w") as outfile:
        json.dump(final, outfile)

    print('File Created!')

if __name__ == '__main__':
    main()