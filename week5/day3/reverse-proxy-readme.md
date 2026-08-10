# NGINX Reverse Proxy + Load Balancing

## 1. Overview

This Day 3 exercise demonstrates how to use **NGINX inside Docker as a reverse proxy** and distribute requests across multiple backend instances using **round-robin load balancing**.

The setup contains:

* Two Node.js backend containers
* One NGINX container
* One Docker bridge network
* NGINX routing client requests to the backend containers
* Round-robin load balancing between the backend replicas

The architecture is:

```text
                    Client
                       |
                       | HTTP Request
                       v
                +-------------+
                |    NGINX    |
                | Reverse     |
                | Proxy       |
                +------+------+
                       |
                day3_network
                       |
             +---------+---------+
             |                   |
             v                   v
      +-------------+     +-------------+
      |  backend1   |     |  backend2   |
      | Node.js     |     | Node.js     |
      | :3000       |     | :3000       |
      +-------------+     +-------------+
```

---

## 2. Objectives

The main objectives of this exercise were:

1. Run NGINX inside Docker.
2. Run two instances of the same Node.js backend.
3. Connect the containers through a Docker network.
4. Use NGINX as a reverse proxy.
5. Route client requests to the internal backend containers.
6. Enable round-robin load balancing.
7. Verify that requests are distributed between both backend instances.

---

## 3. Project Structure

```text
day3/
│
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── package.json
│   ├── package-lock.json
│   └── server.js
│
├── nginx/
│   └── nginx.conf
│
└── reverse-proxy-readme.md
```

---

## 4. Backend Application

The backend is a simple Node.js + Express application running on port `3000`.

The API returns a response containing the container hostname.

The hostname is important because it allows us to identify which backend container handled a request.

Example response:

```json
{
  "message": "Hello from backend",
  "hostname": "..."
}
```

Since `backend1` and `backend2` are separate containers, they have different hostnames.

---

## 5. Docker Image

A Docker image was created from the backend Dockerfile:

```dockerfile
FROM node:22-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["node", "server.js"]
```

The image was built using:

```bash
docker build -t day3-backend ./backend
```

This produces one reusable image that can be used to create multiple backend containers.

---

## 6. Multiple Backend Replicas

Two containers were created from the same `day3-backend` image:

```bash
docker run -d \
  --name backend1 \
  --network day3_network \
  day3-backend
```

```bash
docker run -d \
  --name backend2 \
  --network day3_network \
  day3-backend
```

Both containers run the Node.js application on port `3000`.

The important point is that the port is available inside the Docker network. We do not need to expose both containers on the same host port.

The resulting architecture is:

```text
day3_network
│
├── backend1:3000
│
└── backend2:3000
```

---

## 7. Docker Network

A custom Docker bridge network was created:

```bash
docker network create day3_network
```

The network allows the containers to communicate with each other using Docker's internal networking and container names.

For example:

```text
backend1:3000
backend2:3000
```

NGINX can therefore communicate with the backend containers without requiring their ports to be published to the host.

---

## 8. NGINX Configuration

The NGINX configuration contains an upstream backend group:

```nginx
events {}

http {
    upstream backend_servers {
        server backend1:3000;
        server backend2:3000;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://backend_servers;
        }
    }
}
```

> Note: The exercise specification describes `/api → backend-service:3000`. During implementation, the route was configured as `/` for testing, and the reverse proxy/load-balancing behavior was successfully verified through that route.

---

## 9. `events {}`

The `events` block is an NGINX configuration context used for connection and event-related settings.

For this project it is kept empty:

```nginx
events {}
```

No custom worker connection tuning was required for this exercise.

For example, NGINX could be configured with:

```nginx
events {
    worker_connections 20;
}
```

This would configure each NGINX worker to handle up to 20 simultaneous connections, subject to other system and NGINX limits.

This setting is separate from backend load balancing.

---

## 10. Upstream

The following configuration defines a group of backend servers:

```nginx
upstream backend_servers {
    server backend1:3000;
    server backend2:3000;
}
```

`backend_servers` is the name given to this NGINX upstream group.

It contains:

```text
backend1:3000
backend2:3000
```

The upstream group allows NGINX to treat multiple backend instances as a single logical backend destination.

---

## 11. `proxy_pass`

The following directive forwards incoming requests to the upstream group:

```nginx
proxy_pass http://backend_servers;
```

`proxy_pass` tells NGINX where to send a request after receiving it.

The flow is:

```text
Client
   |
   | Request
   v
NGINX
   |
   | proxy_pass
   v
backend_servers
   |
   +------> backend1:3000
   |
   +------> backend2:3000
```

