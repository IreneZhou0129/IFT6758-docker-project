import requests
import json
import pandas as pd
import logging
from collections import OrderedDict
import datetime
import os
import math
import csv

# import sys
# sys.path.append('../../../')

class GameClient:
    def __init__(self, game_id: int = 2021020329):
        self.game_id = game_id
        # pass
    
    
    def process_and_save_data(self):
        # print(game_id)
        response = requests.get(f"https://statsapi.web.nhl.com/api/v1/game/{self.game_id}/feed/live/")
        data = response.json()

        # print(data)

        json_data_local_path = 'm4_json_files'
        filename = f"{json_data_local_path}/{self.game_id}.json"
        # filename = f"{game_id}.json"

        dirname = os.path.dirname(filename)

        # print(dirname)

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        if not os.path.isfile(filename):
            # print(filename)
            # os.makedirs(dirname)
            # print('os.makedirs(dirname)')

            # write data to local
            with open(filename, 'w+') as f:
                json.dump(data, f, sort_keys=True, indent=4)
                print('saved json again')

            columns = ['eventIdx', 'game_id', 'Game Seconds', 'Game Period', 'X-Coordinate', 'Y-Coordinate', 
                       'Shot Distance', 'Shot Angle', 'Shot Type', 'Was Net Empty', 'Last Event Type', 'Last X-Coordinate',
                       'Last Y-Coordinate', 'Time from Last Event (seconds)', 'Distance from Last Event', 'Is Rebound',
                       'Change in Shot Angle', 'Speed', 'Is Goal']

            data = []

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

            f = open(f'{json_data_local_path}/{self.game_id}.json')

            # game_id = int(file[:-5])

            loaded_json = json.load(f)

            # print('loaded_json', loaded_json)

            all_plays = loaded_json['liveData']['plays']['allPlays']

            home_team = loaded_json['gameData']['teams']['home'].get('name')

            home_side = 'NA'
            if len(loaded_json['liveData']['linescore']['periods']) > 0:
                home_side = loaded_json['liveData']['linescore']['periods'][0]['home'].get('rinkSide')

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

                    is_rebound = True if last_event == 'Shot' and game_period == all_plays[i - 1]['about']['period'] else False

                    change_in_shot_angle = angle - prev_angle if is_rebound else 0

                    speed = distance_from_last_event / time_from_last_event if time_from_last_event != 0 else 0

                    #######################################################################################

                    row_data = [eventIdx, self.game_id, game_seconds, game_period, x_coor, y_coor, 
                                distance, angle, shot_type, int(is_net_empty), last_event, last_x_coor,
                                last_y_coor, time_from_last_event, distance_from_last_event, is_rebound, 
                                change_in_shot_angle, speed, int(event == 'Goal')]

                    if type(x_coor) == int and type(y_coor) == int and type(last_x_coor) == int and type(last_y_coor) == int:
                        data.append(row_data)

            # print('year', year)
            # print('count_jsons', count_jsons)

            # data['Shot Type'] = data['Shot Type'].astype('category')
            # data['Last Event Type'] = data['Last Event Type'].astype('category')
            df = pd.DataFrame.from_records(data)

            unique_shot_types = df.iloc[:, 8].unique()
            # print(unique_shot_types)
            df.iloc[:, 8].replace(to_replace=unique_shot_types,
                   value=list(range(len(unique_shot_types))),
                   inplace=True)

            unique_last_event_types = df.iloc[:, 10].unique()
            # print(unique_last_event_types)
            df.iloc[:, 10].replace(to_replace=unique_last_event_types,
                   value=list(range(len(unique_last_event_types))),
                   inplace=True)

            # print(df.dtypes)

            data = df.values.tolist()

            # create file path if it doesn't exist

            csv_data_local_path = 'm4_csv_files'
            filename = f'{csv_data_local_path}/{self.game_id}_categorical.csv'
            dirname = os.path.dirname(filename)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            # writing to csv file 
            with open(filename, 'w+') as csvfile: 
                # creating a csv writer object 
                csvwriter = csv.writer(csvfile) 

                # writing the fields 
                csvwriter.writerow(columns) 

                # writing the data rows 
                csvwriter.writerows(data)
                
                print('saved csv again')
        
#     def process_json_data():
        
        
#     def predict():
        
    
#     def store_probabilities():
        

# a = GameClient()
# a.process_and_save_data()



        
        