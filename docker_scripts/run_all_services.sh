docker network create microservices-network

docker compose -f ../frontend-service/docker-compose.yml -f ../docker-compose.override.yml up -d
docker compose -f ../user-service/docker-compose.yml -f ../docker-compose.override.yml up -d