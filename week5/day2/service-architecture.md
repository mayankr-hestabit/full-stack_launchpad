# Day 2 — Service Architecture

## 1. Overview

This project demonstrates a multi-container application using Docker Compose.

The application consists of three main services:

* **Client** — React frontend
* **Server** — Node.js backend
* **MongoDB** — database

Docker Compose is used to build, start, stop, and manage all services together.

The services communicate through a custom Docker bridge network, while MongoDB uses a named Docker volume for persistent data storage.

---

## 2. Application Architecture

The overall architecture is:

```text
                    Docker Compose
                          |
                  app_network
                   (bridge)
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
       Client           Server         MongoDB
       React            Node.js         MongoDB 8
       :5173            :3001           :27017
                          |
                          |
                    mongodb:27017
                          |
                          v
                    mongo_data
                      Volume
```

### Services

| Service | Technology | Container Port |           Host Port |
| ------- | ---------- | -------------: | ------------------: |
| client  | React      |           5173 |                5173 |
| server  | Node.js    |           3001 |                3001 |
| mongodb | MongoDB 8  |          27017 | Not exposed to host |

---

## 3. Docker Compose

Docker Compose defines the complete application architecture in `docker-compose.yml`.

The Compose file is responsible for:

* Building the client image
* Building the server image
* Starting MongoDB
* Creating the application network
* Creating and mounting the MongoDB volume
* Configuring service dependencies
* Mapping application ports
* Supplying the MongoDB connection string

The application can therefore be started as a complete stack instead of manually starting each service.

```bash
docker compose up -d --build
```

---

## 4. Client Service

The client service builds the React frontend.

```yaml
client:
  build: ./client
  ports:
    - "5173:5173"
  depends_on:
    - server
  networks:
    - app_network
```

### Responsibilities

The client:

* Runs the React application
* Is accessible through port `5173`
* Is connected to `app_network`
* Depends on the server service

The host can access the frontend through:

```text
http://localhost:5173
```

---

## 5. Server Service

The server service builds and runs the Node.js backend.

```yaml
server:
  build: ./server
  ports:
    - "3001:3001"
  environment:
    MONGO_URI: mongodb://mongodb:27017/day2db
  depends_on:
    - mongodb
  networks:
    - app_network
```

### Responsibilities

The server:

* Runs the Node.js backend
* Listens on port `3001`
* Connects to MongoDB
* Uses the Docker network for database communication

The backend is accessible from the host through:

```text
http://localhost:3001
```

---

## 6. MongoDB Service

MongoDB uses the official MongoDB 8 image.

```yaml
mongodb:
  image: mongo:8
  volumes:
    - mongo_data:/data/db
  networks:
    - app_network
```

MongoDB stores its database files in:

```text
/data/db
```

inside the container.

The volume mapping:

```yaml
- mongo_data:/data/db
```

connects the named Docker volume `mongo_data` to MongoDB's data directory.

---

## 7. Docker Network

A custom network is defined for communication between services.

```yaml
networks:
  app_network:
    name: app_network
    driver: bridge
```

The network uses Docker's `bridge` driver.

All three services are connected to it:

```yaml
networks:
  - app_network
```

Therefore:

```text
Client
   |
   |
Server
   |
   |
MongoDB
```

can communicate within the Docker network.

---

## 8. Why a Bridge Network Is Used

A bridge network provides a private Docker network for the containers.

Instead of relying on container IP addresses, services can communicate using their Compose service names.

For example, the server connects to MongoDB using:

```text
mongodb:27017
```

rather than:

```text
localhost:27017
```

Here:

```text
mongodb
   |
   +-- Compose service name
```

Docker's internal DNS resolves the service name to the appropriate MongoDB container.

---

## 9. MongoDB Connection

The server receives the following environment variable:

```yaml
MONGO_URI: mongodb://mongodb:27017/day2db
```

The connection string consists of:

```text
mongodb://
mongodb
:27017
/day2db
```

Where:

* `mongodb://` — MongoDB connection protocol
* `mongodb` — Docker Compose service name
* `27017` — MongoDB's internal port
* `day2db` — application database

Because the server and MongoDB are on the same Docker network, the server can reach MongoDB through the service name.

---

## 10. Why `localhost` Is Not Used

Inside the Node.js container:

```text
localhost
```

refers to the **Node.js container itself**, not the MongoDB container.

Therefore this would be incorrect for container-to-container communication:

```text
mongodb://localhost:27017/day2db
```

Instead, the server uses:

```text
mongodb://mongodb:27017/day2db
```

because `mongodb` is the service name on the shared Docker network.

---

## 11. Named Volume

The Compose file declares:

```yaml
volumes:
  mongo_data:
```

This creates a named Docker volume managed by Docker.

The volume is mounted into MongoDB:

```yaml
volumes:
  - mongo_data:/data/db
```

The relationship is:

```text
Docker Volume
    |
    | mongo_data
    v
MongoDB container
    |
    | /data/db
    v
MongoDB database files
```

