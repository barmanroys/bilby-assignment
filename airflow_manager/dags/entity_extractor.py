#!/usr/bin/env python3
# encoding: utf-8

"""Define the EntityExtractor DAG."""

import logging, sys
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime
import os

logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s|%(levelname)s: %(message)s",
    datefmt="%H:%M:%S, %d-%b-%Y",
    level=logging.DEBUG,
)


default_args = {
    "owner": "airflow",
    "start_date": datetime(year=2025, month=4, day=27),
}


with DAG(
    dag_id="ent_extraction_dag",
) as dag:
    # Define the environment variables to pass
    env_vars = {
        "MYSQL_HOST": "database",
        "MYSQL_USER": os.environ["MYSQL_USER"],
        "MYSQL_PASSWORD": os.environ["MYSQL_PASSWORD"],
        "MYSQL_DATABASE": os.environ["MYSQL_DATABASE"],
        "NER_HOST": os.environ["NER_HOST"],
    }
    run_ent_extraction = DockerOperator(
        task_id="run_ent_extraction",
        image="ent-extraction",  # Local Docker image
        network_mode="bilby-assignment_bilby",  # Use the specified bridge network
        auto_remove="success",  # Automatically remove the container after it exits
        environment=env_vars,  # This will pick up the environment variables from airflow container
        tty=True,  # To enable interactive mode
        dag=dag,
    )
    run_ent_extraction
