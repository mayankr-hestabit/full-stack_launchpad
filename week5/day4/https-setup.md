# Day 4 — HTTPS, SSL/TLS & NGINX Configuration

## 1. Objective

Day 4 extended the Day 3 reverse-proxy architecture by adding HTTPS/SSL/TLS support using NGINX.

The main objectives were:

- Understand HTTP vs HTTPS.
- Understand SSL/TLS and certificates.
- Use mkcert for local development certificates.
- Configure NGINX for HTTPS.
- Mount certificates into an NGINX Docker container.
- Configure myapp.local.
- Understand TLS termination.
- Connect HTTPS NGINX to the Day 3 backend containers.
- Test HTTPS from WSL and Windows Chrome.
- Understand certificate trust and curl -k.
- Understand the difference between a server certificate and a CA certificate.

## 2. Architecture Before Day 4

Day 3 already had three backend containers running on a Docker network.

```text
                     day3-network
              ┌────────────────────────────┐
              │                            │
              │  day3-backend1:3000        │
              │  day3-backend2:3000        │
              │  day3-backend3:3000        │
              │                            │
              └─────────────┬──────────────┘
                            │
                          NGINX
                            │
                           HTTP
                            │
                          Client
```

Day 4 added HTTPS/TLS in front of NGINX.

## 3. Final Architecture

```text
                         Windows Chrome
                              │
                              │ HTTPS
                              │
               https://myapp.local:8443
                              │
                              ▼
                    ┌─────────────────┐
                    │      NGINX      │
                    │                 │
                    │ HTTPS :443      │
                    │ TLS termination │
                    └────────┬────────┘
                             │
                             │ HTTP
                             ▼
                       day3-network
                       ┌─────┼─────┐
                       │     │     │
                       ▼     ▼     ▼
                 day3-backend1 day3-backend2 day3-backend3
                     :3000       :3000       :3000
```

The browser communicates with NGINX over HTTPS.

NGINX terminates TLS and forwards the request to the backend servers over the Docker network.


# 4. HTTP vs HTTPS

HTTP sends application traffic without TLS encryption.

```text
Client
   │
   │ HTTP
   ▼
NGINX
   │
   ▼
Backend
```

HTTPS is:

```text
HTTPS = HTTP + TLS
```

With HTTPS:

```text
Client
   │
   │ HTTPS / encrypted
   ▼
NGINX
   │
   │ HTTP
   ▼
Backend
```

HTTPS provides:

- Encryption
- Authentication
- Data integrity

## 5. What is TLS?

TLS stands for Transport Layer Security.

TLS establishes a secure connection between a client and a server.

The browser verifies the server certificate and establishes encrypted communication.

In this setup, NGINX acts as the TLS endpoint.

This process is called TLS termination.

## 6. Why NGINX Handles TLS

NGINX is placed between the browser and backend servers.

```text
Browser
   │
   │ HTTPS
   ▼
NGINX
   │
   │ HTTP
   ▼
Backend
```

NGINX receives the encrypted HTTPS request, handles TLS, decrypts the request and forwards it to the backend.

This allows the backend applications to continue listening on normal HTTP ports.


# 7. Installing mkcert

Because this was a local development environment, a publicly issued SSL certificate was unnecessary.

We used mkcert to create locally trusted development certificates.

On Windows PowerShell:

```powershell
winget install FiloSottile.mkcert
```

After installation, the shell was restarted so the mkcert command became available.

The installation was verified using:

```powershell
mkcert --version
```

Then the local CA was installed:

```powershell
mkcert -install
```

## 8. Local Certificate Authority

mkcert creates a local Certificate Authority (CA).

The CA signs the development certificates.

The CA location was found with:

```powershell
mkcert -CAROOT
```

The directory contains files similar to:

```text
rootCA.pem
rootCA-key.pem
```

### rootCA.pem

This is the CA certificate.

It can be installed into a system's trusted certificate store.

