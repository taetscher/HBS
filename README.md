# handballStats

Have a look at this repo's <a href="https://taetscher.github.io/HBS/index.html" target="blank">gh-pages page</a>!

This repository was created for me to learn about web scraping and git/github flow.
If you have any comments, ideas for improvement, let me know!

These scripts allow you to scrape data from <a href="https://www.handball.ch/de/matchcenter/" target="blank">handball.ch</a>. Please be aware the scraper built in this repository is made to scrape data from games which were recorded using the <a href="https://www.handball.ch/de/matchcenter/liveticker/" target="blank">liveticker</a> feature. Other games cannot be analyzed with it currently. At this point, only the performance-oriented teams of <a href="https://wackerthun.ch/de/" target="blank">Wacker Thun</a> are analyzed, however through adjustment of `options.py`, any team playing under the <a href="https://www.handball.ch/de/matchcenter/" target="blank">Swiss Handball Federation</a> may be analyzed.

Using the github pages page, data gained this way can be visualized for better understanding and analysis. Here's an example:
![Example of Visualized Game Progression](https://user-images.githubusercontent.com/24844442/112179972-6d325780-8bfb-11eb-9592-7d4dc0af0368.png)


Currently I have a Raspberry Pi set up which updates the data in the following intervals:
| Update Day | Update Hours      |
|------------|-------------------|
| Wednesday  | 22:00pm - 24:00pm |
| Saturday   | 22:00pm - 24:00pm |
| Sunday     | 22:00pm - 24:00pm |
