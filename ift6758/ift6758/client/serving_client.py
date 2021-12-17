import json
import requests
import pandas as pd
import logging
import os

# Customized libs
import sys
sys.path.append('../../..')
from config_data import comet_config, df


LOG_FILE = os.environ.get("FLASK_LOG", "flask.log")
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

logger = logging.getLogger(__name__)


class ServingClient:
    def __init__(self, ip: str = "0.0.0.0", port: int = 5000, features=None):
        logger.info('------- serving_client/__init__ ---------')
        self.base_url = f"http://{ip}:{port}"
        
        logger.info(f"Initializing client; base URL: {self.base_url}")

        if features is None:
            features = ["distance"]
        self.features = features

        # any other potential initialization

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Formats the inputs into an appropriate payload for a POST request, and queries the
        prediction service. Retrieves the response from the server, and processes it back into a
        dataframe that corresponds index-wise to the input dataframe.
        
        Args:
            X (Dataframe): Input dataframe to submit to the prediction service.
        """
        logger.info('------- serving_client/predict ---------')
        logger.info(f"Initializing request to generate predictions")

        user_request = requests.post(
            "http://127.0.0.1:5000/predict", 
            json = json.loads(df.iloc[0:5].to_json())
        )
        
        logger.info(f"Successfully generated predictions")

        result = user_request.json()

        logger.info(f"Results:\n{result}")

        return result

    def logs(self) -> dict:
        """Get server logs"""
        logger.info('------- serving_client/logs ---------')
        logger.info(f"Initializing request to server get logs")
        user_request = requests.post(
            "http://127.0.0.1:5000/download_registry_model", 
            json = comet_config
        )
        logger.info(f"Server Logs fetched")
        return user_request.json()

    def download_registry_model(self, workspace: str, model: str, version: str) -> dict:
        """
        Triggers a "model swap" in the service; the workspace, model, and model version are
        specified and the service looks for this model in the model registry and tries to
        download it. 

        See more here:

            https://www.comet.ml/docs/python-sdk/API/#apidownload_registry_model
        
        Args:
            workspace (str): The Comet ML workspace
            model (str): The model in the Comet ML registry to download
            version (str): The model version to download
        """ 
        logger.info('------- serving_client/download_registry_model ---------')
        logger.info(f"Downloading the model {model}-{version}")
        user_request = requests.post(
            "http://127.0.0.1:5000/download_registry_model", 
            json = {'workspace': workspace,
                   'model': model,
                   'version': version}
        )
        logger.info(f"Successfully downloaded model {model}")


if __name__=='__main__':
    s = ServingClient()
    # breakpoint()
    s.download_registry_model(comet_config['workspace'],
                                comet_config['model'],
                                comet_config['version'])

    s.predict(df)