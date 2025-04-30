#!/usr/bin/env bash
# encoding:utf-8

# End to end run of the project, incorporating
# Fire up the database and ner services
# Initialise the database with tables
# Start the extraction task via airflow test run. The test run does the followings:
#   - Read sample documents from disk
#   - Insert the documents into the database
#   - Extract the named entities from documents
#   - Match the extracted entities against SoT entities
#   - Insert the matched entities into the database
docker compose down # Shut down previous services
set -e # Preemptive stopping in case of errors
function TIMESTAMP() { printf "%s" "$(date "+%H:%M:%S, %d-%b-%Y")";}
docker compose up --detach
cd extraction_pipeline
./build_image.sh # Build the image for extraction ETL job
printf "%s Starting up the services, may take a few minutes. Grab a coffee meanwhile.\n" "$(TIMESTAMP)"
# This waits for the services to start up, because of heavy network latency at home environment.
# This is not a performance bottleneck, as in production, it is a one time set up for the NER service.
# After set up, the service can be called concurrently with high throughput and milisecond level latency.
sleep 5m
printf "%s ETL image built, performing a test run via airflow.\n" "$(TIMESTAMP)"

# Now run the image via airflow. First few lines are boilerplates to set up the airflow environment and SQLite
cd ../airflow_manager
cp .env.example .env
echo "AIRFLOW_HOME=$(pwd)" >> .env
uv run --env-file .env airflow db migrate
uv run --env-file .env airflow db check
DAG_ID="ent_extraction_dag" # Defined in the dag file

# The following line triggers the DAG test run. If completed successfully, the database will be populated with the extracted entities.
time uv run --env-file .env airflow dags test $DAG_ID
rm  --recursive --force --verbose .env airflow.cfg airflow.db logs # Clean up the transient artefacts
