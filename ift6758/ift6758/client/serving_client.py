import json
import requests
import pandas as pd
import logging
import os

comet_config = {'workspace': 'xiaoxin-zhou', \
            'model': 'logreg-distance', \
            'version': '1.0.0'}

LOG_FILE = os.environ.get("FLASK_LOG", "flask.log")
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

logger = logging.getLogger(__name__)
df = pd.read_csv('/Users/xiaoxinzhou/Documents/IFT6758_M2_CSV_data/all_data.csv')

class ServingClient:
    def __init__(self, ip: str = "0.0.0.0", port: int = 5000, features=None):
        print('------- __init__ ---------')
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
        print('------- serving_client/predict ---------')

        logger.info(f"Initializing request to generate predictions")
        r = requests.post(
            "http://127.0.0.1:5000/predict", 
            json=json.loads(df.iloc[0:5].to_json())
        )
        logger.info(f"Successfully generated predictions")
        return r.json()

    def logs(self) -> dict:
        """Get server logs"""
        print('------- serving_client/logs ---------')
        logger.info(f"Initializing request to server get logs")
        r = requests.post(
            "http://127.0.0.1:5000/download_registry_model", 
            json= comet_config
        )
        logger.info(f"Server Logs fetched")
        return r.json()

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
        print('------- serving_client/download_registry_model ---------')

        logger.info(f"Initializing request to download the model{model}-{version}")
        r = requests.post(
            "http://127.0.0.1:5000/download_registry_model", 
            json= comet_config
        )
        logger.info(f"Successfully Downloaded Model")


if __name__=='__main__':
    s = ServingClient()
    # breakpoint()
    s.download_registry_model(comet_config['workspace'],
                                comet_config['model'],
                                comet_config['version'])