import os
from unittest.mock import patch
from google.cloud import bigquery
from src.config import (
    get_bigquery_config,
    get_bigquery_client,
    get_dataset_ref,
    get_table_path,
)

def test_get_bigquery_config_defaults():
    project_id, dataset_id = get_bigquery_config()
    assert project_id == os.getenv("BIGQUERY_PROJECT_ID", "agents-cli-503022")
    assert dataset_id == os.getenv("BIGQUERY_DATASET_ID", "thelook_ecommerce")

def test_get_bigquery_config_env_vars():
    with patch.dict(os.environ, {"BIGQUERY_PROJECT_ID": "test-project", "BIGQUERY_DATASET_ID": "test-dataset"}):
        project_id, dataset_id = get_bigquery_config()
        assert project_id == "test-project"
        assert dataset_id == "test-dataset"

def test_get_bigquery_client():
    with patch.dict(os.environ, {"BIGQUERY_PROJECT_ID": "test-project"}):
        with patch("google.cloud.bigquery.Client") as mock_client:
            client = get_bigquery_client()
            mock_client.assert_called_once_with(project="test-project")

def test_get_dataset_ref():
    with patch.dict(os.environ, {"BIGQUERY_PROJECT_ID": "test-project", "BIGQUERY_DATASET_ID": "test-dataset"}):
        dataset_ref = get_dataset_ref()
        assert dataset_ref == "test-project.test-dataset"

def test_get_table_path():
    with patch.dict(os.environ, {"BIGQUERY_PROJECT_ID": "test-project", "BIGQUERY_DATASET_ID": "test-dataset"}):
        table_path = get_table_path("users")
        assert table_path == "`test-project.test-dataset.users`"
