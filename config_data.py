from comet_ml import Experiment
from comet_ml import API

# Comet account API key
key = 'I3rjeTiik3391gTYjiRDDbq8R'
api = API(key)

# Models paths schemas
comet_config = {'workspace': 'xiaoxin-zhou', \
                'model': 'logreg-distance', \
                'version': '1.0.0'}

filename_dict = {
    'models':{
        'decision-tree':{
            '1.0.2': 'approach_3.pkl',
            '1.0.3': '',
            '1.0.4': '',
        },
        'logreg-distance':{
            '1.0.0': 'models\log_reg\log_reg_dist.pkl',
            'features': ['Distance from Net']
        }
    }
}

features_dict = {
    'models\log_reg\log_reg_dist.pkl': ['Distance from Net'],
}





