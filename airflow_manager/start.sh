#!/usr/bin/env bash
# encoding:utf-8

# The script is used to fire up the airflow service
uv run --env-file .env airflow standalone
