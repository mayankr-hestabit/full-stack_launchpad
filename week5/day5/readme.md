Day 5 — Docker Production & CI-Style Deployment Automation

1. Day 5 Scope

2. Starting Point

pwd
ls -la
docker ps
docker ps -a
docker images
docker network ls
docker volume ls

docker ps

Browser
   |
   | HTTP / HTTPS
   v
NGINX reverse proxy
   |
   +----> day3-backend1
   +----> day3-backend2
   +----> day3-backend3

3. Docker Volumes

3.1 Why persistence is needed

MongoDB container
      |
      v
Named Docker volume
      |
      v
Persistent database data

3.2 Named volume

docker volume create mongo_data

docker volume ls

docker volume inspect mongo_data

services:
  mongo:
    image: mongo:8
    volumes:
      - mongo_data:/data/db
volumes:
  mongo_data:

3.3 Bind mount

services:
  app:
    volumes:
      - ./src:/app/src

3.4 Volume commands

docker volume ls
docker volume inspect mongo_data
docker volume rm mongo_data

4. Compose Profiles

services:
  app:
    image: myapp
  debug:
    image: busybox
    profiles:
      - debug

docker compose up -d

docker compose --profile debug up -d

profiles:
  - debug

5. .env Configuration

PORT=3000
NODE_ENV=production
MONGO_URI=mongodb://mongo:27017/week5db

services:
  app:
    environment:
      PORT: ${PORT}
      NODE_ENV: ${NODE_ENV}
      MONGO_URI: ${MONGO_URI}

6. Secrets

environment:
  MONGO_PASSWORD: super-secret-password

7. .gitignore

.env
.env.*
!.env.example
*.pem
*.key
node_modules/
logs/

8. .env.example

PORT=3000
NODE_ENV=production
MONGO_URI=
MONGO_USER=
MONGO_PASSWORD=

.env.example
     |
     v
Documents required configuration
     |
     v
Developer creates local .env

9. Log Rotation

services:
  app:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

10. Health Checks

services:
  app:
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

Fields

test

interval

timeout

retries

start_period

docker ps

docker inspect <container>

starting
healthy
unhealthy

11. Restart Policies

services:
  app:
    restart: unless-stopped

no
always
on-failure
unless-stopped

12. Production Compose

docker-compose.prod.yml

services:
  app:
    image: myapp:latest
    restart: unless-stopped
    environment:
      NODE_ENV: production
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
  mongo:
    image: mongo:8
    restart: unless-stopped
    volumes:
      - mongo_data:/data/db
volumes:
  mongo_data:

13. Production Architecture

                    Browser
                       |
                HTTPS :443 / HTTP :80
                       |
                       v
                NGINX Reverse Proxy
                       |
             Docker application network
                 /       |       \
                /        |        \
               v         v         v
        backend1    backend2    backend3
               \        |        /
                \       |       /
                    MongoDB
                       |
                       v
                 Named Volume

14. depends_on

services:
  app:
    depends_on:
      - mongo

services:
  app:
    depends_on:
      mongo:
        condition: service_healthy
  mongo:
    image: mongo:8
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5

depends_on + healthcheck
          |
          v
wait for dependency readiness

15. Deployment Automation

deploy.sh

#!/bin/sh
set -e
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps

chmod +x deploy.sh

./deploy.sh

Why set -e?

set -e

16. Production Compose Commands

docker compose -f docker-compose.prod.yml up -d

docker compose -f docker-compose.prod.yml build

docker compose -f docker-compose.prod.yml up -d --build

docker compose -f docker-compose.prod.yml down

docker compose -f docker-compose.prod.yml ps

docker compose -f docker-compose.prod.yml logs

docker compose -f docker-compose.prod.yml logs -f

17. Deployment Sequence

1. Check source/configuration
        |
2. Build application image
        |
3. Pull required images
        |
4. Start production Compose stack
        |
5. Check container status
        |
6. Check health
        |
7. Check logs
        |
8. Test application
        |
9. Test NGINX
        |
