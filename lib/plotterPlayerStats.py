import matplotlib.pyplot as plt
import pandas as pd
from pandas.core.groupby.groupby import DataError
import os
import numpy as np

def find_min(inframe):
    minimum = inframe.min()
    return minimum

def find_max(inframe):
    maximum = inframe.max()
    return maximum

def plotPlayerStats():
    indir = os.listdir('../playerStats_data')

    for file in indir:
        infile = file[:-4]
        group = infile.split('_')[1:]
        s = '_'
        group = s.join(group)
        print('\n\n\n')
        print('reading in... ' + infile)

        df = pd.read_csv('./playerStats_data/' + infile + '.csv')
        # df = df.drop(['yellowCards','2mins','redCards'], axis=1 )

        try:
            n = 20
            goalsPerGame = df.groupby(['team'])['goalsPerGame'].mean().sort_values(ascending=False)
            suspensions = df.groupby(['team'])['2mins'].mean().sort_values(ascending=False)
            yellows = df.groupby(['team'])['yellowCards'].mean().sort_values(ascending=False)
            reds = df.groupby(['team'])['redCards'].sum().sort_values(ascending=False)
            goalGetters = df.sort_values('goalsPerGame', ascending=False)
            goalGetters = goalGetters.head(n)
            dangerousAttacks = goalGetters.groupby(['team']).count().sort_values('playerName', ascending=False)

            # print(goalsPerGame.head(10))
            #print(suspensions.head(20))
            #print(yellows.head(20))
            #print(reds.head(20))

            goalsPerGame.plot(x='teams', y='goalsPerGame', kind='bar', zorder=100)
            plt.title('Mean amount of Goals per Player per Team per Game\n{}'.format(group))
            plt.yticks(np.arange(find_max(goalsPerGame),step=0.25))
            plt.ylim(bottom=find_min(goalsPerGame)-0.25)
            plt.grid(b=True, zorder=0, linestyle='--')
            plt.tight_layout()
            plt.savefig('./output_png/{}_meanGoalsPerPlayerPerTeamPerGame.png'.format(group))
            plt.close('all')

            suspensions.plot(x='teams', y='2mins', kind='bar', zorder=100)
            plt.title('Mean amount of Suspensions per Player per Team\n{}'.format(group))
            plt.yticks(np.arange(find_max(suspensions), step=0.5))
            plt.ylim(bottom=find_min(suspensions) - 1)
            plt.grid(b=True, zorder=0, linestyle='--')
            plt.tight_layout()
            plt.savefig('./output_png/{}_meanSuspensionsPerPlayerPerTeam.png'.format(group))
            plt.close('all')

            yellows.plot(x='teams', y='yellowCards', kind='bar', zorder=100)
            plt.title('Mean amount of Yellow Cards per Player per Team\n{}'.format(group))
            plt.yticks(np.arange(find_max(yellows), step=0.5))
            plt.ylim(bottom=find_min(yellows) - 1)
            plt.grid(b=True, zorder=0, linestyle='--')
            plt.tight_layout()
            plt.savefig('./output_png/{}_meanYellowCardsPerPlayerPerTeam.png'.format(group))
            plt.close('all')

            reds.plot(x='teams', y='redCards', kind='bar', zorder=100)
            plt.title('Sum of Red Cards per Team\n{}'.format(group))
            plt.yticks(np.arange(find_max(reds), step=0.5))
            plt.ylim(bottom=find_min(reds))
            plt.grid(b=True, zorder=0, linestyle='--')
            plt.tight_layout()
            plt.savefig('./output_png/{}_redCardsPerTeam.png'.format(group))
            plt.close('all')

            goalGetters.plot(x='playerName', y='goalsPerGame', kind='bar', zorder=100)
            plt.title('{} Top Scorers in Group\n{}'.format(n, group))
            plt.yticks(np.arange(find_max(goalGetters['goalsPerGame']), step=0.5))
            plt.ylim(bottom=find_min(goalGetters['goalsPerGame']) - 0.5)
            plt.grid(b=True, zorder=0, linestyle='--')
            plt.tight_layout()
            plt.savefig('./output_png/{}_{}topGoalgetters.png'.format(group,n))
            plt.close('all')

            dangerousAttacks.plot(y='goalsPerGame', kind='bar', zorder=100)
            plt.title('Count of Team in top {} Goal Scorers\n{}'.format(n, group))
            plt.yticks(np.arange(find_max(dangerousAttacks['playerName']), step=1))
            plt.ylim(bottom=find_min(dangerousAttacks['playerName']) - 1)
            plt.grid(b=True, zorder=0, linestyle='--')
            plt.tight_layout()
            plt.savefig('./output_png/{}_mostDangerousAttacks.png'.format(group))
            plt.close('all')

        except DataError as e:
            print('ERROR: {}'.format(e))
            print('The season you are looking at probably does not have player stats (yet/anymore)')
            print('Looked specifically at group {}'.format(group))
            print('\n\n\n')
            continue

if __name__ == '__main__':
    plotPlayerStats()