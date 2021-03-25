from lib.scraperPlayerProgress import *

#loading in the options file
teams_seasons = options.teams_seasons
teams = []

def scrapeGameProgression():
    # run firefox webdriver from executable path of your choice
    driver = webdriver.Chrome()

    #get team ids from options.py
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

    for team in teams:
        season = get_season(team)
        year_start = season.split(' ')[1].split('_')[0]
        year_finish = season.split(' ')[1].split('_')[1]

        team_name, games = findGamesPage(driver, team,year_start,year_finish)

        try:
            # Check which (if any) games have already been scraped, discard them
            existing_data = os.listdir(f'output_csv/gameProgressions/{get_team(team)}/{season}')
            existing_games = []
            for file in existing_data:
                game_nr = file[-10:-4]
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

        except Exception as e:
            print(e)

        # scrape the data
        for game in games:
            time.sleep(0.1)
            link = 'https://www.handball.ch/de/matchcenter/spiele/{}'.format(game)
            print(link)
            time.sleep(0.1)
            try:
                try:
                    progression, date = getGameProgression(link, driver)
                    writeProgression(progression, team, season, date, game)
                except Exception as e:
                    #TODO: fix issue where index is out of range for home or away team
                    print(e)

            except Exception as e:
                print(e)
                print(f'error. most likely the game ({game}) you are trying to download does not have stats available\nskipping...')

    print('\n', '-'*10)
    print('scraping successfully terminated, closing firefox...')
    driver.quit()


def getGameProgression(link, driver):
    driver.get(link)
    time.sleep(0.5)
    tab = driver.find_element_by_xpath('//*[@id="live-tab"]')
    tab.click()
    time.sleep(1.5)
    table = driver.find_element_by_xpath('//*[@id="live"]/div[2]/div[3]')
    table_content = table.get_attribute('innerText')
    date = driver.find_element_by_xpath('/html/body/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div[3]/span[1]').get_attribute('innerText')
    date = date.split(' ')[1][:-6]
    date = date.split('.')
    date = "_".join(reversed(date))
    print(date)

    return table_content, date


def writeProgression(progression, team, season, date, game):

    entries = progression.split('\n')
    team_home = entries[0]
    team_away = entries[1]
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
        #handle games that werent played (yet)
        print(e)


def divide_chunks(l, n):
    """takes a list and segments it into evenly sized chunks of length n"""

    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


if __name__ == "__main__":
    scrapeGameProgression()