// Built-in Node HTTP module - no npm needed
const http = require('http');
const url = require('url');

const PORT = 3000;

const server = http.createServer((req, res) => {
  // Parse the URL to get path and query params
  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;
  const query = parsedUrl.query;

  // ─── /echo ───────────────────────────────────────────
  // Returns all request headers back as JSON
  if (path === '/echo') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      message: 'Here are your request headers',
      headers: req.headers,
      method: req.method,
      url: req.url
    }, null, 2));

  // ─── /slow ───────────────────────────────────────────
  // Delays response by ?ms= query param
  } else if (path === '/slow') {
    const delay = parseInt(query.ms) || 1000;
    setTimeout(() => {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        message: `Responded after ${delay}ms delay`,
        delay
      }, null, 2));
    }, delay);

  // ─── /cache ──────────────────────────────────────────
  // Returns response with cache headers
  } else if (path === '/cache') {
    res.writeHead(200, {
      'Content-Type': 'application/json',
      // Tell client to cache for 60 seconds
      'Cache-Control': 'public, max-age=60',
      // ETag fingerprint for this response
      'ETag': '"day4-cache-demo-v1"',
      // Last modified timestamp
      'Last-Modified': new Date().toUTCString()
    });
    res.end(JSON.stringify({
      message: 'This response has cache headers set',
      cacheControl: 'public, max-age=60',
      etag: '"day4-cache-demo-v1"'
    }, null, 2));

  // ─── 404 ─────────────────────────────────────────────
  } else {
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      error: 'Route not found',
      availableRoutes: ['/echo', '/slow?ms=3000', '/cache']
    }, null, 2));
  }
});

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
  console.log('Available endpoints:');
  console.log(`  http://localhost:${PORT}/echo`);
  console.log(`  http://localhost:${PORT}/slow?ms=3000`);
  console.log(`  http://localhost:${PORT}/cache`);
});