The actual Docker-managed volume in this project was:

```text
day2_mongo_data
```

---

## 12. Why the Volume Is Required

Containers are replaceable.

If the MongoDB container is removed, its container filesystem can disappear.

The named volume provides persistent storage outside the container lifecycle.

Therefore:

```text
MongoDB Container
       |
       v
mongo_data Volume
```

allows database data to survive the removal and recreation of the MongoDB container.

---

## 13. Persistence Test

Persistence was verified by inserting test data into MongoDB.

Example:

```javascript
use day2db

db.test.insertOne({
  name: "Mayank",
  purpose: "Docker volume persistence test"
})
```

The document was then verified using:

```javascript
db.test.find().pretty()
```

The MongoDB container was stopped and removed without removing the named volume.

The MongoDB service was recreated.

The same data was queried again:

```javascript
use day2db

db.test.find().pretty()
```

The previously inserted document was still available.

This demonstrates that the database data was persisted in the named Docker volume rather than being dependent only on the MongoDB container.

---

## 14. Important Difference: Container vs Volume

A container and a volume are different Docker resources.

### Container

A container runs an application or service.

```text
client
server
mongodb
```

### Network

A network allows containers to communicate.

```text
app_network
```

### Volume

A volume provides persistent storage.

```text
mongo_data
```

Therefore the architecture contains:

```text
Containers
├── client
├── server
└── mongodb

Network
└── app_network

Volume
└── mongo_data
```

---

## 15. Port Mapping

The client uses:

```yaml
ports:
  - "5173:5173"
```

The server uses:

```yaml
ports:
  - "3001:3001"
```

The format is:

```text
HOST_PORT:CONTAINER_PORT
```

Therefore:

```text
localhost:5173
        |
        v
client container :5173
```

and:

```text
localhost:3001
        |
        v
server container :3001
```

MongoDB does not require a host port mapping because the server accesses it through the Docker network.

The server communicates internally using:

```text
mongodb:27017
```

---

## 16. `depends_on`

The Compose configuration uses:

```yaml
client:
  depends_on:
    - server
```

and:

```yaml
server:
  depends_on:
    - mongodb
```

This establishes the startup dependency relationship:

```text
MongoDB
   |
   v
Server
   |
   v
Client
```

`depends_on` controls service startup order but does not itself guarantee that an application inside the dependent container is ready to accept connections.

---

## 17. Useful Docker Commands

### Start the complete application

```bash
docker compose up -d
```

### Build and start

```bash
docker compose up -d --build
```

### Check running containers

```bash
docker ps
```

### Check Compose services

```bash
docker compose ps
```

### View server logs

```bash
docker compose logs server
```

### View MongoDB logs

```bash
docker compose logs mongodb
```

### View client logs

```bash
docker compose logs client
```

### Follow logs

```bash
docker compose logs -f server
```

### List Docker networks

```bash
docker network ls
```

### Inspect the application network

```bash
docker network inspect app_network
```

### List Docker volumes

```bash
docker volume ls
```

### Inspect the MongoDB volume

```bash
docker volume inspect day2_mongo_data
```

### Stop the stack

```bash
docker compose stop
```

### Remove containers and network

```bash
docker compose down
```

### Remove containers, network, and volumes

```bash
docker compose down -v
```

> `docker compose down -v` should be used carefully because it removes the named volume and therefore deletes the persisted MongoDB data associated with it.

---

## 18. Docker Compose Workflow

The complete workflow is:

```text
docker-compose.yml
       |
       v
docker compose up -d --build
       |
       v
Build Images
       |
       v
Create Network
       |
       v
Create Volume
       |
       v
Start MongoDB
       |
       v
Start Server
       |
       v
Start Client
       |
       v
Application Running
```

---

## 19. Final Architecture

```text
                         HOST MACHINE
                              |
               +--------------+--------------+
               |                             |
               |                             |
        localhost:5173                localhost:3001
               |                             |
               v                             v
       +---------------+             +---------------+
       |    CLIENT     |             |    SERVER     |
       |    React      |             |    Node.js    |
       |    :5173      |             |    :3001      |
       +-------+-------+             +-------+-------+
               |                             |
               |                             |
               +-------------+---------------+
                             |
                       app_network
                         (bridge)
                             |
                             v
                     +---------------+
                     |    MONGODB    |
                     |   MongoDB 8   |
                     |    :27017     |
                     +-------+-------+
                             |
                             | /data/db
                             v
                     +---------------+
                     |  mongo_data   |
                     | Docker Volume |
                     +---------------+
```

## 20. Day 2 Outcome

The Day 2 implementation demonstrates:

* Multi-service Docker Compose architecture
* React client containerization
* Node.js server containerization
* MongoDB containerization
* Custom Docker bridge networking
* Service-name-based container communication
* MongoDB persistent storage
* Named Docker volume usage
* Volume persistence across MongoDB container recreation
* Port mapping
* Compose service dependencies
* Centralized application orchestration

The complete stack can be managed using Docker Compose rather than manually starting individual containers.
