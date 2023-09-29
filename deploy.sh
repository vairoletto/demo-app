#!/bin/bash

# List of directories to build
directories=("frontend" "backend" "consumer" "producer" "producerpy" "mysql-service" "backoffice")

for dir in "${directories[@]}"
do
    # Go to the directory
    cd "$dir" || exit

    # Build the Docker image
    docker build . -t "$(basename $(pwd))"

    # Go back to the execution root
    cd - || exit
done

# Combine the directories into a single string separated by spaces
dirs_to_up=$(printf "%s " "${directories[@]}")

# Run docker-compose up with directories
docker-compose up -d --force-recreate $dirs_to_up agent
