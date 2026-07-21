import os
from google.cloud import bigquery

def get_bigquery_config() -> tuple[str, str]:
    project_id = os.getenv("BIGQUERY_PROJECT_ID", "agents-cli-503022")
    dataset_id = os.getenv("BIGQUERY_DATASET_ID", "thelook_ecommerce")
    return project_id, dataset_id

def get_bigquery_client() -> bigquery.Client:
    project_id, _ = get_bigquery_config()
    return bigquery.Client(project=project_id)

def get_dataset_ref() -> str:
    project_id, dataset_id = get_bigquery_config()
    return f"{project_id}.{dataset_id}"

def get_table_path(table_name: str) -> str:
    project_id, dataset_id = get_bigquery_config()
    return f"`{project_id}.{dataset_id}.{table_name}`"
