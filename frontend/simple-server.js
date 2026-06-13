const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
const BASE_DIR = '/home/marcelo/Documents/costaricatravel/frontend/.output/server';

const mimeTypes = {
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.mjs': 'application/javascript'
};

const server = http.createServer((req, res) => {
  console.log(`Request: ${req.url}`);

  // Serve index.html for all routes (SPA)
  let filePath = path.join(BASE_DIR, 'client', req.url);

  // If file doesn't exist, serve index.html
  if (!fs.existsSync(filePath)) {
    filePath = path.join(BASE_DIR, 'client', 'index.html');
  }

  const ext = path.extname(filePath);
  const contentType = mimeTypes[ext] || 'text/plain';

  try {
    const content = fs.readFileSync(filePath);
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(content);
  } catch (err) {
    res.writeHead(404);
    res.end('Not Found');
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});
