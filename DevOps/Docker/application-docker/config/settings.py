import os
from dotenv import load_dotenv

load_dotenv() 

class Settings:
    PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "default_project")
    BIGQUERY_DATASET: str = os.getenv("BIGQUERY_DATASET", "default_dataset")
    BIGQUERY_TABLE: str = os.getenv("BIGQUERY_TABLE", "default_table")
    API_PORT: int = int(os.getenv("API_PORT", 8000))

settings = Settings()