### rootCA-key.pem

This is the CA private key.

It must remain private and must not be committed to Git or shared.

## 9. Generating the Local Certificate

A certificate was generated for the local development hostname:

```text
myapp.local
```

The certificate was generated using:

```powershell
mkcert myapp.local localhost 127.0.0.1 ::1
```

This produced files similar to:

```text
myapp.local+3.pem
myapp.local+3-key.pem
```


# 10. Understanding the Generated Files

## Server Certificate

```text
myapp.local+3.pem
```

This is the server certificate.

It contains information identifying the domain and information about the certificate issuer and validity.

NGINX presents this certificate to clients.

## Server Private Key

```text
myapp.local+3-key.pem
```

This is the private key associated with the server certificate.

NGINX uses it during TLS operations.

The private key must be protected.

## 11. Certificate Directory

The certificates were copied into the Day 4 project.

The project contained:

```text
day4/
├── certs/
│   ├── myapp.local+3.pem
│   └── myapp.local+3-key.pem
│
└── nginx/
    └── nginx.conf
```

The certificates generated on Windows were copied into WSL so that Docker/NGINX could use them.

## 12. Configuring NGINX

The NGINX configuration contained an upstream group for the three backend containers.

```nginx
events {}

http {
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

    server {
        listen 443 ssl;

        ssl_certificate /etc/nginx/certs/myapp.local+3.pem;
        ssl_certificate_key /etc/nginx/certs/myapp.local+3-key.pem;

        location / {
            proxy_pass http://backend_servers;
        }
    }
}
```


# 13. NGINX Port 80

The HTTP server used:

```nginx
listen 80;
```

This means NGINX accepts HTTP traffic on port 80 inside the container.

The request is then forwarded using:

```nginx
proxy_pass http://backend_servers;
```

## 14. NGINX Port 443

The HTTPS server used:

```nginx
listen 443 ssl;
```

This tells NGINX to listen for HTTPS/TLS traffic on port 443.

The certificate was configured with:

```nginx
ssl_certificate /etc/nginx/certs/myapp.local+3.pem;
```

The private key was configured with:

```nginx
ssl_certificate_key /etc/nginx/certs/myapp.local+3-key.pem;
```

## 15. Why proxy_pass Is Still Used

Adding HTTPS does not remove the reverse-proxy functionality.

The complete flow is:

```text
Browser
   │
   │ HTTPS
   ▼
NGINX
   │
   │ TLS termination
   │
   │ HTTP
   ▼
Backend
```

Therefore NGINX still needs:

```nginx
proxy_pass http://backend_servers;
```

HTTPS and reverse proxying are separate responsibilities.


# 16. Docker Network

The NGINX container was connected to the existing Day 3 network:

```text
day3-network
```

The backend containers were also attached to this network.

This allows NGINX to resolve:

```text
day3-backend1
day3-backend2
day3-backend3
```

using Docker's internal DNS.

The communication is therefore:

```text
NGINX
  │
  ├── day3-backend1:3000
  │
  ├── day3-backend2:3000
  │
  └── day3-backend3:3000
```

## 17. Docker Certificate Mount

The certificates were mounted into the NGINX container using a bind mount:

```bash
-v "$(pwd)/certs:/etc/nginx/certs:ro"
```

This means:

```text
Host:
./certs

        ↓

Container:
/etc/nginx/certs
```

The :ro means read-only.

NGINX can read the certificate files but cannot modify them.

## 18. Docker Port Mapping

The NGINX container was started with:

```bash
-p 8080:80
-p 8443:443
```

The mapping means:

```text
Host port 8080 → Container port 80
Host port 8443 → Container port 443
```

Therefore:

```text
http://localhost:8080
```

reaches NGINX's port 80.

And:

```text
https://myapp.local:8443
```

reaches NGINX's port 443.


# 19. NGINX Docker Command

The NGINX container was started with:

