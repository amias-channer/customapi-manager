#!/bin/env bash

# options

# make docker image
docker build -t customapi .


# run docker container
docker run  --network host customapi