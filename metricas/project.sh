#!/usr/bin/env bash

pushd mqtt; docker-compose up -d;popd
pushd grafinflux; docker-compose up -d;popd