```bash
docker run -d   --name day4-nginx   --network day3-network   -p 8080:80   -p 8443:443   -v "$(pwd)/nginx/nginx.conf:/etc/nginx/nginx.conf:ro"   -v "$(pwd)/certs:/etc/nginx/certs:ro"   nginx:alpine
```

Important parts:

```text
--network day3-network
```

connects NGINX to the backend network.

```text
-p 8080:80
```

exposes HTTP.

```text
-p 8443:443
```

exposes HTTPS.

```text
-v ...nginx.conf:/etc/nginx/nginx.conf:ro
```

mounts the NGINX configuration.

```text
-v ...certs:/etc/nginx/certs:ro
```

mounts the certificates.

## 20. Verifying the Certificates Inside NGINX

The certificate files were verified using:

```bash
docker exec day4-nginx ls -l /etc/nginx/certs
```

The container showed:

```text
myapp.local+3.pem
myapp.local+3-key.pem
```

This confirmed that the certificates were successfully mounted into the container.

## 21. Configuring myapp.local

The local hostname was mapped to localhost.

The hosts file contained:

```text
127.0.0.1 myapp.local
```

This means:

```text
myapp.local
     ↓
127.0.0.1
```

The hostname could then be used in the browser:

```text
https://myapp.local:8443/
```


# 22. Testing HTTPS

HTTPS was tested using:

```bash
curl -I https://myapp.local:8443/
```

When certificate trust wasn't configured in the environment, curl reported a certificate verification problem.

To verify that HTTPS itself was working, the request was tested with:

```bash
curl -k -I https://myapp.local:8443/
```

The -k option means:

```text
--insecure
```

It tells curl to skip certificate verification.

A successful response such as:

```text
HTTP/1.1 200 OK
Server: nginx
```

proved that:

- NGINX was reachable.
- Port 8443 was working.
- TLS was configured.
- NGINX could communicate with the backend.
- The reverse proxy was working.

## 23. Why -k Is Not the Proper Final Solution

The following:

```bash
curl -k https://myapp.local:8443/
```

does not verify the certificate.

It is useful for testing connectivity but is not a proper solution for certificate trust.

The proper setup is:

```text
Client
   ↓
Trust mkcert CA
   ↓
Verify server certificate
   ↓
Establish HTTPS connection
```


# 24. Windows vs WSL Certificate Trust

An important concept discovered during the exercise was that Windows and WSL have separate certificate trust stores.

The certificate generated by Windows mkcert could be used by NGINX in Docker, but WSL's curl could still report:

```text
SSL certificate problem:
unable to get local issuer certificate
```

This occurs because the WSL Linux CA store does not automatically inherit all Windows trusted CAs.

## 25. Installing the mkcert CA in WSL

The Windows CA location was obtained using:

```powershell
mkcert -CAROOT
```

The rootCA.pem file can then be copied into WSL.

For example:

```bash
cp /mnt/c/Users/mayan/AppData/Local/mkcert/rootCA.pem ~/rootCA.pem
```

It can be installed into the Linux CA directory:

```bash
sudo cp ~/rootCA.pem /usr/local/share/ca-certificates/mkcert-rootCA.crt
```

Then the CA database is updated:

```bash
sudo update-ca-certificates
```

After this, HTTPS can be tested without -k:

```bash
curl -I https://myapp.local:8443/
```

## 26. Certificate Trust Flow

The complete certificate trust relationship is:

```text
                   mkcert
                      │
                      ▼
              ┌──────────────┐
              │   Local CA   │
              │  rootCA.pem  │
              └──────┬───────┘
                     │
                     │ signs
                     ▼
           ┌────────────────────┐
           │ myapp.local cert   │
           │ myapp.local+3.pem  │
           └─────────┬──────────┘
                     │
                     ▼
                   NGINX
                     │
                     │ HTTPS
                     ▼
                  Browser
```

The client trusts the CA.

