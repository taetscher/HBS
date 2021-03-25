from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os
import unicodecsv as csv
import options
import pandas as pd
from datetime import datetime
from datetime import timedelta

# loading in the options file
teams_seasons = options.teams_seasons
teams = []

# global: data_dir variable to store the cleaned output
data_dir = '././playerProgress_data'


def scrapePlayerProgress():

    #TODO: find a way to only do conversions for the files newly generated

    # run firefox webdriver from executable path of your choice
    driver = webdriver.Chrome()

    # get team ids from options.py
    for season in teams_seasons.values():
        for id in season.values():
            teams.extend(id)

    # check if output directory already exists, create new one if not
    for team in teams:
        try:
            print(f'creating new directories for team {get_team(team)} and season {get_season(team)}...')
            os.makedirs(f"playerProgress_data/{get_team(team)}/{get_season(team)}/raw_data", exist_ok=False)
            os.makedirs(f'output_png/progress_plots/{get_team(team)}/{get_season(team)}', exist_ok=False)
            os.makedirs(f'output_csv/progress_data/{get_team(team)}/{get_season(team)}', exist_ok=False)
        except OSError:
            print(f'directories for team {get_team(team)} and season {get_season(team)} already exist, skipping...\n')

    # scrape the data
    for team in teams:
        season = get_season(team)
        year_start = season.split(' ')[1].split('_')[0]
        year_finish = season.split(' ')[1].split('_')[1]

        team_name, games = findGamesPage(driver, team, year_start, year_finish)

        # Check which (if any) games have already been scraped, discard them
        existing_data = os.listdir(f'playerProgress_data/{get_team(team)}/{season}/raw_data')
        existing_games = []
        for file in existing_data:
            game_nr = file[4:-4]
            existing_games.append(eval(game_nr))

        remove = []
        for game in games:
            if eval(game) in existing_games:
                print(f'game #{game} has already been scraped, skipping')
                remove.append(game)
            else:
                pass

        for element in remove:
            games.remove(element)

        # actual scraping
        for game in games:
            print(f'scraping game {game}...')

            time.sleep(0.5)
            link = f'https://www.handball.ch/de/matchcenter/spiele/{game}'
            time.sleep(0.5)
            try:
                # get the data
                game_stats, date, league = scrapeGame(link, team_name, driver)
                # write a raw file
                raw_file = writer(game_stats, game, date, team, league)
                # convert raw data to csv
                csvConverter(raw_file, data_dir, get_team(team), season)
                print(date, team, league)

            except TypeError:
                print(f'error. most likely the game ({game}) you are trying to download does not have stats available (yet)\nskipping...')


        # aggregate the stats
        # take the converted data and output the final, cleaned and aggregated data per season as csv
        output_csv(get_team(team), season)

    # shut down firefox
    driver.quit()
    print('\n', '-'*10)
    print('scraping successfully terminated, closing firefox...')


def findGamesPage(driver,team,year_start,year_finish):
    """finds all games played by specified team

    returns a list of game ids"""

    # specify url
    urlpage = 'https://www.handball.ch/de/matchcenter/teams/{}#/games'.format(team)
    print('\n\nscraping... ', urlpage)

    driver.get(urlpage)
    time.sleep(2)

    team_name = driver.find_element_by_xpath(r'/html/body/div[2]/div[3]/div/div/div[2]/div/div[2]/h1').text
    print(f'\nscraping games of team: {team_name}, season {year_start}/{year_finish}')

    games_button = driver.find_element_by_xpath('//*[@id="games-tab"]')
    games_button.click()

    time.sleep(1)
    first_date = driver.find_element_by_xpath('//*[@id="dateFromGames_1"]')
    first_date.send_keys(Keys.CONTROL + "a")
    first_date.send_keys('01.07.20'+year_start)

    second_date = driver.find_element_by_xpath('//*[@id="dateToGames_1"]')
    second_date.send_keys(Keys.CONTROL + "a")
    second_date.send_keys(datetime.now().strftime('%d.%m.%Y'))
    second_date.send_keys(Keys.ENTER)

    click_away = driver.find_element_by_xpath('//*[@id="games"]/div/div[1]/h2')
    click_away.click()

    games = getAllGames(driver)
    return team_name, games


