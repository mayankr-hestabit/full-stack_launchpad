# Linux Internals Inside a Docker Container

## 1. Objective

The objective of this exercise was to run a Node.js application inside a Docker container and explore basic Linux internals from within the container.

The following areas were explored:

* Linux filesystem
* Users and groups
* File permissions
* Running processes
* Disk usage
* Container logs
* Container interaction using `docker exec`

---

## 2. Docker Container Setup

A fresh Node.js application was created for this exercise.

The application was packaged using a Dockerfile based on Node.js with Alpine Linux.

### Dockerfile

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
docker build -t node_image .
```

The container was started using:

```bash
docker run -d --name node_container -p 3000:3000 node_image
```

The running container was verified using:

```bash
docker ps
```

The Node.js application was accessible through port `3000`.

---

## 3. Entering the Container

A shell was opened inside the running container using:

```bash
docker exec -it node_container /bin/sh
```

This allowed Linux commands to be executed directly inside the container.

The current directory was checked with:

```bash
pwd
```

The result was `/app`, which was configured through:

```dockerfile
WORKDIR /app
```

The contents of the application directory were inspected using:

```bash
ls
```

The root filesystem was explored using:

```bash
ls /
```

This demonstrated that `/app` is a working directory inside the container, while `/` is the filesystem root.

---

## 4. Users and Groups

The current user was identified using:

```bash
whoami
```

Additional user and group information was obtained with:

```bash
id
```

The list of users configured inside the container was inspected using:

```bash
cat /etc/passwd
```

Groups were inspected using:

```bash
cat /etc/group
```

These commands demonstrated that a container has its own Linux users, groups, and identity information.

---

## 5. File Permissions

File ownership and permissions were inspected using:

```bash
ls -la /app
```

Detailed information about the application file was obtained using:

```bash
stat /app/server.js
```

Linux permissions follow the owner, group, and others model.

For example:

```text
-rw-r--r--
```

can be interpreted as:

```text
Owner  → rw-
Group  → r--
Others → r--
```

The numeric representation is:

```text
644
```

This means:

* Owner: read and write
* Group: read
* Others: read

### Permission Experiment

The write permission was temporarily removed:

```bash
chmod 444 /app/server.js
```

The changed permissions were verified with:

```bash
ls -l /app/server.js
```

The original permissions were then restored:

```bash
chmod 644 /app/server.js
```

This demonstrated that Linux file permissions also apply inside Docker containers.

---

## 6. Running Processes

Processes inside the container were inspected using:

```bash
ps
```

A more detailed process listing was obtained using:

```bash
ps aux
```

The process hierarchy was also examined using:

```bash
ps -ef
```

The Node.js application process was visible in the process list.

Because the Dockerfile starts the application with:

```dockerfile
CMD ["node", "server.js"]
```

the Node.js process acts as the primary application process of the container.

This demonstrates an important container concept: the application process is directly associated with the lifecycle of the container.

---

## 7. Disk Usage

Filesystem-level disk usage was checked using:

```bash
df -h
```

The size of the application directory was checked using:

```bash
du -sh /app
```

Individual files and directories were inspected using:

```bash
du -sh /app/*
```

These commands provide different views of storage usage:

* `df -h` shows filesystem capacity and usage.
* `du -sh` shows the size consumed by a particular directory.
* `du -sh /app/*` helps identify which contents consume space.

---

## 8. Container Logs

After leaving the container:

```bash
exit
```

the application's logs were viewed from the host using:

```bash
docker logs node_container
```

Live logs were followed using:

```bash
docker logs -f node_container
```

The `-f` option follows the container's log output continuously.

Pressing:

```text
Ctrl + C
```

stops following the logs but does not stop the container itself.

---

## 9. Important Docker Concepts Observed

### Image vs Container

A Docker image is the packaged environment used to create containers.

A container is a running instance created from an image.

```text
Dockerfile
    ↓
Docker Image
    ↓
Docker Container
    ↓
Node.js Application
```

### Container Filesystem

The container has its own filesystem environment.

The filesystem root is:

```text
/
```

while `/app` is the working directory configured by:

```dockerfile
WORKDIR /app
```

### Container Process

The Node.js application runs as the primary process started by:

```dockerfile
CMD ["node", "server.js"]
```

### Linux Permissions

Docker containers still use Linux filesystem permissions. Files have owners, groups, and permission modes.

### Container Logs

Application output can be viewed from outside the container with:

```bash
docker logs node_container
```

This avoids having to manually open log files inside the container.

---

## 10. Commands Used

| Command                                  | Purpose                                  |
| ---------------------------------------- | ---------------------------------------- |
| `docker ps`                              | List running containers                  |
| `docker exec -it node_container /bin/sh` | Enter the running container              |
| `pwd`                                    | Display current directory                |
| `ls`                                     | List directory contents                  |
| `ls /`                                   | Explore filesystem root                  |
| `whoami`                                 | Show current user                        |
| `id`                                     | Show UID, GID and groups                 |
| `cat /etc/passwd`                        | View configured users                    |
| `cat /etc/group`                         | View configured groups                   |
| `ls -la /app`                            | Inspect files, ownership and permissions |
| `stat /app/server.js`                    | Display detailed file metadata           |
| `chmod 444`                              | Remove write permissions                 |
| `chmod 644`                              | Restore standard file permissions        |
| `ps`                                     | Display processes                        |
| `ps aux`                                 | Display detailed processes               |
| `ps -ef`                                 | Display process hierarchy                |
| `df -h`                                  | Display filesystem disk usage            |
| `du -sh /app`                            | Display `/app` disk usage                |
| `du -sh /app/*`                          | Display usage of `/app` contents         |
| `docker logs node_container`             | Display container logs                   |
| `docker logs -f node_container`          | Follow container logs                    |

---

## 11. Conclusion

This exercise demonstrated how a Node.js application can be packaged and executed inside a Docker container and how Linux internals can be inspected from inside that container.

The exercise covered:

* Docker image creation
* Container execution
* Container shell access
* Linux filesystem structure
* Users and groups
* File ownership and permissions
* Process inspection
* Disk usage analysis
* Container logging

The main workflow was:

```text
Node.js Application
        ↓
Dockerfile
        ↓
Docker Image
        ↓
Docker Container
        ↓
Enter Container
        ↓
Explore Linux Internals
        ↓
Inspect Processes
        ↓
Inspect Disk Usage
        ↓
Inspect Logs
        ↓
Inspect Users & Permissions
```

**Day 1 Docker Fundamentals + Linux Internals exercise completed.**
