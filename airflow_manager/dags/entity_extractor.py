#!/usr/bin/env python3
# encoding: utf-8

"""Define the EntityExtractor DAG."""

import logging
import sys
from typing import FrozenSet
from airflow import DAG
from airflow.models.baseoperator import BaseOperator
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import timedelta, datetime
import os
from typing import Dict

logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s|%(levelname)s: %(message)s",
    datefmt="%H:%M:%S, %d-%b-%Y",
    level=logging.DEBUG,
)


with DAG(
    dag_id="ent_extraction_dag",  # Used in the test script to invoke this DAG
    description="Extract the named entities from the documents, match them against SoT and insert them into the relational database.",
    start_date=datetime(year=2025, month=4, day=1),
    schedule=timedelta(days=1),
) as dag:
    # Define the environment variables to pass to the container runtime
    variables: FrozenSet[str] = frozenset(
        ("MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE", "NER_HOST")
    )
    env_vars: Dict[str, str] = {var: os.environ[var] for var in variables}
    env_vars["TZ"]: str = "Asia/Singapore"
    run_ent_extraction: BaseOperator = DockerOperator(
        task_id="run_ent_extraction",  # Defined here
        image=os.path.join(os.environ["USER"], "ent-extraction"),  # Dockerhub image
        network_mode="bilby-assignment_bilby",  # Local Docker network, defined in the compose manifest together with the directory suffix
        auto_remove="success",  # Automatically remove the container after it exits
        environment=env_vars,  # This will pick up the environment variables
        tty=True,  # To enable interactive mode
        dag=dag,
    )
    run_ent_extraction
