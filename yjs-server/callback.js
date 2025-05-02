// callback.js
import http from 'http';

const CALLBACK_URL = process.env.CALLBACK_URL
  ? new URL(process.env.CALLBACK_URL)
  : null;
const CALLBACK_TIMEOUT = parseInt(process.env.CALLBACK_TIMEOUT, 10) || 5000;
const CALLBACK_OBJECTS = process.env.CALLBACK_OBJECTS
  ? JSON.parse(process.env.CALLBACK_OBJECTS)
  : {};

/**
 * `true` if we have a callback URL configured.
 */
export const isCallbackSet = Boolean(CALLBACK_URL);

/**
 * This handler will be called (debounced) on every Yjs update.
 *
 * @param {Uint8Array} update
 * @param {any} origin
 * @param {WSSharedDoc} doc
 */
export function callbackHandler(update, origin, doc) {
  if (!CALLBACK_URL) return;
  const room = doc.name;
  const dataToSend = { room, data: {} };

  // Build up the payload from configured shared objects
  for (const [name, type] of Object.entries(CALLBACK_OBJECTS)) {
    const content = getContent(name, type, doc);
    dataToSend.data[name] = {
      type,
      content: content?.toJSON?.() ?? null,
    };
  }

  doCallbackRequest(CALLBACK_URL, CALLBACK_TIMEOUT, dataToSend);
}

/**
 * Fire off the HTTP POST to your callback URL.
 *
 * @param {URL} url
 * @param {number} timeout
 * @param {object} data
 */
function doCallbackRequest(url, timeout, data) {
  const body = JSON.stringify(data);
  const options = {
    hostname: url.hostname,
    port: url.port,
    path: url.pathname,
    method: 'POST',
    timeout,
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(body),
    },
  };

  const req = http.request(options);
  req.on('timeout', () => {
    console.warn('Callback request timed out.');
    req.abort();
  });
  req.on('error', (err) => {
    console.error('Callback request error:', err);
    req.abort();
  });

  req.write(body);
  req.end();
}

/**
 * Pick the right Yjs data type instance off the document.
 * @param {string} name
 * @param {string} type
 * @param {WSSharedDoc} doc
 */
function getContent(name, type, doc) {
  switch (type) {
    case 'Array': return doc.getArray(name);
    case 'Map': return doc.getMap(name);
    case 'Text': return doc.getText(name);
    case 'XmlFragment': return doc.getXmlFragment(name);
    case 'XmlElement': return doc.getXmlElement(name);
    default: return null;
  }
}