def getAllGames(driver):
    """helper function, retrieves and cleans up a list of all games played by specified team"""
    games = []
    time.sleep(1)
    table_rows = driver.find_elements_by_tag_name('tr')

    for row in table_rows:
        game = row.get_attribute('id')

        # get date of game and check if it is in the future, if so, skip
        try:
            date_info = row.find_element_by_xpath('// *[ @ id = "{}"] / td[1] / span[1]'.format(row.get_attribute('id')))
            text = date_info.get_attribute('innerHTML')
            text = text[3:].split('&nbsp;')

            date = text[0]
            kickoff = text[1]
            today = datetime.now().strftime("%d.%m.%y %H:%M")

            t_format = "%d.%m.%y %H:%M"

            game_played = datetime.strptime(date + ' ' + kickoff, t_format)
            now = datetime.strptime(today, t_format) + timedelta(hours=1.5)

            if game_played > now:
                print(f'game @{game_played} is played in the future, not scraping that...')
            else:
                #print(f'appending game played @{game_played}')
                games.append(game)

        except Exception as e:
            #print(e)
            pass

    while ("" in games):
        games.remove("")

    return games


def scrapeGame(link, team, driver):
    """helper function. retrieves game statistics of input game-id

    returns only statistics for specified team and input game"""

    driver.get(link)
    time.sleep(2)
    stats_tab = driver.find_element_by_xpath(r'//*[@id="stats-tab"]')
    stats_tab.click()
    time.sleep(2)
    date = driver.find_element_by_xpath(r'/html/body/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div[3]/span[1]').text
    left_table = driver.find_element_by_xpath(r'//*[@id="stats"]/div[2]/div[3]/div[1]/div/table')
    right_table = driver.find_element_by_xpath(r'//*[@id="stats"]/div[2]/div[3]/div[2]')

    left_content = left_table.get_attribute('innerText')
    left_team = driver.find_element_by_xpath(r'//*[@id="stats"]/div[2]/div[3]/div[1]/div/table/thead[1]/tr/td/span').text
    time.sleep(3)

    right_content = right_table.get_attribute('innerText')
    right_team = driver.find_element_by_xpath(r'//*[@id="stats"]/div[2]/div[3]/div[2]/div/table/thead[1]/tr/td/span').text
    time.sleep(3)

    league = driver.find_element_by_xpath(r'/html/body/div[2]/div[1]/div[2]/div/div/div[6]/p').text
    try:
        league = league.split('-')[1]
    except IndexError:
        pass

    #get only stats for specified team
    try:
        if left_team.upper() == team:
            return left_content, date, league
        elif right_team.upper() == team:
            return right_content, date, league
    except Exception as e:
        print(e)


def writer(game_stats, game, date, team, league):
    """helper function. writes statistics of input game-id into csv file"""

    with open(f'playerProgress_data/{get_team(team)}/{get_season(team)}/raw_data/raw_{game}.csv','wb') as outfile:
        #write in bytes mode ('wb') to avoid characters being saved wrongly
        print(f'\nwriting stats for game {game}...')
        writeR = csv.writer(outfile)
        date = date.split(' ')
        league = league.split(' ')[1:]
        writeR.writerow(date)
        writeR.writerow(league)

        cSv = game_stats.split('\n')

        for element in cSv:
            # remove whitespace at beginning of strings
            try:
                element = element.strip().replace('\t',' ')
            except:
                pass

            element = element.split(' ')
            writeR.writerow(element)

        outfile.close()

    return f'raw_{game}.csv'


def get_team(val):
    """returns the key to a value in a dictionary within the options.py dictionary"""
    for entry in teams_seasons.items():
        for season, number in entry[1].items():
            for element in number:
                if val == element:
                    return entry[0]
    return "season not found"


