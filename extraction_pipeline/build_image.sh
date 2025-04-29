#!/usr/bin/env bash
# encoding:utf-8

# Build the extractor image and optionally run it using this file.


IMAGE=ent-extraction # This is the definition, used in the DAG definition

docker build --tag=$IMAGE ./


# # Supply the necessary environment variables from the host for access credentials and network inclusion to run the container without scheduler
# CONTAINER=extraction_container # Local variable, no impact outside this file.
# DOCKER_NETWORK=bilby-assignment_bilby # Defined in the compose file
# docker run --name "$CONTAINER" --network "$DOCKER_NETWORK" -e MYSQL_USER="$USER" \
#   -e MYSQL_PASSWORD="$MYSQL_PASSWORD" -e MYSQL_DATABASE="$MYSQL_DATABASE" -e NER_HOST="$NER_HOST" \
#    -e MYSQL_HOST="$MYSQL_HOST" $IMAGE
