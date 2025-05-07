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

minikube delete
set -e
cd ner_service/
./build_ner_image.sh
cd ../extraction_pipeline/
./build_etl_image.sh
cd ..
minikube start --nodes=3
kubectl apply --filename ./kubeops-manifests
kubectl get pods --namespace bilby # This to capture the pod names for NER
# The service can be verified by the port forward and accessing loalhost:8080
# If the NER is using replicas, you can use any of the podnames to substitute the following variable $PODNAME
# kubectl port-forward --namespace bilby $PODNAME 8080:8081

# To trigger the cronjob manually, out of schedule for testing
# kubectl create job --from=cronjob/ent-extraction-cronjob --namespace bilby test-job-run
minikube dashboard
