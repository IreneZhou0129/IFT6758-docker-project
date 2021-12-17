from comet_ml import Experiment
from comet_ml import API

import pandas as pd

# Miilestone 2 Q4 DataFrame
df = pd.read_csv('/Users/xiaoxinzhou/Documents/IFT6758_M2_CSV_data/all_data_categorical.csv')

# Comet account API key
key = 'I3rjeTiik3391gTYjiRDDbq8R'
api = API(key)

# Models paths schemas
comet_config = {'workspace': 'xiaoxin-zhou', \
                'model': 'decision-tree-approach-2', \
                'version': '1.0.0'}

filename_dict = {
    'models':{
        'decision-tree':{
            '1.0.2': 'approach_3.pkl',
        },
        'decision-tree-approach-2':{
            '1.0.0': 'approach_2.pkl'
        },
        # As David mentioned in office hour, he mainly looking for 'M2 Q4 advanced features'.
        # 'logreg-distance':{
        #     '1.0.0': 'models\log_reg\log_reg_dist.pkl',
        #     'features': ['Distance from Net']
        # },
        # 'logreg-angle':{
        #     '1.0.0': 'models\log_reg\log_reg_angle.pkl',
        #     'features': ['Angle from Net']
        # },
        # 'logreg-both':{
        #     '1.0.0': 'models\log_reg\log_reg_both.pkl',
        #     'features': ['Distance from Net', 'Angle from Net']
        # },
        'xgboost-5-2':{
            '1.0.3': 'q5_2_tuned.json', 
        },
        'xgboost-model-var-threshold':{
            '1.0.1': 'q5_3_var_threshold.json'
        },
        'xgboost-model-selectkbest':{
            '1.0.2': 'q5_3_selectKbest.json'
        },
        'xgboost-model-extratree':{
            '1.0.1': 'q5_3_extratree.json'
        },
        'xgboost-model-selectfrommodel':{
            '1.0.1': 'q5_3_selectfrommodel.json'
        },
        'xgboost-model-rfe':{
            '1.0.1': 'q5_3_rfe.json'
        },
    }
}

features_dict = {
    'models\log_reg\log_reg_dist.pkl': ['Distance from Net'],
    'models\log_reg\log_reg_angle.pkl': ['Angle from Net'],
    'models\log_reg\log_reg_both.pkl': ['Distance from Net', 'Angle from Net']
}