10. Test HTTPS

18. Verification

Containers

docker ps

Compose

docker compose -f docker-compose.prod.yml ps

Logs

docker compose -f docker-compose.prod.yml logs

docker compose -f docker-compose.prod.yml logs app

docker compose -f docker-compose.prod.yml logs -f app

Health

docker inspect <container>

Health.Status

19. Reverse Proxy Verification

Client
  |
  | request
  v
NGINX
  |
  | proxy_pass
  v
Backend container

upstream backend_servers {
    server day3-backend1:3000;
    server day3-backend2:3000;
    server day3-backend3:3000;
}
server {
    listen 80;
    location / {
        proxy_pass http://backend_servers;
    }
}

20. HTTPS Capstone

Browser
   |
HTTPS
   |
NGINX :443
   |
proxy_pass
   |
Backend containers

certificate (.pem)
private key (-key.pem)

server {
    listen 443 ssl;
    server_name myapp.local;
    ssl_certificate /etc/nginx/certs/myapp.local+3.pem;
    ssl_certificate_key /etc/nginx/certs/myapp.local+3-key.pem;
    location / {
        proxy_pass http://backend_servers;
    }
}

21. Certificate Mounting

docker run -d \
  --name nginx-https \
  --network day3-network \
  -p 8080:80 \
  -p 8443:443 \
  -v "$(pwd)/nginx/nginx.conf:/etc/nginx/nginx.conf:ro" \
  -v "$(pwd)/certs:/etc/nginx/certs:ro" \
  day3-nginx:alpine

docker exec nginx-https ls -l /etc/nginx/certs

22. HTTPS Verification

curl -k -I https://myapp.local:8443/

curl -I https://myapp.local:8443/

https://myapp.local:8443/

23. Environment Separation

.env
.env.example
docker-compose.yml
docker-compose.prod.yml

docker compose up -d

docker compose -f docker-compose.prod.yml up -d

24. Production Volumes

services:
  mongo:
    volumes:
      - mongo_data:/data/db
volumes:
  mongo_data:

docker volume ls
docker volume inspect mongo_data

25. Production Logging

logging:
  driver: json-file
  options:
    max-size: "10m"
    max-file: "3"

docker compose -f docker-compose.prod.yml logs

26. Production Healthcheck