The client does not need to know the internal names or addresses of the backend containers.

---

## 12. Reverse Proxy

A reverse proxy is a server that receives requests from clients and forwards those requests to one or more internal servers.

In this project:

```text
Client
   |
   v
NGINX
   |
   +-----> backend1
   |
   +-----> backend2
```

The client communicates with NGINX instead of directly communicating with the backend containers.

Therefore, NGINX acts as the public entry point while the backend containers remain internal to the Docker network.

---

## 13. NGINX Container

NGINX was run using the official Alpine-based NGINX image:

```bash
docker run -d \
  --name nginx-proxy \
  --network day3_network \
  -p 8080:80 \
  -v "$(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro" \
  nginx:alpine
```

The important options are:

### `--name nginx-proxy`

Gives the container a predictable name.

### `--network day3_network`

Connects NGINX to the same Docker network as the backend containers.

### `-p 8080:80`

Maps:

```text
Host port 8080
      |
      v
NGINX container port 80
```

Therefore, requests can be sent to:

```text
http://localhost:8080
```

### `-v`

Mounts the local NGINX configuration into the container:

```text
nginx/nginx.conf
      |
      v
/etc/nginx/nginx.conf
```

The `:ro` flag makes the mounted configuration read-only inside the container.

---

## 14. Round-Robin Load Balancing

NGINX uses round-robin behavior by default for the upstream servers.

The upstream group contains:

```nginx
upstream backend_servers {
    server backend1:3000;
    server backend2:3000;
}
```

Requests are distributed approximately like:

```text
Request 1 → backend1
Request 2 → backend2
Request 3 → backend1
Request 4 → backend2
Request 5 → backend1
Request 6 → backend2
```

This allows traffic to be distributed across the available backend instances.

---

## 15. Testing the Backend Containers

Each backend was tested directly before testing NGINX.

For example:

```bash
docker exec backend1 wget -qO- http://localhost:3000/
```

and:

```bash
docker exec backend2 wget -qO- http://localhost:3000/
```

Both backend containers responded successfully.

This confirmed that the backend application was working independently of NGINX.

---

## 16. Testing the Reverse Proxy

The NGINX endpoint was tested through the host:

```bash
curl http://localhost:8080/
```

The request flow was:

```text
curl
 |
 | localhost:8080
 v
NGINX
 |
 | proxy_pass
 v
backend_servers
 |
 +----> backend1
 |
 +----> backend2
```

---

## 17. Testing Round-Robin Behavior

Multiple requests were sent through NGINX:

```bash
for i in {1..10}; do
  curl -s http://localhost:8080/
  echo
done
```

The backend response included the container hostname.

Because the two backend containers have different hostnames, the responses demonstrated that requests were being handled by different backend instances.

Conceptually:

```text
Request 1 → backend1 hostname
Request 2 → backend2 hostname
Request 3 → backend1 hostname
Request 4 → backend2 hostname
...
```

This confirms that NGINX is distributing requests across the backend replicas.

---

## 18. Final Architecture

The completed Day 3 architecture is:

```text
                    CLIENT
                       |
                       | http://localhost:8080/
                       v
              +------------------+
              |      NGINX       |
              |  nginx:alpine    |
              |      :80         |
              +--------+---------+
                       |
                       | proxy_pass
                       v
              +------------------+
              | backend_servers  |
              |    upstream      |
              +--------+---------+
                       |
                 day3_network
                  /          \
                 /            \
                v              v
       +---------------+  +---------------+
       |   backend1    |  |   backend2    |
       |   Node.js     |  |   Node.js     |
       |     :3000     |  |     :3000     |
       +---------------+  +---------------+
```

---

## 19. Key Concepts Learned

### Reverse Proxy

The client sends requests to NGINX, and NGINX forwards them to internal backend servers.

### Upstream

An NGINX upstream group defines multiple backend servers:

```nginx
upstream backend_servers {
    server backend1:3000;
    server backend2:3000;
}
```

### `proxy_pass`

Specifies where NGINX forwards incoming requests:

```nginx
proxy_pass http://backend_servers;
```

### Round-Robin

NGINX distributes requests across the available backend servers.

### Docker Networking

Containers connected to the same Docker network can communicate using their container/service names.

### Backend Replicas

Multiple containers can be created from the same Docker image:

```text
day3-backend image
       |
       +----> backend1
       |
       +----> backend2
```

---

## Conclusion

Day 3 demonstrates a basic production-style architecture in which NGINX acts as the entry point for client requests and forwards traffic to multiple backend instances running inside Docker.

Using an NGINX upstream group and default round-robin behavior, requests can be distributed across multiple backend replicas while the client only communicates with the reverse proxy.