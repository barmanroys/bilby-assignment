#!/usr/bin/env bash
# encoding:utf-8

# End to end run of the project, incorporating
# Fire up the database and ner services
# Initialise the database with tables
# Set up the ner pipeline as a cronjob which can
#   - Read sample documents from disk
#   - Insert the documents into the database
#   - Extract the named entities from documents
#   - Match the extracted entities against SoT entities
#   - Insert the matched entities into the database

function TIMESTAMP() { printf "%s" "$(date "+%H:%M:%S, %d-%b-%Y")";}
minikube delete
minikube start --driver=docker
minikube docker-env
minikube dashboard
