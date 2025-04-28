#!/usr/bin/env bash
# encoding:utf-8

# Build the extractor image and run it.
IMAGE=ent-extraction
CONTAINER=extraction_container
docker build --tag=$IMAGE ./
docker container stop $CONTAINER
docker container rm $CONTAINER
docker run --name $CONTAINER --network bilby-assignment_bilby -e MYSQL_USER="$USER" \
  -e MYSQL_PASSWORD="$MYSQL_PASSWORD" -e MYSQL_DATABASE="$MYSQL_DATABASE" -e NER_HOST="$NER_HOST" -e MYSQL_HOST="database" \
  $IMAGE
