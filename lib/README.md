# Overview of all the Scripts used for this Scraper/Plotter


## Scripts handling the Data-Scraping Part
For scraping the data from <a href="https://www.handball.ch/de/" target="blank">handball.ch</a> I used <a href="https://www.selenium.dev/projects/" target="blank">Selenium</a>.
+ ###### scraperGameProgression.py
+ ###### scraperPlayerProgress.py
+ ###### scraperPlayerStats.py

## Scripts handling the Plotting Part
<a href="https://matplotlib.org/" target="blank">Matplotlib</a> and <a href="https://pandas.pydata.org/" target="blank">Pandas</a> were used in all of these to generate the plots in <a href="https://github.com/taetscher/handballStats/tree/master/output_png" target="blank">output_png</a>
+ ###### plotterGameProgression.py
+ ###### plotterPlayerProgress.py
+ ###### plotterPlayerStats.py

## The Scraper itself (handballStats.py)
The scraper itself built modularly: if you don't need certain parts to be run, you can comment them out.

## statistician.py (in root folder)
This is a script used to automate the data scraping part of this whole operation
