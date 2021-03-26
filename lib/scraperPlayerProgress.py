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
    """
    Function that handles scraping of the player progress statistics

    :return: does not return, saves outputs into output_csv/progress_data
    """

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
        try:
            check_dir = f'playerProgress_data/{get_team(team)}/{season}/raw_data'
            games = check_for_already_scraped_games(games, check_dir, 4, -4)
        except Exception as e:
            print(e)

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

    # shut down webdriver
    driver.quit()
    print('\n', '-'*10)
    print('scraping successfully terminated, closing webdriver...')


def findGamesPage(driver, team, year_start, year_finish):
    """
    Finds all games played by specified team.

    :param driver: selenium webdriver object
    :param team: SHV team ID (season-specific)
    :param year_start: starting year of a season (for 2021/2022 year_start = 21)
    :param year_finish: ending year of a season (for 2021/2022 year_finish = 22)
    :return: returns a list of game SHV game IDs
    """

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
    """
    Finds all games played by specified team in driver at 'https://www.handball.ch/de/matchcenter/teams/{}#/games'.
    Checks if the games have already been played and removes games which won't be finished 1.5 hours in the future

    :param driver: selenium webdriver object
    :return: returns a list of valid games
    """

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
    """
    Helper function that scrapes statistics of input game-id

    :param link: link to a game played and recorded with SHV Liveticker Feature
    :param team: handball team to query for
    :param driver: selenium webdriver object
    :return: statistics for specified team and input game; the date of the game; the leage in which the game was played
    """

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
    """
    Helper function that writes statistics of input game-id into raw_{game-ID}.csv file in playerProgress_data

    :param game_stats: game statistics scraped from handball.ch
    :param game: SHV game ID
    :param date: date of the game played
    :param team: SHV team ID (season-specific)
    :param league: leage in which the game was played
    :return: returns the filename of the raw_{game-ID}.csv file created
    """

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
    """
    Helper function that returns the key to a value in the options.py dictionary

    :param val: SHV team ID (season-specific)
    :return: returns the team name (key of value)
    """

    for entry in teams_seasons.items():
        for season, number in entry[1].items():
            for element in number:
                if val == element:
                    return entry[0]
    return "season not found"


def get_season(val):
    """
    Helper function that returns the key to a value in the options.py dictionary

    :param val: SHV team ID (season-specific)
    :return: returns the season name (key of value)
    """

    for entry in teams_seasons.items():
        for season, number in entry[1].items():
            for element in number:
                if val == element:
                    return season
    return "season not found"


def csvConverter(infile, team_folders, team_folder, season):
    """
    Converts messy raw data scraped from SHV page and turns it into readable csv format.
    Writes one output csv per season for outfield players and for goalies.

    :param infile: raw_{game-ID}.csv file with messy data
    :param team_folders: path to team folders (playerProgress_data)
    :param team_folder: path to team folder (specific subdirectory of team_folders)
    :param season: the name of the season for which stats are converted
    :return: does not return, but saves output .csv files at playerProgress_data
    """

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
    """
    Helper function that converts lists to strings without []
    :param inlist: list
    :return: string of list, where no [] are present and the separator is one empty space
    """

    return str(inlist).strip("['").strip("']").replace(',', ' ')


