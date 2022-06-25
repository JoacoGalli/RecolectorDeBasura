#!/usr/bin/env bash

pushd docker-data/mqtt; docker-compose up -d;popd
pushd docker-data/node-red; docker-compose up -d;popd
pushd docker-data/influx1; docker-compose up -d;popd
pushd docker-data/grafana; docker-compose up -d;popd
