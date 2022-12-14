from lib.scraperPlayerProgress import scrapePlayerProgress
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
        try:
            print("\n", "-" * 30, "\n", "Scraping Player Progress", "\n", "-" * 30, "\n")
            scrapePlayerProgress()
        except Exception as e:
            print(f"ERROR: Could not scrape PlayerProgress, exception: {e}")

    if options.plotPlayerProgress:
        print("\n", "-" * 30, "\n", "Plotting Player Progress", "\n", "-" * 30, "\n")
        plotPlayerProgress()

    if options.scrapeGameProgressions:
        try:
            print("\n", "-" * 30, "\n", "Scraping Game Progression", "\n", "-" * 30, "\n")
            scrapeGameProgression()
        except Exception as e:
            print(f"ERROR: Could not scrape GameProgressions, exception: {e}")
            print("If Exception was 'Kader', there might not be stats for this game")

    if options.plotGameProgressions:
        print("\n", "-" * 30, "\n", "Calculating Median Performance", "\n", "-" * 30, "\n")
        plotGameProgressions()

    end = datetime.now()
    print()
    print('#'*10)
    print(f'done. elapsed time: {end - start}')
    print('#' * 10)


if __name__ == '__main__':
    handballStats()