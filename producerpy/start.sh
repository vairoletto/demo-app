#!/bin/bash
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program uvicorn main:app --host 0.0.0.0 --port 3004
