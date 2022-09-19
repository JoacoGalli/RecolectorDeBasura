#!/usr/bin/env bash

pushd mqtt; docker-compose up -d;popd
pushd node-red; docker-compose up -d;popd
pushd influx1; docker-compose up -d;popd
pushd grafana; docker-compose up -d;popd