def output_csv(team_folder, season):
    """
    Helper function that takes cleaned .csv files from csvConverter and outputs them to output_csv/progress_data

    :param team_folder: the team name for which output csvs should be generated
    :param season: the season name for which output csvs should be generated
    :return: does not return, saves output csv files in output_csv/progress_data
    """

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
    """
    Helper function that merges outfield player's stats from different games to get a csv where stats per game per
    player are available.

    :param games_list: list of games that are to be merged
    :param player_list: list of all players that have played at least one game
    :param stat: string of the statistic which is analyzed
    :param team_folder: team name
    :param season: name of the season which is analyzed
    :return: returns a merged pandas dataframe object with stats per player per game
    """
    
    # create a base dataframe of all players
    join_df = pd.DataFrame(list(player_list), columns=['SPIELER'])

    header = ['TORE', '7M', r'%', 'TF', 'V', r"2'", 'D']
    header.remove(stat)

    # merge stats to the base dataframe using the date as column name
    for file in games_list:
        temp_df = pd.read_csv(f'{data_dir}/{team_folder}/{season}/{file}', encoding='utf-8').fillna(0)
        merged = pd.merge(join_df, temp_df, left_on='SPIELER', right_on='SPIELER', how='outer')
        merged = merged.drop(header, axis=1)
        merged.rename(columns={stat: str(file[:8])}, inplace=True)
        join_df = merged

    # sort columns: first is SPIELER, then sort according to date
    join_df = join_df.reindex(sorted(join_df.columns), axis=1)
    col = join_df.pop("SPIELER")
    join_df.insert(0, col.name, col)
    return join_df


def mergeStatsGoalie(games_list,player_list,stat,team_folder,season):
    """
    Helper function that merges goalie stats from different games to get a csv where stats per game per player are
    available.

    :param games_list: list of games that are to be merged
    :param player_list: list of all goalies that have played at least one game
    :param stat: string of the statistic which is analyzed
    :param team_folder: team name
    :param season: name of the season which is analyzed
    :return: returns a merged pandas dataframe object with stats per goalie per game
    """

    # create a base dataframe of all players
    join_df = pd.DataFrame(list(player_list), columns=['TORHÜTER'])

    header = [r'P/W','7M',r'%']
    header.remove(stat)

    # merge stats to the base dataframe using the date as column name
    for file in games_list:
        temp_df = pd.read_csv(f'{data_dir}/{team_folder}/{season}/{file}', encoding='utf-8').fillna(0)
        merged = pd.merge(join_df, temp_df, left_on='TORHÜTER', right_on='TORHÜTER', how='outer')#.fillna(-1)
        merged = merged.drop(header, axis=1)
        merged.rename(columns={stat: str(file[:8])}, inplace=True)
        join_df = merged

    # sort columns: first is SPIELER, then sort according to date
    join_df = join_df.reindex(sorted(join_df.columns), axis=1)
    col = join_df.pop("TORHÜTER")
    join_df.insert(0, col.name, col)

    return join_df


def write(input_dataframe, team_folder, season, stat):
    """
    Helper function that actually writes information to output csvs generated in output_csv()

    :param input_dataframe: the merged pandas dataframe from either mergeStatsOutfield or mergeStatsGoalie
    :param team_folder: name of the team being analyzed
    :param season: name of the season in which the games took place
    :param stat: name of the statistic represented in the input_dataframe
    :return: does not return anything, but saves output .csv files in output_csv/
    """

    print(f'writing data to ././output_csv/progress_data/{team_folder}/{season}/{stat}')
    input_dataframe.to_csv(f'././output_csv/progress_data/{team_folder}/{season}/{stat}', index=False)
    return f'././output_csv/progress_data/{team_folder}/{season}/{stat}'


def check_for_already_scraped_games(games, check_dir, gamenr_idx_from, gamenr_idx_to):
    """
    Helper function that checks for games which have already been scraped

    :param games: list of SHV game IDs
    :param check_dir: directory to check for games which have already been scraped
    :param gamenr_idx_from: starting index of game number in csv filename
    :param gamenr_idx_to: ending index of game number in csv filename
    :return:
    """

    existing_data = os.listdir(check_dir)
    existing_games = []

    for file in existing_data:
        game_nr = file[gamenr_idx_from:gamenr_idx_to]
        existing_games.append(eval(game_nr))

    remove = []
    for game in games:
        if eval(game) in existing_games:
            print(f'game #{game} has already been scraped, skipping...')
            remove.append(game)
        else:
            pass

    for element in remove:
        games.remove(element)

    return games


if __name__ == '__main__':
    scrapePlayerProgress()