The CA has signed the server certificate.

Therefore the client can trust the server certificate.


# 27. Difference Between Certificates and CA

The following files have different responsibilities:

| File | Purpose |
| --- | --- |
| `myapp.local+3.pem` | Server certificate |
| `myapp.local+3-key.pem` | Server private key |
| `rootCA.pem` | Local CA certificate |
| `rootCA-key.pem` | Local CA private key |

The CA private key should never be shared or committed to source control.

## 28. HTTP vs HTTPS Testing

The setup was tested from WSL.

HTTP:

```text
http://localhost:8080
```

worked.

HTTPS:

```text
https://myapp.local:8443
```

also worked.

From Windows Chrome, the HTTPS URL:

```text
https://myapp.local:8443
```

was successfully reachable.

The HTTP localhost:8080 behavior differed between WSL and Windows because localhost refers to the environment from which the request originates.

In WSL:

```text
localhost → WSL environment
```

In Windows Chrome:

```text
localhost → Windows environment
```

This distinction is important when working with WSL and Docker Desktop networking.


# 29. Complete Request Flow

The final HTTPS request follows this path:

```text
Windows Chrome
      │
      │ https://myapp.local:8443
      ▼
127.0.0.1
      │
      ▼
Docker/WSL
      │
      ▼
NGINX :443
      │
      │ TLS termination
      ▼
HTTP request
      │
      ▼
upstream backend_servers
      │
      ├──────────────► day3-backend1:3000
      │
      ├──────────────► day3-backend2:3000
      │
      └──────────────► day3-backend3:3000
```

NGINX handles the TLS connection and reverse-proxying.

## 30. Important Concepts Learned

### HTTPS

HTTP running over TLS.

### TLS

Provides encryption, authentication and integrity.

### Certificate

Identifies the server/domain and is signed by a certificate authority.

### Certificate Authority

An authority whose certificates are trusted by clients.

### mkcert

Creates a local development CA and certificates.

### TLS Termination

NGINX handles HTTPS/TLS and forwards normal HTTP requests to the backend.

### Reverse Proxy

NGINX receives client requests and forwards them to backend servers.

### Docker Network

Allows NGINX to communicate with backend containers using container/service names.

### Bind Mount

Maps host files into a container.

### `:ro`

Makes a bind mount read-only.

### Port Mapping

```text
8443:443
```

means host port 8443 maps to container port 443.

### `curl -k`

Disables certificate verification and should be used only when intentionally testing an untrusted certificate.


# 31. Final Day 4 Architecture

```text
                         Browser
                            │
                            │ HTTPS
                            │
             https://myapp.local:8443
                            │
                            ▼
                 ┌──────────────────┐
                 │      NGINX       │
                 │                  │
                 │  :443 SSL/TLS    │
                 │ TLS termination  │
                 │ Reverse Proxy    │
                 └────────┬─────────┘
                          │
                          │ HTTP
                          ▼
                    day3-network
                   ┌──────┼──────┐
                   │      │      │
                   ▼      ▼      ▼
          day3-backend1 day3-backend2 day3-backend3
               :3000        :3000        :3000
```

## 32. Day 4 Result

By the end of Day 4, the Day 3 reverse-proxy architecture was extended to support local HTTPS.

The important chain is:

```text
mkcert
   ↓
Local CA
   ↓
myapp.local certificate
   ↓
Certificate mounted into NGINX
   ↓
NGINX listens on HTTPS :443
   ↓
Docker maps host :8443 → container :443
   ↓
Browser connects using HTTPS
   ↓
NGINX terminates TLS
   ↓
NGINX forwards HTTP to
day3-backend1 / day3-backend2 / day3-backend3
```

The key outcome of Day 4 is therefore:

> NGINX acts as an HTTPS reverse proxy and TLS termination point, using a locally trusted mkcert certificate while forwarding requests to the three backend containers running on the day3-network Docker network.
