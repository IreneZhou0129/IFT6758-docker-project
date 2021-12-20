import requests
import json
import pandas as pd
import logging
from collections import OrderedDict
import datetime



class GameClient:
    def __init__(self):
        
        self.game_data_dict=OrderedDict()
        self.currentTime=pd.to_datetime(datetime.datetime.now())
        self.BASE_URL = "https://statsapi.web.nhl.com"
        self.SCHEDULE_URL = self.BASE_URL + "/api/v1/schedule"
        self.game_data_df=pd.DataFrame()

        
        
    def q1 (self,game_id : str = 2021020329 ,append=True):
        if game_id not in self.game_data_dict:
            response=requests.get(f'https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live/')
            if response.reason=="OK":
                df = pd.json_normalize(response.json())
                if append:
                    self.game_data_dict[game_id]=df
                    self.game_data_df=pd.concat((self.game_data_df,df))
                return(response,df)
        else :
            print("this game data already exist in game data dict")
            
            
            
        
            
    def q2 (self,start_date=None, end_date=None):
        games=self.list_game(start_date, end_date)
        games_id=games.game_id.values
        
        games_id1=self.checkـexisting(games_id)
        
        df_lst=[]
        for game_id in games_id1:
            df_lst.append(self.q1(str(game_id),append=False)[1])
            
        res=pd.concat(df_lst)
        self.game_data_df=pd.concat((self.game_data_df,res))
        return(a.game_data_df.set_index("gamePk").loc[games_id].reset_index())


    
    def checkـexisting (self,games_id):
        return(set(games_id)-set(self.game_data_df.gamePk.values))
        
        

    def list_game(self,start_date=None, end_date=None):
        if start_date is None:
            start_date = str(datetime.date.today())
        if end_date is None:
            end_date = str(datetime.date.today())
        
        resp = requests.get(self.SCHEDULE_URL, params={"startDate": start_date, "endDate": end_date})
        data = resp.json()
        res=[self.game_summary(game) for date in data["dates"]for game in date["games"]]
        
        return (pd.DataFrame.from_dict(res))
            
    
    def game_summary(self,gs):
        return {"date": gs["gameDate"][:10],
                "game_id": gs["gamePk"],
                "home_team": gs["teams"]["home"]["team"]["name"],
                "home_score": gs["teams"]["home"]["score"],
                "away_team": gs["teams"]["away"]["team"]["name"],
                "away_score": gs["teams"]["away"]["score"],
                "season": gs["season"],
                "game_state": gs["status"]["detailedState"]}
        
            


# a=GameClient()
# a.q1()
# a.q2()




        
        