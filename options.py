# Configuration file for the handballStats.py script

# --------------------GENERAL OPTIONS-------------------------------------
# Game Progressions
scrapeGameProgressions = True
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

teams_seasons = {'Wacker Thun U15 Elite':{'Saison 20_21':[32054]},
                 'Wacker Thun U17 Elite':{'Saison 20_21':[31846]},
                 'Wacker Thun U19 Elite':{'Saison 20_21':[31823]},
                 'TV Steffisburg NLB':{'Saison 20_21':[32296]},
                 'Wacker Thun NLA':{'Saison 20_21':[31821]}
                 }
# -----------------------------------------------------------------------------



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
