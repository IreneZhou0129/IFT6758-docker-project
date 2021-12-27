"""
If you are in the same directory as this file (app.py), you can run run the app using gunicorn:
    
    $ gunicorn --bind 0.0.0.0:<PORT> app:app

gunicorn can be installed via:

    $ pip install gunicorn

"""

# Basic Python libs
import os
import joblib # https://joblib.readthedocs.io/en/latest/
import logging
from pathlib import Path

# App libs
from flask import Flask, jsonify, request, abort

# Data science libs
import pickle
import sklearn
import numpy as np
import pandas as pd
import xgboost as xgb
from comet_ml import API
from comet_ml import Experiment

# Cutomized libs
import ift6758
from config_data import api, \
                        comet_config, \
                        filename_dict


LOG_FILE = os.environ.get("FLASK_LOG", "flask.log")


app = Flask(__name__)


@app.before_first_request
def before_first_request():
    """
    Hook to handle any initialization before the first request (e.g. load model,
    setup logging handler, etc.)

    In our project, default model is Decision Tree (with RandomizedSearchCV)

    """
    app.logger.info("---------------------running before_first_request()---------------------")
    # Basic logging configuration
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

    # clear log file
    with open(LOG_FILE, "w"):
        pass

    # Any other initialization before the first request (e.g. load default model)
    global model_name
    
    model_name = filename_dict["models"]\
                    [comet_config["model"]]\
                    [comet_config["version"]]

    model_file = Path(f"./ift6758/ift6758/data/{model_name}")

    # Check to see if the model you are querying for is already downloaded
    # if yes, load that model and write to the log about the model change. 
    if os.path.isfile(model_file):
        app.logger.info(f"Loading model {model_name}.")
    
    else:
        app.logger.info(f"{model_file} doesn't exist, downloading ...")
        # if it succeeds, load that model and write to the log about the model change. 
        try:
            # https://www.comet.ml/docs/python-sdk/API/#apidownload_registry_model
            api.download_registry_model(
                comet_config["workspace"],
                comet_config["model"],
                comet_config["version"],
                output_path="./ift6758/ift6758/data/",
                expand=True,
            )

            app.logger.info(f"Succesfully downloaded model: {model_name}")
        
        except Exception as e:
            app.logger.info(f"Failed to download model: {model_name}")

    global model
    model = pickle.load(open(model_file, "rb"))

    app.logger.info("Succesfully loaded default model")
    pass


@app.route("/logs", methods=["GET"])
def logs():
    """Reads data from the log file and returns them as the response"""

    # Read the log file specified and return the data
    with open(LOG_FILE) as f:
        response = f.readlines()

    return jsonify(response)  # response must be json serializable!


@app.route("/download_registry_model", methods=["POST"])
def download_registry_model():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/download_registry_model

    The comet API key should be retrieved from the ${COMET_API_KEY} environment variable.

    Recommend (but not required) json with the schema:

        {
            workspace: (required),
            model: (required),
            version: (required),
            ... (other fields if needed) ...
        }

    """
    app.logger.info("---------------------running download_registry_model()---------------------")
    # Get POST json data
    user_json = request.get_json()
    app.logger.info(user_json)

    global model_name
    model_name = filename_dict["models"]\
                    [user_json["model"]]\
                    [user_json["version"]]

    model_file = Path(f"./ift6758/ift6758/data/{model_name}")

    # Check to see if the model you are querying for is already downloaded
    # if yes, load that model and write to the log about the model change. 
    if os.path.isfile(model_file):
        app.logger.info(f"Model {model_file} is already downloaded, loading ...")
    
    else:
        app.logger.info(f"{model_file} doesn't exist, downloading ...")
        # if it succeeds, load that model and write to the log about the model change. 
        try:
            # https://www.comet.ml/docs/python-sdk/API/#apidownload_registry_model
            api.download_registry_model(
                user_json["workspace"],
                user_json["model"],
                user_json["version"],
                output_path="./ift6758/ift6758/data/",
                expand=True,
            )

            app.logger.info(f"Succesfully downloaded model: {model_name}")
        
        except Exception as e:
            app.logger.info(f"Failed to download model: {model_name}.\nError:{e}")

    global model
    try:
        # As my XGBoost version is 1.5.0, there is error when load its models using pickle,
        # so using sklearn lib load json models instead. https://mljar.com/blog/xgboost-save-load-python/
        
        if 'json' in model_name:
    
            model = xgb.XGBClassifier()
            # check model path
            model_path = f'{model_file}/{model_name}'
            
            if os.path.isfile(model_path):
                model.load_model(model_path)
            else:
                model.load_model(model_file)
            # Features are various in XGBoost classifiers
            # Get XGBoost Classifier feature names
            clf = model.get_booster()
        
            feature_names = clf.feature_names # a list of strings
            app.logger.info(f"Selected features are:\n{feature_names}")
        
        else:
            model = pickle.load(open(model_file, "rb"))

        app.logger.info(f"Succesfully loaded default model {model_name}")
    except Exception as e:
        app.logger.info(f"Failed to load model {model_name}.\nError:{e}")
    
    response = None

    return jsonify(response)  # response must be json serializable!


@app.route("/predict", methods=["POST"])
def predict():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/predict

    Returns predictions

    why method is not allowed:
    https://stackoverflow.com/a/21689599
    """
    app.logger.info("---------------------running predict()---------------------")
    # Get POST json data
    
    data = request.get_json()
    # app.logger.info(data)
    print('app.py X:')
    # X = pd.DataFrame(data).iloc[: , :-1]
    X = pd.DataFrame(data).drop(columns=['Is Goal'])
    if 'xG' in X.columns:
        X = X.drop(columns=['xG'])
    app.logger.info(f'X.dtypes:\n{X.dtypes}')
    response = model.predict_proba(X)

    app.logger.info(f"Done predict(). Result:\n{response}")

    # response must be json serializable!
    return jsonify({"response": response.tolist()})


# if __name__ == "__main__":
    # run app in debug mode on port 5000
    # kill a running process: 
    # sudo kill -9 `sudo lsof -t -i:5000`
    # app.run(host="0.0.0.0", port="5000", debug=True)