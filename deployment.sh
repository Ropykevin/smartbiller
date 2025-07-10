sh mypostgresql.sh
git pull origin master
docker-compose down --remove-orphans
docker-compose -f docker-compose.yml up -d --build 
docker logs -f smartbiller