def get_season(val):
    """returns the season of a value in a dictionary within the options.py dictionary"""
    for entry in teams_seasons.items():
        for season, number in entry[1].items():
            for element in number:
                if val == element:
                    return season
    return "season not found"


def csvConverter(infile, team_folders, team_folder, season):
    """ takes in messy raw data and turns it into readable csv format.
    writes one output file for outfield players and one file for goalies"""
    game_number = infile[4:-4]

    data = []
    with open(f'{team_folders}/{team_folder}/{season}/raw_data/{infile}', 'rb') as infile:

        for line in infile.readlines():
            line = line.decode('utf-8')
            line = line[:-2]
            data.append(line.split(' '))

    date = cleanUp(data[0]).split(' ')[1].replace('.','_')
    date = date[-2:] + '_' + date[3:5] + '_' + date[:2]
    header_players = str(data[3]).strip('["').strip('"]')

    goalie_index = float('NaN')
    staff_index = float('NaN')

    #find where to slice the data to get player stats
    for entry in data:
        if "'TORHÜTER,P/W,7M,%'" in str(entry):
            index = data.index(entry)
            goalie_index = index + 1
        else:
            pass

    # find where to slice the data to get goalie stats
    for entry in data:
        if "STAFF,V,2',D" in str(entry):
            index = data.index(entry)
            staff_index = index + 1
        else:
            pass
    try:
        # this try/except statement is here because there can be faulty raw_.csv files, avoid those and skip
        # Champions League games, for instance, can trigger these exceptions because of bad stats

        player_data = data[4:goalie_index - 2]
        goalie_data = data[goalie_index:staff_index - 2]
        header_goalies = cleanUp(data[goalie_index - 1]).replace(' ', ',')

        # write the cleaned data into two seperate files
        # outfield players
        with open(f'{team_folders}/{team_folder}/{season}/{date}_{game_number}_outfield.csv', 'w',
                  encoding='utf-8') as outfile:
            outfile.write(header_players + '\n')
            for element in player_data:
                element = element[0].split(',')
                element = str(element[1:]).strip("[").strip("]")

                player_names = eval(element)[:-7]
                player_name = ''
                for segment in player_names:
                    player_name = player_name.strip() + ' ' + segment

                player_stats_in = eval(element)[-7:]
                player_stats = []
                for stat in player_stats_in:
                    player_stats.append(str(stat))

                element = str(player_name) + ',' + str(player_stats).strip('[').strip(']').replace("'", '').replace(' ',
                                                                                                                    '')
                outfile.write(element + '\n')
            outfile.close()

        # goalies
        with open(f'{team_folders}/{team_folder}/{season}/{date}_{game_number}_goalies.csv', 'w',
                  encoding='utf-8') as outfile:
            outfile.write(header_goalies + '\n')
            for element in goalie_data:
                element = element[0].split(',')
                element = str(element[1:]).strip("[").strip("]")

                goalie_names = eval(element)[:-3]
                goalie_name = ''
                for segment in goalie_names:
                    goalie_name = goalie_name.strip() + ' ' + segment

                goalie_stats_in = eval(element)[-3:]
                goalie_stats = []
                for stat in goalie_stats_in:
                    goalie_stats.append(str(stat))

                element = str(goalie_name) + ',' + str(goalie_stats).strip('[').strip(']').replace("'", '').replace(' ',
                                                                                                                    '')
                outfile.write(element + '\n')
            outfile.close()
    except TypeError:
        print('raw_file has errors, skipping this one...')


def cleanUp(inlist):
    return str(inlist).strip("['").strip("']").replace(',',' ')


