#!/usr/bin/env bash
# encoding:utf-8

# The script is used to fire up the ASGI from the project root. It is a
# blocking script
cd src||exit
uv run uvicorn gateway:app --host=0.0.0.0 --port=8081