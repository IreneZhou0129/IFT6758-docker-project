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
from comet_ml import API
from comet_ml import Experiment

# Cutomized libs
import ift6758
from config_data import api, \                        
                        comet_config, \
                        filename_dict, \
                        features_dict


LOG_FILE = os.environ.get("FLASK_LOG", "flask.log")


app = Flask(__name__)


@app.before_first_request
def before_first_request():
    """
    Hook to handle any initialization before the first request (e.g. load model,
    setup logging handler, etc.)
    """
    print("---------------------running before_first_request()---------------------")
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

    model_file = Path(f"{model_name}")

    
    if not model_file.is_file():
        print(f"{model_file} doesn't exist, downloading ...")
        # https://www.comet.ml/docs/python-sdk/API/#apidownload_registry_model
        api.download_registry_model(
            comet_config["workspace"],
            comet_config["model"],
            comet_config["version"],
            output_path="./",
            expand=True,
        )
        # rename model file to the same name as in the api.get() call
        # this will allow us to detect if a model has already been downloaded by looking at the file name
        # rename_model_file(model_name)
        print(f"model name:{model_name}")

    global model
    model = pickle.load(open(model_name, "rb"))

    app.logger.info("succesfully loaded default model")
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
    # Get POST json data
    json = request.get_json()
    app.logger.info(json)

    # TODO: check to see if the model you are querying for is already downloaded

    # TODO: if yes, load that model and write to the log about the model change.
    # eg: app.logger.info(<LOG STRING>)

    # Tip: you can implement a "CometMLClient" similar to your App client to abstract all of this
    # logic and querying of the CometML servers away to keep it clean here

    global model_name
    model_name = filename_dict["models"][comet_config["model"]][comet_config["version"]]
    model_file = Path(f"{model_name}")

    # TODO: if no, try downloading the model: if it succeeds, load that model and write to the log
    # about the model change. If it fails, write to the log about the failure and keep the
    # currently loaded model
    if not model_file.is_file():
        api = API(key)
        api.download_registry_model(
            comet_config["workspace"],
            comet_config["model"],
            comet_config["version"],
            output_path="./",
            expand=True,
        )
        # rename_model_file(model_name)
        print(model_name)

    global model
    model = pickle.load(open(model_name, "rb"))

    response = None

    app.logger.info(response)
    return jsonify(response)  # response must be json serializable!


@app.route("/predict", methods=["POST"])
def predict():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/predict

    Returns predictions

    why method is not allowed:
    https://stackoverflow.com/a/21689599
    """
    print("---------------------running predict()---------------------")
    # Get POST json data
    data = request.get_json()
    app.logger.info(data)

    features = features_dict[model_name]

    X = pd.DataFrame(data)[features]
    response = model.predict_proba(X)

    app.logger.info(response)

    # response must be json serializable!
    return jsonify({"response": response.tolist()})


if __name__ == "__main__":
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)


"""
focus on XGBoost model
"""