# Configuration file for the handballStats.py script

# --------------------GENERAL OPTIONS-------------------------------------
# Game Progressions
scrapeGameProgressions = False
plotGameProgressions = False

# Player Progress
scrapePlayerProgress = True
plotPlayerProgress = False

# Player Stats (not fully implemented yet)
scrapePlayerStats = False
plotPlayerStats = False
# -----------------------------------------------------------------------------


# --------------------TEAM/SEASONS SELECTION-------------------------------------
# SHV-Numbers needed to get the right data. Adjust teams and seasons being processed here:

teams_seasons = {
    "Wacker Thun U15 Elite": {"Saison 22_23":[35207]},
    "Wacker Thun U17 Elite": {"Saison 22_23":[35200]},
    "Wacker Thun NLA": {"Saison 22_23":[35196]}
}

# old configurations
# teams_seasons = {'Wacker Thun U15 Elite':{'Saison 20_21':[32054],'Saison 19_20':[30639],'Saison 18_19':[28999]},
#                 'Wacker Thun U17 Elite':{'Saison 20_21':[31846],'Saison 19_20':[30635],'Saison 18_19':[29811]},
#                 'Wacker Thun U19 Elite':{'Saison 20_21':[31823],'Saison 19_20':[30371], 'Saison 18_19':[28998]},
#                 'Wacker Thun NLA':{'Saison 20_21':[31821],'Saison 19_20':[30644],'Saison 18_19':[28972], 'Saison 17_18':[27795]},
#                 'TV Steffisburg NLB':{'Saison 20_21':[32296],'Saison 19_20':[31092], 'Saison 18_19':[29304]},
#                 'Wacker Thun 1.Liga':{'Saison 20_21':[31822],'Saison 19_20':[30370], 'Saison 18_19':[28973]}
#                 }

# teams_seasons = {'TV Steffisburg 3': {'Saison 19_20':[31089],'Saison 18_19':[29306]}
#                 }
# -----------------------------------------------------------------------------


# --------------------XPATHS FOR SCRAPERS-------------------------------------
# xpaths to information relevant to the scrapers

xpaths = {"playerProgress":{"team_name": r"/html/body/div[3]/div[3]/div/div/div[2]/div/div[2]/h1",
                            "games_button": r'//*[@id="games-tab"]',
                            "first_date": r'//*[@id="dateFromGames_1"]',
                            "second_date": r'//*[@id="dateToGames_1"]',
                            "click_away": r'//*[@id="games"]/div/div[1]/h2',
                            "stats_tab": r'//*[@id="stats-tab"]',
                            "game_date": r'/html/body/div[3]/div[1]/div[1]/div/div/div[2]/div[2]/div[3]/span[1]',
                            "left_table": r'//*[@id="stats"]/div[2]/div[3]/div[1]/div/table',
                            "right_table": r'//*[@id="stats"]/div[2]/div[3]/div[2]',
                            "left_team": r'//*[@id="stats"]/div[2]/div[3]/div[1]/div/table/thead[1]/tr/td/span',
                            "right_team": r'//*[@id="stats"]/div[2]/div[3]/div[2]/div/table/thead[1]/tr/td/span',
                            "league": r'/html/body/div[3]/div[1]/div[2]/div/div/div[6]/p',
                            "date_info": ".//td[1]/span[1]"
                            },
          "gameProgressions":{"tab": r'//*[@id="live-tab"]',
                              "table": r'//*[@id="live"]/div[3]/div[3]',
                              "date": r'/html/body/div[3]/div[1]/div[1]/div/div/div[2]/div[2]/div[3]/span[1]'
                              }
          }
# -----------------------------------------------------------------------------
