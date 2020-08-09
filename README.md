# pokerback

## Start server dev config
`docker-compose -f docker-compose.yml up -d --build`

## Start server prod config
`docker-compose -f docker-compose.prod.yml up -d --build`

## Stop server
`docker-compose down -v`

## SSH into the docker container
`docker exec -it docker_pokerback_1 /bin/bash`

## Run unit tests
`export DJANGO_SETTINGS_MODULE=pokerback.settings`
`pytest tests/*`
