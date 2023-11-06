#!/usr/bin/env python
# coding: utf-8

# ### Gang Green All Time Stats
# Chris McAllister
# 
# #### This notebook gathers all the Oakland Hockey Stats for all 4 GG teams, for every season that which the website has data.
# 
# #### Oultine:
# 
# ##### 1) Import libraries
# ##### 2) Establish mapping of GG Team ID's in URL to Team Names (Gang Green 1, 2, etc.)
# ##### 3) Read in a CSV that converts SeasonIDs to the Season Name
# ##### 4) Establish an empty dataset of only the column header. We later append our data to this empty dataframe.
# ##### 5) For each GG team, loop over all the season that they have data on going back to 2007.
# ##### 6) Light data manipulation. Removing columns, create Points per Game metric, etc.
# ##### 7) Join dataset back to Team ID and Season ID tables so we can know what year / team name the IDs correspond to. 

# In[39]:


# 1) Import libraries. All we need is Pandas
import pandas as pd

# Don't truncate dataframes (ie show every column)
pd.set_option('display.max_columns', None)


# Ignore any warning messages. 
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from warnings import filterwarnings
filterwarnings('ignore')


# 2) Create simple mapping table that converts the Team ID to a Team Name.
gg_team_ids = [1843, 692, 4622, 4818]
gg_team_names = ['Gang Green 1', 'Gang Green 2', 'Gang Green 3', 'Gang Green 4']

team_dim = pd.DataFrame(zip(gg_team_ids, gg_team_names), columns = ['TeamID', 'Team Name'])


# 3) Create Mapping table for Season IDs too
season_dim = pd.read_csv('OaklandHockeySeasondDim.csv')


# 4) Establish empty dataframe to get the column names. Next we'll append each team-season combination to this df
team_id = 692
url = 'https://stats.sharksice.timetoscore.com/display-schedule?team='+str(team_id)+'&season=' + str(50) + '&league=27&stat_class=1'

# Establish base data frame so we can later append onto it
df = pd.read_html(url)
df[1].columns = df[1].columns.droplevel()

df_main = df[1].iloc[0:0]


# 5) For each GG team, loop over every season to grab their stats and append it to our big dataframe we made above.
# This is written very inefficiently and will be pretty slow. 
for team_id in gg_team_ids:

    for season_id in season_dim['SeasonID']:
        url = 'https://stats.sharksice.timetoscore.com/display-schedule?team='+str(team_id)+'&season=' + str(season_id) + '&league=27&stat_class=1'

        # There are gaps in season IDs (for example there's no season #34). 
        # This would cause an error when reading the URL so we need to handle that with the try / except code block below. 
        try:
            df = pd.read_html(url)
            season_dim = pd.read_csv('OaklandHockeySeasonDim.csv')
            # Remove first layer of column (that just say says 'Game Results')
            #df[0].columns = df[0].columns.droplevel()
            #df[0].head()

            df[1].columns = df[1].columns.droplevel()
            df[1]['SeasonID'] = int(season_id)
            df[1]['TeamID'] = int(team_id)
            

            df_main = pd.concat([df_main, df[1]])
            #df_main['SeasonID'] = season_id

        except:
            pass


# In[5]:


# 6) Data manipulation. Removing certain columns. Tweaking data types. Joing to our dimension tables. 

# Cast as integers so the join below works (otherwise it won't recognize 5.0 as 5, etc.)
df_main['SeasonID'] = df_main['SeasonID'].astype(int) 
df_main['TeamID'] = df_main['TeamID'].astype(int) 

# Convert season IDs (#40) to Season Name (Fall 2017)
df_final = pd.merge(left = df_main, right = season_dim, how = 'left', left_on = 'SeasonID', right_on = 'SeasonID')

# Only select necessarry columns
col = ['Name', '#', 'GP', 'Goals', 'Ass.', 'PPG', 'PPA', 'SHG', 'SHA', 'GWG',
       'GWA', 'PSG', 'ENG',  'PIMs', 'Hat', 'Pts', 'SeasonID', 'Season', 'Year', 'TeamID',
       'SeasonName']

df_final = df_final[col]

# Create a GPG and Pts per game metric. 
df_final['GPG'] = df_final['Goals'] / df_final['GP']
df_final['Pts_PG'] = df_final['Pts'] / df_final['GP']

df_final['SeasonID'] = df_final['SeasonID'].astype(int) 
df_final['TeamID'] = df_final['TeamID'].astype(int)


# Get team name from Team ID (GG 1, 3, etc.)
df_final_2 = pd.merge(left = df_final, right = team_dim, how = 'left', left_on = 'TeamID', right_on = 'TeamID')


# Ouput results to CSV
df_final_2.to_csv('OaklandHockeyData.csv', index = False)


# #### Begin Team Stats

df_teams_dim = pd.read_csv('Oakland_Team_Dim.csv')

dfs = []

for team in df_teams_dim['TeamID']:
    
    # Added in the try-except because I'm not sure how folded teams will be handled
    try:        
        url = 'https://stats.sharksice.timetoscore.com/display-schedule?team=' + str(team) + '&season=0&league=27&stat_class=1'

        # 3 is the goal diff table
        df_i = pd.read_html(url)[3]
        df_i.columns = df_i.columns.droplevel()
        df_i = df_i[df_i['Situation'] == 'Total']
        df_i['TeamID'] = team

        dfs.append(df_i)
    
    except: 
        pass
    
goal_diff_df = pd.concat(dfs)
goal_diff_df = pd.merge(left = goal_diff_df, right = df_teams_dim, how = 'left', on = 'TeamID')

col = ['Goals For', 'Goals Against', 'TeamName', 'Division']

goal_diff_df = goal_diff_df[col]
goal_diff_df['Goal Differential'] = goal_diff_df['Goals For'] - goal_diff_df['Goals Against']


df_final_2.to_csv('Oakland_Goal_Diff.csv', index = False)
    




