# eu-ai-api

For launching application in docker environment, you should use https://github.com/Panchos39/eu-ai-environment-docker repository in the same folder, where eu-ai-api was placed
When you placed eu-ai-environment-docker in the same folder, as eu-ai-api, to start application, you have to use following command
```
docker-compose build
```

```
docker-compose up --build --force-recreate --remove-orphans -d && \
docker-compose logs -f --tail 100
```
These commands will build docker-container and launch web application ready to use
