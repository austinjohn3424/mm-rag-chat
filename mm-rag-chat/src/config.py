# config.py
import os
import logging
from google.cloud import logging as cloud_logging
from vertexai.generative_models import SafetySetting

# Configuration variables
API_KEY = "YOUR_PINECONE_API_KEY"
INDEX_NAME = "YOUR_PINECONE_INDEX"
PROJECT_ID = "YOUR_GCP_PROJECT_ID"
REGION = "YOUR_GCP_RESGION"
MYSQL_CONFIG = {
    'host': 'YOUR_GCP_SQL_HOST',
    'user': 'YOUR_GCP_SQL_USER',
    'password': 'YOUR_GCP_SQL_PASS',
    'database': 'YOUR_GCP_SQL_DB'
}

# Logging setup
def setup_logging():
    cloud_logging_client = cloud_logging.Client(project=PROJECT_ID)
    cloud_logging_client.setup_logging()
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Gemini safety settings
SAFETY_SETTINGS = [
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
]
