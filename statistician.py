from git import Repo
from handballStats import handballStats
from datetime import datetime
import time
import sys
import os
import smtplib
import ssl
import json


def statistician():
    """
    Runs handballStats on Wednesdays, Saturdays and Sundays between 10:00 and 23:00 pm
    :return: does not return anything, saves output_csvs and pushes changes to github
    """

    while True:

        # check if it is wednesday, saturday or sunday and between 22:00 and 24:00
        start = datetime.now()
        today = datetime.now().weekday()
        time = datetime.now().time().strftime("%H:%M:%S")

        if (today in (2,5,6)) and (int(time.split(':')[0]) in range(10,24,1)):
            interval = 45
            print(f'it is {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}, and I shall get statistics...')
            
            # scrape data
            try:
                handballStats()
                print('successfully scraped the stats')
            except Exception as e:
                print(e)
                log(f'Error @ {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}', e)
                emailAlert(e)

            sleep_minutes(0.1)
            
            # clean up the Gameprogressions Folder (kick out games, that have not been played yet"
            try:
                print('getting rid of games which are played in the future...')
                cleanupGameProgressions()
            except Exception as e:
                print(e)
                log(f'Error @ {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}', e)
                emailAlert(e)
                sys.exit()
            
            sleep_minutes(0.1)
            
            # push updates to github
            print('-' *15, '\npushing to origin...')
            try:
                git_push()
            except Exception as e:
                print(e)
                log(f'Error @ {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}', e)
                emailAlert(e)
                sys.exit()
                
        else:
            # if its a day for updates, set interval to 1h, otherwise 2h
            if today in (2,5,6):
                interval = 60
            else:
                interval = 240
            
            print(f'i sleep @ {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}')
            try:
                print('housekeeping...')
                cleanupGameProgressions()
                print('house kept :)')
            except Exception as e:
                print(e)
                log(f'Error @ {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}', e)
                emailAlert(e)
                sys.exit()

        # wait for 45 minutes before checking again
        end = datetime.now()
        log(f'Finished a run which took {end-start}')
        print('-' * 15)
        sleep_minutes(interval)


def sleep_minutes(minutes):
    """
    sleeps the execution of a program for the amount of minutes specified
    :param minutes: amount of minutes to sleep the execution of the program
    :return: executes time.sleep with the specified amount of minutes
    """

    time.sleep(minutes * 60)


def git_push():
    """
    pushes changes to the git repo, if there have been changes
    :return: does not return anything, pushes to remote github repo
    """

    PATH_OF_GIT_REPO = r'.git'  # make sure .git folder is properly configured

    try:
        repo = Repo(PATH_OF_GIT_REPO)
        # add all changes
        repo.git.add(A=True)
        status = repo.git.status()
        diff = repo.index.diff('HEAD')
        print(status)

        if len(diff)>0:
            # if there are changes in the files, push changes to github
            COMMIT_MESSAGE = f'statistician @ {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'
            print(f'commit message: {COMMIT_MESSAGE}')
            repo.index.commit(COMMIT_MESSAGE)
            origin = repo.remote(name='origin')
            origin.push()
            print('push successful')
        else:
            print('nothing to push, skipping...')

    except Exception as e:
        print('Error while pushing to remote repository (in git_push): ')
        print(e)
        
        
def cleanupGameProgressions():
    """
    Helper function. Gets rid of csvs from games that have not even been played yet
    :return: does not return, housekeeping function
    """
    
    gp_path = './output_csv/gameProgressions'
    
    teams = os.listdir(gp_path)
    
    for team in teams:
        dir_path = f'{gp_path}/{team}'
        seasons = os.listdir(dir_path)
        for season in seasons:
            g_path = f'{dir_path}/{season}'
            games = os.listdir(g_path)
            
            for game in games:
                
                #check if game is played in the future, if so delete file
                game_d = game[:8].split('_')
                game_d[0] = '20'+game_d[0]
                game_d.reverse()
                game_date = '.'.join(game_d)
                current_date = datetime.now().strftime('%d.%m.%Y')
                
                t_format = '%d.%m.%Y'
                
                game_played = datetime.strptime(game_date, t_format)
                today = datetime.strptime(current_date, t_format)
                
                #if the game in question is played in the future, delete the csv
                if game_played > today or game.split('_')[4].isspace():
                    os.remove(f'{g_path}/'+game)


def emailAlert(message):
    """
    sends error message to let me know if statistician failed somehow
    :param message: string message to send
    :return: sends message via email
    """

    # load credentials
    with open('gmail.credentials') as cred:

        credentials = json.load(cred)
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        gmail_acc = credentials['user']
        pw = credentials['pw']

        # define receiving account
        receiver = credentials['receiver']
        cred.close()

    # construct message
    msg = f'@{timestamp}\n' \
        f'statistician.py @ raspberry failed. Error message:\n{"-"*10}\n\n' \
        f'{message}'


    # set up email
    port = 465
    smtp_server = "smtp.gmail.com"
    context = ssl.create_default_context()

    # send email
    print(f'Sending email about crash to {receiver}...')

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(gmail_acc, pw)
        server.sendmail(gmail_acc, receiver, msg)
        server.quit()

    print(f'Sent email from {gmail_acc} to {receiver}')


def log(message, errormessage=None):
    """
    Logs messages to a logfile, for debugging
    :param message: string to log
    :param errormessage: (voluntary) error message
    :return: does not return, logs to file
    """

    with open('handballstats.log', 'a') as logfile:
        logfile.write('-'*10)
        logfile.write(f'\n log @{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n')
        logfile.write(message)
        if errormessage is not None:
            logfile.write('\n')
            logfile.write('#'*10)
            logfile.write(errormessage)
            logfile.write('#' * 10)
        logfile.write('-'*10)
        logfile.write('\n\n')


if __name__ == '__main__':
    statistician()