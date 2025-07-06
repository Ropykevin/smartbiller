#!/bin/bash

sh mypostgresql.sh
git pull origin master
docker-compose -f docker-compose.yml up -d --build 

# Optional: view logs for the main web service
docker logs -f smartbiller-web