def output_csv(team_folder, season):

    # read in newly generated, split csvs
    inputs = []
    outfield = []
    goalies = []

    inputs.extend(os.listdir(f'{data_dir}/{team_folder}/{season}'))

    # create list of files for outfield/goalie players
    for file in inputs:
        if str(file).split('_')[-1] == 'outfield.csv':
            outfield.append(file)
        elif str(file).split('_')[-1] == 'goalies.csv':
            goalies.append(file)
        else:
            pass

    # first, generate a list of all players who have played over the course of the whole season
    outfield_players = []
    for file in outfield:
        temp_df = pd.read_csv(f'{data_dir}/{team_folder}/{season}/{file}', encoding='utf-8').fillna(0)
        for player in temp_df['SPIELER']:
            outfield_players.append(player)
    outfield_players = set(outfield_players)

    stats = ['TORE', '7M', r'%', 'TF', 'V', r"2'", 'D']

    for stat in stats:
        try:
            merged_outfield = mergeStatsOutfield(outfield, outfield_players, stat, team_folder, season)
            write(merged_outfield, team_folder, season, stat)

        except Exception as e:
            print('in output_csv, outfield player handling: ', e)

    # second, generate a list of all goalies who have played over the course of the whole season
    goalie_players = []
    for file in goalies:
        temp_df = pd.read_csv(f'{data_dir}/{team_folder}/{season}/{file}', encoding='utf-8').fillna(0)
        for player in temp_df['TORHÜTER']:
            goalie_players.append(player)
    goalie_players = set(goalie_players)

    stats = ['P/W', '7M', '%']

    for stat in stats:
        try:
            merged_goalies = mergeStatsGoalie(goalies, goalie_players, stat, team_folder, season)
            write(merged_goalies, team_folder, season, str(stat).replace('/', '-') + '_goalie')

        except Exception as e:
            print('in output_csv, goalie player handling: ', e)


def mergeStatsOutfield(games_list, player_list, stat, team_folder, season):
    """merging stats across the season (stats per game per player)"""
    
    # create a base dataframe of all players
    join_df = pd.DataFrame(list(player_list), columns=['SPIELER'])

    header = ['TORE', '7M', r'%', 'TF', 'V', r"2'", 'D']
    header.remove(stat)

    # merge stats to the base dataframe using the date as column name
    for file in games_list:
        temp_df = pd.read_csv(f'{data_dir}/{team_folder}/{season}/{file}', encoding='utf-8').fillna(0)
        merged = pd.merge(join_df, temp_df, left_on='SPIELER', right_on='SPIELER', how='outer')#.fillna(-1)
        merged = merged.drop(header, axis=1)
        merged.rename(columns={stat : str(file[:8])}, inplace=True)
        join_df = merged

    # sort columns: first is SPIELER, then sort according to date
    join_df = join_df.reindex(sorted(join_df.columns), axis=1)
    col = join_df.pop("SPIELER")
    join_df.insert(0, col.name, col)
    return join_df


def mergeStatsGoalie(games_list,player_list,stat,team_folder,season):
    """merging stats across the season (stats per game per player)"""

    # create a base dataframe of all players
    join_df = pd.DataFrame(list(player_list), columns=['TORHÜTER'])

    header = [r'P/W','7M',r'%']
    header.remove(stat)

    # merge stats to the base dataframe using the date as column name
    for file in games_list:
        temp_df = pd.read_csv(f'{data_dir}/{team_folder}/{season}/{file}', encoding='utf-8').fillna(0)
        merged = pd.merge(join_df, temp_df, left_on='TORHÜTER', right_on='TORHÜTER', how='outer')#.fillna(-1)
        merged = merged.drop(header, axis=1)
        merged.rename(columns={stat : str(file[:8])}, inplace=True)
        join_df = merged

    # sort columns: first is SPIELER, then sort according to date
    join_df = join_df.reindex(sorted(join_df.columns), axis=1)
    col = join_df.pop("TORHÜTER")
    join_df.insert(0, col.name, col)

    return join_df


def write(input_dataframe, team_folder, season, stat):
    print(f'writing data to ././output_csv/progress_data/{team_folder}/{season}/{stat}')
    input_dataframe.to_csv(f'././output_csv/progress_data/{team_folder}/{season}/{stat}', index=False)
    return f'././output_csv/progress_data/{team_folder}/{season}/{stat}'


if __name__ == '__main__':
    scrapePlayerProgress()
