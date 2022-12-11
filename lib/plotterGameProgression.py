import os
import pandas as pd
import options
import random
import numpy as np

data_dir = '../output_csv/gameProgressions'

#loading in the options file
teams_seasons = options.teams_seasons

def plotGameProgressions():

    team_folders = os.listdir(data_dir)

    for team_folder in team_folders:
        seasons = os.listdir(f'{data_dir}/{team_folder}')

        for season in seasons:
            print(f'\n\nPlotting game progressions for team {team_folder}, season {season}')
            games = os.listdir(f'{data_dir}/{team_folder}/{season}')

            whole_season = pd.DataFrame()
            for game in reversed(games):
                if game == 'median_performance.csv':
                    pass
                else:
                    df, home, away, date = convert_stats(data_dir, team_folder, season, game)
                    df['time'] = df['time'].round()
                    grouped = df.groupby('time', as_index=False)['Moving Average'].mean()
                    whole_season[game[:6]] = grouped['Moving Average']

            whole_season['Average Performance (Whole Season)'] = whole_season.mean(axis=1)
            whole_season['Median Performance (Whole Season)'] = whole_season.median(axis=1)
            whole_season['time'] = np.arange(1,len(whole_season)+1)

            whole_season.to_csv(f'../output_csv/gameProgressions/{team_folder}/{season}/median_performance.csv', index=False)

            print(whole_season.head(10))


def convert_stats(data_dir, team_folder, season, game):

    time = []
    score = []
    cols = []
    with open(f'{data_dir}/{team_folder}/{season}/{game}', 'r') as infile:
        lines = infile.readlines()
        n = 0
        for line in lines:
            # line = line.decode('utf-8')
            if n == 0:
                line = line[:-1]
                cols.extend(line.split(','))
                n += 1
            else:
                line = line.split(',')
                time.append(str(line[0]))
                score.append(str(line[1][:-1]))
                n += 1

        data = reversed(list(zip(time, score)))

        df = pd.DataFrame(data, columns=cols)

        # check which team was home or away, adjust goal diff accordingly
        homeAway = 1000
        ha = game[9:].split('_')
        home = ha[0]
        away = ha[1][:-4]
        date = game[:9]
        us = ['lakeside', 'wacker', 'steffisburg']
        if any(us in home.lower() for us in us):
            homeAway = 0
        else:
            homeAway = 1

        # calculate new columns
        df['GDoT'] = df['score'].apply(lambda x: convert_score(x, homeAway))
        df['time'] = df['timestamp'].apply(lambda t: convert_time(t))
        df['Moving Average'] = df['GDoT'].rolling(6, min_periods=1, center=True).mean()

        return df, home, away, date


def convert_score(x, homeAway):
    try:
        if homeAway == 0:
            string = str(x).split(':')
            diff = round(int(string[0])-int(string[1]),1)
            return diff
        else:
            string = str(x).split(':')
            diff = round(int(string[1]) - int(string[0]), 1)
            return diff

    except (ValueError, IndexError) as e:
        return x


def convert_time(t):

    try:
        minutes = int(t.split(':')[0])
        seconds = int(t.split(':')[1])/60
        return round(minutes + seconds, 1)

    except (ValueError, IndexError) as e:
        return t


def r_color():
    r = lambda: random.randint(0, 255)
    return '#%02X%02X%02X' % (r(),r(),r())

if __name__ == '__main__':
    plotGameProgressions()