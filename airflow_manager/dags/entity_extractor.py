#!/usr/bin/env python3
# encoding: utf-8

"""Define the EntityExtractor DAG."""

import logging
import sys
from airflow import DAG
from airflow.models.baseoperator import BaseOperator
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import timedelta
import os
from typing import Dict

logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s|%(levelname)s: %(message)s",
    datefmt="%H:%M:%S, %d-%b-%Y",
    level=logging.DEBUG,
)


with DAG(
    dag_id="ent_extraction_dag",
    description="Extract the named entities from the documents, match them against SoT and insert them into the relational database.",
    schedule_interval=timedelta(days=1),
) as dag:
    # Define the environment variables to pass
    env_vars: Dict[str, str] = {
        "MYSQL_HOST": "database",
        "MYSQL_USER": os.environ["MYSQL_USER"],
        "MYSQL_PASSWORD": os.environ["MYSQL_PASSWORD"],
        "MYSQL_DATABASE": os.environ["MYSQL_DATABASE"],
        "NER_HOST": os.environ["NER_HOST"],
    }
    run_ent_extraction: BaseOperator = DockerOperator(
        task_id="run_ent_extraction",
        image="ent-extraction",  # Local Docker image
        network_mode="bilby-assignment_bilby",  # Use the specified bridge network
        auto_remove="success",  # Automatically remove the container after it exits
        environment=env_vars,  # This will pick up the environment variables
        tty=True,  # To enable interactive mode
        dag=dag,
    )
    run_ent_extraction
