from lib.plotterPlayerProgress import plotPlayerProgress
from lib.plotterPlayerStats import plotPlayerStats
from lib.scraperPlayerProgress import scrapePlayerProgress
from lib.scraperPlayerStats import scrapePlayerStats
from lib.scraperGameProgression import scrapeGameProgression
from lib.plotterGameProgression import plotGameProgressions
from datetime import datetime
import options


def handballStats():
    """Executes HandballStats according to settings in options.py"""

    start = datetime.now()
    print(f'initiating handballStats with the following parameters:')
    #print(help(options))

    # --------------------------------
    # unfinished stuff

    # print("\n", "-"*30, "\n", "Scraping Player Stats", "\n", "-"*30, "\n")
    # scrapePlayerStats()

    # print("\n", "-"*30, "\n", "Plotting Player Stats", "\n", "-"*30, "\n")
    # plotPlayerStats()
    # --------------------------------

    if options.scrapePlayerProgress:
        print("\n", "-" * 30, "\n", "Scraping Player Progress", "\n", "-" * 30, "\n")
        scrapePlayerProgress()

    if options.plotPlayerProgress:
        print("\n", "-" * 30, "\n", "Plotting Player Progress", "\n", "-" * 30, "\n")
        plotPlayerProgress()

    if options.scrapeGameProgressions:
        print("\n", "-" * 30, "\n", "Scraping Game Progression", "\n", "-" * 30, "\n")
        scrapeGameProgression()

    if options.plotGameProgressions:
        print("\n", "-" * 30, "\n", "Plotting Game Progression", "\n", "-" * 30, "\n")
        plotGameProgressions()

    end = datetime.now()
    print(f'done. elapsed time: {end - start}')


if __name__ == '__main__':
    handballStats()