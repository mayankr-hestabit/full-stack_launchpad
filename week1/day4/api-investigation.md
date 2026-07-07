# API Investigation — Day 4

## DNS & Network Analysis
- dummyjson.com resolves to two Cloudflare IPs (172.67.205.42, 104.21.61.23)
- Two IPs = load balancing across multiple edge servers
- Traceroute: 17 hops, ~75ms total latency from WSL to destination
- Request path: WSL → Windows host → Reliance Jio → public internet → Cloudflare SIN edge

## Pagination
- API uses limit/skip pattern: ?limit=5&skip=10
- Returns metadata alongside data: total=194, skip=10, limit=5
- To get next page: increment skip by limit value (skip=15 for page 3)
- Total of 194 products available, paginated in chunks

## Headers Analysis

### Request Headers
- User-Agent: identifies the client making the request
- Authorization: carries authentication token
- If-None-Match: sends cached ETag for cache validation

### Response Headers
- Content-Type: application/json — tells client how to parse the body
- ETag: content fingerprint for cache validation
- x-ratelimit-limit/remaining: 100 requests allowed, tracked by IP
- server: cloudflare — CDN layer sitting in front of origin
- cf-ray: SIN — Singapore edge server handled the request

## Header Manipulation Findings
| Experiment | Change | Server Response | Conclusion |
|------------|--------|-----------------|------------|
| Remove User-Agent | No User-Agent sent | 200 OK | Server doesn't enforce User-Agent |
| Fake Authorization | Bearer faketoken123 | 200 OK | /products is public, auth ignored |
| Both together | No UA + fake auth | 200 OK | Rate limiting by IP, not by headers |

## ETag Caching
- First request: server returns 200 + full JSON body + ETag fingerprint
- Second request with If-None-Match: server returns 304 Not Modified + no body
- Bandwidth saved: entire JSON response not re-transmitted
- Same ETag returned in 304 confirms content unchanged

## Node HTTP Server
Built server.js with three endpoints:
- /echo → returns client's own request headers as JSON (debugging tool)
- /slow?ms=N → delays response by N milliseconds (simulates heavy operations)
- /cache → returns Cache-Control, ETag, Last-Modified headers

## Key Learnings
- Headers are invisible metadata controlling every HTTP request/response
- ETags prevent unnecessary data transfer when content hasn't changed
- Rate limiting is tracked server-side by IP, not by client-provided headers
- Cloudflare acts as a CDN/proxy layer — you never directly hit the origin server
- HTTP/1.1 is used for localhost, HTTP/2 mainly over HTTPS connections
