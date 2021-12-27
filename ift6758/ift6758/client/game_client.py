import requests
import json
import pandas as pd
import logging
from collections import OrderedDict
import datetime
import os
import math
import csv
import numpy as np
from prettytable import PrettyTable


class GameClient:
    def __init__(self):
        # key: game_id, value: processed dataframe for up to what event has occurred live
        self.games_dataframes = {}
        self.shot_types = {'Wrist Shot': 0, 'Backhand': 1, 'Slap Shot': 2, 'Snap Shot': 3, 'Tip-In': 4, 'Deflected': 5, 'Wrap-around': 6, 'NA': 7}
        self.last_event_types = {'Hit': 0, 'Faceoff': 1, 'Takeaway': 2, 'Blocked Shot': 3, 'Giveaway': 4, 'Shot': 5, 'Missed Shot': 6, 'Goal': 7, 'Penalty': 8, 'Stoppage': 9}
    
    
    def process_and_predict_data(self, game_id):

        # game_id = int(game_id)
        # print(f"game_id type:{type(game_id)}")
        
        response = requests.get(f"https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live/")
        json_data = response.json()
        
        def get_distance_angle(shoot_left, x_coor, y_coor):
            if shoot_left == True:
                distance = math.sqrt((89 + x_coor) ** 2 + (y_coor) ** 2)
                if x_coor == -89:
                    if y_coor > 0:
                        angle = 0
                    elif y_coor < 0:
                        angle = 180
                    elif y_coor == 0:
                        angle = 90
                else:
                    if y_coor > 0:
                        angle = math.degrees(math.atan((89 + x_coor) / y_coor))
                    elif y_coor < 0:
                        angle = 180 - abs(math.degrees(math.atan((89 + x_coor) / y_coor)))
                    elif y_coor == 0:
                        angle = 90

            elif shoot_left == False:
                distance = math.sqrt((89 - x_coor) ** 2 + (y_coor) ** 2)
                if x_coor == 89:
                    if y_coor > 0:
                        angle = 180
                    elif y_coor < 0:
                        angle = 0
                    elif y_coor == 0:
                        angle = 90
                else:
                    if y_coor > 0:
                        angle = 180 - abs(math.degrees(math.atan((89 - x_coor) / y_coor)))
                    elif y_coor < 0:
                        angle = abs(math.degrees(math.atan((89 - x_coor) / y_coor)))
                    elif y_coor == 0:
                        angle = 90

            return distance, angle
        
        column_names = ['eventIdx', 'game_id', 'Game Seconds', 'Game Period', 'X-Coordinate', 'Y-Coordinate', 
                   'Shot Distance', 'Shot Angle', 'Shot Type', 'Was Net Empty', 'Last Event Type', 'Last X-Coordinate',
                   'Last Y-Coordinate', 'Time from Last Event (seconds)', 'Distance from Last Event', 'Is Rebound',
                   'Change in Shot Angle', 'Speed', 'Is Goal'] # deleted 'Team Name'
            
        ### first time pinging this game_id ##########
        if game_id not in self.games_dataframes:


            data = []
            
            team_names = []

            all_plays = json_data['liveData']['plays']['allPlays']

            home_team = json_data['gameData']['teams']['home'].get('name')

            home_side = 'NA'
            if len(json_data['liveData']['linescore']['periods']) > 0:
                home_side = json_data['liveData']['linescore']['periods'][0]['home'].get('rinkSide')

            angle = 0

            for i in range(len(all_plays)):
                event = all_plays[i]['result']['event']
                if event == 'Shot' or event == 'Goal':

                    # Q4.1 ################################################################################

                    game_period = all_plays[i]['about']['period']

                    period_time_mins, period_time_secs = all_plays[i]['about']['periodTime'].split(':')
                    game_seconds = ((int(game_period) - 1) * 1200) + (int(period_time_mins) * 60 + int(period_time_secs))

                    team_name = all_plays[i]['team']['name']

                    if home_team == team_name:
                        home_or_away = 'Home'
                    else:
                        home_or_away = 'Away'

                    eventIdx = all_plays[i]['about']['eventIdx']

                    x_coor = 'NA'
                    y_coor = 'NA'
                    if 'coordinates' in all_plays[i]:
                        x_coor = all_plays[i]['coordinates'].get('x')
                        y_coor = all_plays[i]['coordinates'].get('y')

                    x_coor = int(float(x_coor)) if bool(x_coor) and x_coor != 'NA' else False
                    y_coor = int(float(y_coor)) if bool(y_coor) and y_coor != 'NA' else False

                    prev_angle = angle

                    if x_coor and y_coor:
                        if home_side == 'right':                    
                            if home_or_away == 'Home':
                                if int(game_period) % 2 == 1:
                                    # shoot left
                                    distance, angle = get_distance_angle(True, x_coor, y_coor)

                                elif int(game_period) % 2 == 0:
                                    # shoot right
                                    distance, angle = get_distance_angle(False, x_coor, y_coor)
                            else:
                                if int(game_period) % 2 == 1:
                                    # shoot right
                                    distance, angle = get_distance_angle(False, x_coor, y_coor)

                                elif int(game_period) % 2 == 0:
                                    # shoot left
                                    distance, angle = get_distance_angle(True, x_coor, y_coor)

                        elif home_side == 'left':
                            if home_or_away == 'Home':
                                if int(game_period) % 2 == 1:
                                    # shoot right
                                    distance, angle = get_distance_angle(False, x_coor, y_coor)

                                elif int(game_period) % 2 == 0:
                                    # shoot left
                                    distance, angle = get_distance_angle(True, x_coor, y_coor)

                            else:
                                if int(game_period) % 2 == 1:
                                    # shoot left
                                    distance, angle = get_distance_angle(True, x_coor, y_coor)

                                elif int(game_period) % 2 == 0:
                                    # shoot right
                                    distance, angle = get_distance_angle(False, x_coor, y_coor)

                    shot_type = 'NA'
                    if 'secondaryType' in all_plays[i]['result']:
                        shot_type = all_plays[i]['result']['secondaryType']

                    is_net_empty = False
                    if event == 'Goal':
                        if 'emptyNet' in all_plays[i]['result']:
                            is_net_empty = all_plays[i]['result']['emptyNet']

                    # Q4.2 ################################################################################

                    last_event = all_plays[i - 1]['result']['event']

                    last_x_coor = 'NA'
                    last_y_coor = 'NA'
                    if 'coordinates' in all_plays[i - 1]:
                        last_x_coor = all_plays[i - 1]['coordinates'].get('x')
                        last_y_coor = all_plays[i - 1]['coordinates'].get('y')

                    last_x_coor = int(float(last_x_coor)) if bool(last_x_coor) and last_x_coor != 'NA' else False
                    last_y_coor = int(float(last_y_coor)) if bool(last_y_coor) and last_y_coor != 'NA' else False

                    last_game_period = all_plays[i - 1]['about']['period']

                    last_period_time_mins, last_period_time_secs = all_plays[i - 1]['about']['periodTime'].split(':')
                    last_event_game_seconds = ((int(last_game_period) - 1) * 1200) + (int(last_period_time_mins) * 60 + int(last_period_time_secs))
                    time_from_last_event = game_seconds - last_event_game_seconds

                    distance_from_last_event = math.sqrt(((x_coor - last_x_coor) ** 2) + ((y_coor - last_y_coor) ** 2))

                    # Q4.3 ################################################################################

                    is_rebound = 1 if last_event == 'Shot' and game_period == all_plays[i - 1]['about']['period'] else 0

                    change_in_shot_angle = angle - prev_angle if (is_rebound==1) else 0

                    speed = distance_from_last_event / time_from_last_event if time_from_last_event != 0 else 0

                    #######################################################################################

                    row_data = [eventIdx, game_id, game_seconds, game_period, x_coor, y_coor, 
                                distance, angle, self.shot_types[shot_type], int(is_net_empty), self.last_event_types[last_event], last_x_coor,
                                last_y_coor, time_from_last_event, distance_from_last_event, is_rebound, 
                                change_in_shot_angle, speed, int(event == 'Goal')]

                    if type(x_coor) == int and type(y_coor) == int and type(last_x_coor) == int and type(last_y_coor) == int:
                        data.append(row_data)
                        team_names.append(team_name)
                        # print('heyyy UWU', type(eventIdx), type(game_id), type(game_seconds), type(game_period), type(x_coor))
                        # break

            df = pd.DataFrame(np.array(data), columns=column_names)
            df['Team Name'] = team_names
            
            # print(f"------- game_client: {type(df.iloc[0,1])}")
            # print('df.dtypes', df.dtypes)
            # df = df.set_index('eventIdx')
            
            self.games_dataframes[game_id] = df
            
            self.games_dataframes[game_id].to_csv(f'{game_id}.csv')
        
            df_without_team_name = self.games_dataframes[game_id].drop(columns=['Team Name'])

            return df_without_team_name
        
        ### game_id has already been pinged before #####################
        else:
            curr_game = self.games_dataframes.get(game_id)
            
            current_eventIdx = curr_game.iloc[-1, curr_game.columns.get_loc('eventIdx')]
            
            data = []

            team_names = []
            
            all_plays = json_data['liveData']['plays']['allPlays']

            home_team = json_data['gameData']['teams']['home'].get('name')

            home_side = 'NA'
            if len(json_data['liveData']['linescore']['periods']) > 0:
                home_side = json_data['liveData']['linescore']['periods'][0]['home'].get('rinkSide')

            angle = 0

            for i in range(len(all_plays)):
                event = all_plays[i]['result']['event']
                # print('event', event)
                # print('type(int(all_plays[i][\'about\'][\'eventIdx\']))', type(int(all_plays[i]['about']['eventIdx'])))
                # print('type(current_eventIdx)', type(current_eventIdx))
                if event == 'Shot' or event == 'Goal' and int(all_plays[i]['about']['eventIdx']) > int(current_eventIdx):

                    # Q4.1 ################################################################################

                    game_period = all_plays[i]['about']['period']

                    period_time_mins, period_time_secs = all_plays[i]['about']['periodTime'].split(':')
                    game_seconds = ((int(game_period) - 1) * 1200) + (int(period_time_mins) * 60 + int(period_time_secs))

                    team_name = all_plays[i]['team']['name']

                    if home_team == team_name:
                        home_or_away = 'Home'
                    else:
                        home_or_away = 'Away'

                    eventIdx = all_plays[i]['about']['eventIdx']

                    x_coor = 'NA'
                    y_coor = 'NA'
                    if 'coordinates' in all_plays[i]:
                        x_coor = all_plays[i]['coordinates'].get('x')
                        y_coor = all_plays[i]['coordinates'].get('y')

                    x_coor = int(float(x_coor)) if bool(x_coor) and x_coor != 'NA' else False
                    y_coor = int(float(y_coor)) if bool(y_coor) and y_coor != 'NA' else False

                    prev_angle = angle

                    if x_coor and y_coor:
                        if home_side == 'right':                    
                            if home_or_away == 'Home':
                                if int(game_period) % 2 == 1:
                                    # shoot left
                                    distance, angle = get_distance_angle(True, x_coor, y_coor)

                                elif int(game_period) % 2 == 0:
                                    # shoot right
                                    distance, angle = get_distance_angle(False, x_coor, y_coor)
                            else:
                                if int(game_period) % 2 == 1:
                                    # shoot right
                                    distance, angle = get_distance_angle(False, x_coor, y_coor)

                                elif int(game_period) % 2 == 0:
                                    # shoot left
                                    distance, angle = get_distance_angle(True, x_coor, y_coor)

                        elif home_side == 'left':
                            if home_or_away == 'Home':
                                if int(game_period) % 2 == 1:
                                    # shoot right
                                    distance, angle = get_distance_angle(False, x_coor, y_coor)

                                elif int(game_period) % 2 == 0:
                                    # shoot left
                                    distance, angle = get_distance_angle(True, x_coor, y_coor)

                            else:
                                if int(game_period) % 2 == 1:
                                    # shoot left
                                    distance, angle = get_distance_angle(True, x_coor, y_coor)

                                elif int(game_period) % 2 == 0:
                                    # shoot right
                                    distance, angle = get_distance_angle(False, x_coor, y_coor)

                    shot_type = 'NA'
                    if 'secondaryType' in all_plays[i]['result']:
                        shot_type = all_plays[i]['result']['secondaryType']

                    is_net_empty = False
                    if event == 'Goal':
                        if 'emptyNet' in all_plays[i]['result']:
                            is_net_empty = all_plays[i]['result']['emptyNet']

                    # Q4.2 ################################################################################

                    last_event = all_plays[i - 1]['result']['event']

                    last_x_coor = 'NA'
                    last_y_coor = 'NA'
                    if 'coordinates' in all_plays[i - 1]:
                        last_x_coor = all_plays[i - 1]['coordinates'].get('x')
                        last_y_coor = all_plays[i - 1]['coordinates'].get('y')

                    last_x_coor = int(float(last_x_coor)) if bool(last_x_coor) and last_x_coor != 'NA' else False
                    last_y_coor = int(float(last_y_coor)) if bool(last_y_coor) and last_y_coor != 'NA' else False

                    last_game_period = all_plays[i - 1]['about']['period']

                    last_period_time_mins, last_period_time_secs = all_plays[i - 1]['about']['periodTime'].split(':')
                    last_event_game_seconds = ((int(last_game_period) - 1) * 1200) + (int(last_period_time_mins) * 60 + int(last_period_time_secs))
                    time_from_last_event = game_seconds - last_event_game_seconds

                    distance_from_last_event = math.sqrt(((x_coor - last_x_coor) ** 2) + ((y_coor - last_y_coor) ** 2))

                    # Q4.3 ################################################################################

                    is_rebound = 1 if last_event == 'Shot' and game_period == all_plays[i - 1]['about']['period'] else 0

                    change_in_shot_angle = angle - prev_angle if (is_rebound==1) else 0

                    speed = distance_from_last_event / time_from_last_event if time_from_last_event != 0 else 0

                    #######################################################################################

                    row_data = [eventIdx, game_id, game_seconds, game_period, x_coor, y_coor, 
                                distance, angle, self.shot_types[shot_type], int(is_net_empty), self.last_event_types[last_event], last_x_coor,
                                last_y_coor, time_from_last_event, distance_from_last_event, is_rebound, 
                                change_in_shot_angle, speed, int(event == 'Goal')]

                    if type(x_coor) == int and type(y_coor) == int and type(last_x_coor) == int and type(last_y_coor) == int:
                        data.append(row_data)
                        team_names.append(team_name)
                        # print('else heyyy UWU', type(eventIdx), type(game_id), type(game_seconds), type(game_period), type(x_coor))
                        # break

            df = pd.DataFrame(np.array(data), columns=column_names)
            df['Team Name'] = team_names

            # print(f"ELSE------- game_client: {type(df.iloc[0,1])}")
            # print('df.dtypes', df.dtypes)
            # df = df.set_index('eventIdx')
            
            self.games_dataframes[game_id].append(df)
            
            self.games_dataframes[game_id].to_csv(f'{game_id}.csv')
            
            df_without_team_name = self.games_dataframes[game_id].drop(columns=['Team Name'])
            
            # print('process_and_predict_data')
            # print(df_without_team_name.columns)

            return df_without_team_name

    
    def add_pred_probs_to_df(self, game_id, xG):
        xG = np.asarray(xG['response'])[:, 1].tolist()
        self.games_dataframes[game_id]['xG'] = xG
        # return self.games_dataframes[game_id]
        
        
    def get_xG_table(self, game_id):
        response = requests.get(f"https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live/")
        json_data = response.json()
        
        all_plays = json_data['liveData']['plays']['allPlays']
        
        game_period = all_plays[-1]['about']['period']
        game_period_time_remaining = all_plays[-1]['about']['periodTimeRemaining']
        
        home_team = json_data['gameData']['teams']['home'].get('name')
        away_team = json_data['gameData']['teams']['away'].get('name')
        
        df = self.games_dataframes[game_id]
        home_team_indices = df.index[df['Team Name'] == home_team].tolist()
        away_team_indices = df.index[df['Team Name'] == away_team].tolist()
        home_sum_xG = df.iloc[home_team_indices, df.columns.get_loc('xG')].sum()
        away_sum_xG = df.iloc[away_team_indices, df.columns.get_loc('xG')].sum()
        
        t = PrettyTable([f'Period: {game_period}', f'Time Left: {game_period_time_remaining}'])
        t.add_row(['Home Team', 'Away Team'])
        t.add_row([home_team, away_team])
        t.add_row([home_sum_xG, away_sum_xG])
        
        return t
        

# a = GameClient()
# a.process_and_predict_data(2021020329)
# t = a.get_xG_table(2021020329)
# print(t)