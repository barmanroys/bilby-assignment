#!/usr/bin/env bash
# encoding:utf-8
# Build the NER service
# Push it to docker hub
IMAGE=ner-service # This is the definition, used in the kubernetes manifest
docker build --tag=$IMAGE ./
docker tag $IMAGE $USER/$IMAGE
docker push  $USER/$IMAGE # This will work because my docker repository username is same as the system username