healthcheck:
  test: ["CMD", "wget", "-qO-", "http://localhost:3000/"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 10s

healthcheck:
  test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
  interval: 10s
  timeout: 5s
  retries: 5

27. Restart Policy

restart: unless-stopped

docker restart <container>
docker ps

28. Failure Testing

Application failure

docker kill <app-container>
docker ps

Dependency failure

docker stop <mongo-container>

docker compose -f docker-compose.prod.yml logs app

docker start <mongo-container>

Proxy verification

docker logs <nginx-container>

curl -I http://localhost:8080/
curl -k -I https://myapp.local:8443/

29. Deployment Repeatability

./deploy.sh

same configuration
      |
      v
same deployment process
      |
      v
predictable result

30. CI-Style Thinking

Code
 |
 v
Build
 |
 v
Test / Verify
 |
 v
Deploy
 |
 v
Health Check
 |
 v
Verify

31. Recommended Project Structure

week5/
├── day3/
├── day4/
├── day5/
│   ├── docker-compose.prod.yml
│   ├── deploy.sh
│   ├── .env.example
│   └── production-guide.md
├── nginx/
│   └── nginx.conf
├── certs/
└── .gitignore

32. production-guide.md

production-guide.md

1. Overview
2. Architecture
3. Prerequisites
4. Project Structure
5. Environment Configuration
6. Secrets
7. Production Compose
8. Volumes
9. Health Checks
10. Restart Policies
11. Log Rotation
12. Compose Profiles
13. Deployment Script
14. Deployment Commands
15. Verification
16. Logs
17. Troubleshooting
18. Rollback
19. Security Notes
20. Final Checklist

33. Important Docker Commands

Containers

docker ps
docker ps -a
docker start <container>
docker stop <container>
docker restart <container>
docker kill <container>
docker rm <container>
docker logs <container>
docker exec -it <container> sh
docker inspect <container>

Images

docker images
docker build -t myapp .
docker image inspect myapp

Networks

docker network ls
docker network inspect <network>

Volumes

docker volume ls
docker volume inspect <volume>
docker volume create <volume>
docker volume rm <volume>

34. Important Compose Commands

docker compose up -d
docker compose up -d --build
docker compose down
docker compose ps
docker compose logs
docker compose logs -f

docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs

docker compose --profile debug up -d

35. Container Inspection Checklist

docker inspect <container>

State
Health
Networks
Mounts
RestartPolicy
Config

docker ps
docker logs <container>
docker inspect <container> | less

36. Network Checklist

docker network ls
docker network inspect day3-network

NGINX
 |
 +-- day3-network -- backend1
 |
 +-- day3-network -- backend2
 |
 +-- day3-network -- backend3

37. Volume Checklist

docker volume ls
docker volume inspect mongo_data

MongoDB data
    |
    v
named volume

38. Production Security Rules

39. Troubleshooting

Container exits

docker ps -a
docker logs <container>

Application unreachable

docker ps
docker logs <app-container>
docker inspect <app-container>

NGINX cannot resolve backend

docker network inspect day3-network

NGINX configuration issue

docker logs <nginx-container>

docker exec <nginx-container> nginx -t

HTTPS issue

docker logs <nginx-container>
docker exec <nginx-container> ls -l /etc/nginx/certs

certificate exists
private key exists
certificate path matches nginx.conf
server_name matches requested hostname
port 443 is exposed

Certificate trust issue

curl -k -I https://myapp.local:8443/

curl -I https://myapp.local:8443/

40. Final Verification

docker ps
docker network ls
docker volume ls
docker compose -f docker-compose.prod.yml ps

docker compose -f docker-compose.prod.yml logs

docker inspect <container>

curl -I http://localhost:8080/

curl -k -I https://myapp.local:8443/

https://myapp.local:8443/

41. Day 5 Deliverables

Named Docker volume demonstrated

Volume inspected

Bind mount vs named volume understood

Compose profile created/tested

.env configuration added

.env.example created

.gitignore checked

Secrets kept outside Git

Log rotation configured

Application health check configured

Database health check configured if applicable

Restart policy configured

Production Compose file created

depends_on/health dependency understood

Deployment script created

Deployment repeated successfully

Failure/restart behavior tested

NGINX reverse proxy verified

HTTPS verified

Persistent volume verified

production-guide.md created

42. Final Day 5 Architecture

                         CLIENT
                           |
                           | HTTPS
                           v
                  +------------------+
                  |      NGINX       |
                  | Reverse Proxy    |
                  | TLS termination  |
                  +--------+---------+
                           |
                    Docker Network
                           |
              +------------+------------+
              |            |            |
              v            v            v
        +---------+  +---------+  +---------+
        |Backend 1|  |Backend 2|  |Backend 3|
        +----+----+  +----+----+  +----+----+
             \            |            /
              \           |           /
               +----------+----------+
                          |
                          v
                     +---------+
                     | MongoDB |
                     +----+----+
                          |
                          v
                    Named Volume
                    Persistent Data

Environment
Secrets
Health Checks
Restart Policies
Log Rotation
Compose Profiles
Deployment Script
Verification

43. Day 5 Execution Order

1. Inspect current Docker environment
2. Understand/create named volume
3. Test persistence
4. Understand bind mount vs volume
5. Add Compose profile
6. Add .env / .env.example
7. Secure secrets and .gitignore
8. Add log rotation
9. Add health checks
10. Add restart policy
11. Create production Compose
12. Add dependency health conditions
13. Create deployment script
14. Deploy
15. Verify containers
16. Verify health
17. Verify logs
18. Test restart/failure recovery
19. Integrate/verify NGINX
20. Verify HTTPS
21. Verify persistence
22. Create production-guide.md
23. Run final checklist