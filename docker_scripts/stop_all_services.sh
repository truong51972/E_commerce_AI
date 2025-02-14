docker compose -f ../frontend-service/docker-compose.yml down
docker compose -f ../user-service/docker-compose.yml down

docker network rm microservices-network