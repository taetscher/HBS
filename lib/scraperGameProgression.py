from lib.scraperPlayerProgress import *

#loading in the options file
teams_seasons = options.teams_seasons
xpaths = options.xpaths["gameProgressions"]


def scrapeGameProgression():
    """
    Function that handles scraping of game progression statistics according to options.py

    :return: does not return, saves output files to output_csv/gameProgressions
    """

    # run firefox webdriver from executable path of your choice
    driver = webdriver.Chrome()

    #get team ids from options.py
    teams = []
    for season in teams_seasons.values():
        for id in season.values():
            teams.extend(id)

    # check if output directory already exists, create new one if not
    for team in teams:
        try:
            print(f'creating new directories for team {get_team(team)} and season {get_season(team)}...')
            os.makedirs(f'././output_csv/gameProgressions/{get_team(team)}/{get_season(team)}', exist_ok=False)
            os.makedirs(f'././output_png/gameProgressions/{get_team(team)}/{get_season(team)}', exist_ok=False)

        except OSError:
            print(f'directories for team {get_team(team)} and season {get_season(team)} already exist, skipping...\n')

    #iterate over teams to scrape
    for team in teams:
        season = get_season(team)
        year_start = season.split(' ')[1].split('_')[0]
        year_finish = season.split(' ')[1].split('_')[1]

        team_name, games = findGamesPage(driver, team,year_start,year_finish)

        try:
            # Check which (if any) games have already been scraped, discard them
            check_dir = f'output_csv/gameProgressions/{get_team(team)}/{season}'
            games = check_for_already_scraped_games(games, check_dir, -10, -4)
        except Exception as e:
            print('Error while checking future games to scrape: ', e)

        # scrape the data
        for game in games:
            time.sleep(0.1)
            link = 'https://www.handball.ch/de/matchcenter/spiele/{}'.format(game)
            print('\n', link)
            time.sleep(0.1)
            try:
                try:
                    progression, date = getGameProgression(link, driver)
                    writeProgression(progression, team, season, date, game)
                except Exception as e:
                    # TODO: fix issue where index is out of range for home or away team
                    print('Error while getting game progression or writing game progression: ', e)

            except Exception as e:
                print(e)
                print(f'error. most likely the game ({game}) you are trying to download does not have stats available\nskipping...')

    print('\n', '-'*10)
    print('scraping successfully terminated, closing webdriver...')
    driver.quit()


def getGameProgression(link, driver):
    """
    Gets game progression data

    :param link: link to the game to get game progression from
    :param driver: selenium webdriver object
    :return: table_content, the actual game progression information; date, the date the game was played
    """

    driver.get(link)
    time.sleep(0.5)
    tab = driver.find_element_by_xpath(xpaths['tab'])
    tab.click()
    time.sleep(1.5)
    table = driver.find_element_by_xpath(xpaths['table'])
    table_content = table.get_attribute('innerText')
    date = driver.find_element_by_xpath(xpaths['date']).get_attribute('innerText')
    date = date.split(' ')[1][:-6]
    date = date.split('.')
    date = "_".join(reversed(date))

    return table_content, date


def writeProgression(progression, team, season, date, game):
    """
    Writes game progression data to csv file

    :param progression: the progression data gained with getGameProgression
    :param team: the SHV team identification number (season-specific!)
    :param season: the season corresponding to the SHV-ID in options.py
    :param date: the date gained with getGameProgression
    :param game: the SHV game number of the game scraped
    :return: does not return anything, but saves the output to output_csv/gameProgressions
    """

    entries = progression.split('\n')
    team_home = entries[0].replace('/', '&')
    team_away = entries[1].replace('/', '&')
    course = entries[2:]
    rows = list(divide_chunks(course,4))
    time_score = []

    for row in rows:
        for entry in row:
            if ':' in entry:
                time_score.append(entry)

    time_score = list(divide_chunks(time_score, 2))

    try:
        with open(f'././output_csv/gameProgressions/{get_team(team)}/{season}/{date}_{team_home.replace(".", "")}_{team_away.replace(".", "")}_{game}.csv',
                  'wb') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['timestamp', 'score'])
            for row in time_score:
                writer.writerow(row)
            outfile.close()

    except Exception as e:
        print('Error in writeProgression:', e)


def divide_chunks(l, n):
    """takes a list and segments it into evenly sized chunks of length n"""

    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


if __name__ == "__main__":
    scrapeGameProgression()