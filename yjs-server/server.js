// server.js
import http from 'http';
import { WebSocketServer } from 'ws';
import { setupWSConnection } from './utils.js';

const wss = new WebSocketServer({ noServer: true });
const host = process.env.HOST || 'localhost';
const port = parseInt(process.env.PORT, 10) || 1234;

const server = http.createServer((request, response) => {
  response.writeHead(200, { 'Content-Type': 'text/plain' });
  response.end('okay');
});

// Handle new WebSocket connections
wss.on('connection', setupWSConnection);

// Upgrade HTTP -> WebSocket
server.on('upgrade', (request, socket, head) => {
  // You can do auth here if you like, then:
  wss.handleUpgrade(request, socket, head, (ws) => {
    wss.emit('connection', ws, request);
  });
});

server.listen(port, host, () => {
  console.log(`running at '${host}' on port ${port}`);
});
