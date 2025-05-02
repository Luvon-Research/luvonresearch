// utils.js
import * as Y from 'yjs'
import * as syncProtocol from 'y-protocols/dist/sync.cjs'
import * as awarenessProtocol from 'y-protocols/dist/awareness.cjs'

import * as encoding from 'lib0/dist/encoding.cjs'
import * as decoding from 'lib0/dist/decoding.cjs'
import * as map from 'lib0/dist/map.cjs'

import debounce from 'lodash.debounce'

import { callbackHandler, isCallbackSet } from './callback.js'

const CALLBACK_DEBOUNCE_WAIT = parseInt(process.env.CALLBACK_DEBOUNCE_WAIT) || 2000
const CALLBACK_DEBOUNCE_MAXWAIT = parseInt(process.env.CALLBACK_DEBOUNCE_MAXWAIT) || 10000

const wsReadyStateConnecting = 0
const wsReadyStateOpen = 1
const wsReadyStateClosing = 2
const wsReadyStateClosed = 3

const gcEnabled = process.env.GC !== 'false' && process.env.GC !== '0'
const persistenceDir = process.env.YPERSISTENCE

let persistence = null
if (typeof persistenceDir === 'string') {
  console.info('Persisting documents to "' + persistenceDir + '"')
  const { LeveldbPersistence } = await import('y-leveldb')
  const ldb = new LeveldbPersistence(persistenceDir)
  persistence = {
    provider: ldb,
    bindState: async (docName, ydoc) => {
      const persistedYdoc = await ldb.getYDoc(docName)
      const newUpdates = Y.encodeStateAsUpdate(ydoc)
      ldb.storeUpdate(docName, newUpdates)
      Y.applyUpdate(ydoc, Y.encodeStateAsUpdate(persistedYdoc))
      ydoc.on('update', update => ldb.storeUpdate(docName, update))
    },
    writeState: async (docName, ydoc) => {}
  }
}

export function setPersistence(p) {
  persistence = p
}

export function getPersistence() {
  return persistence
}

export const docs = new Map()

const messageSync = 0
const messageAwareness = 1

function updateHandler(update, origin, doc) {
  const encoder = encoding.createEncoder()
  encoding.writeVarUint(encoder, messageSync)
  syncProtocol.writeUpdate(encoder, update)
  const msg = encoding.toUint8Array(encoder)
  for (const conn of doc.conns.keys()) {
    send(doc, conn, msg)
  }
}

class WSSharedDoc extends Y.Doc {
  constructor(name) {
    super({ gc: gcEnabled })
    this.name = name
    this.conns = new Map()
    this.awareness = new awarenessProtocol.Awareness(this)
    this.awareness.setLocalState(null)

    this.awareness.on('update', ({ added, updated, removed }, conn) => {
      const changed = added.concat(updated, removed)
      if (conn) {
        const ctr = this.conns.get(conn) || new Set()
        added.forEach(id => ctr.add(id))
        removed.forEach(id => ctr.delete(id))
        this.conns.set(conn, ctr)
      }
      const encoder = encoding.createEncoder()
      encoding.writeVarUint(encoder, messageAwareness)
      encoding.writeVarUint8Array(
        encoder,
        awarenessProtocol.encodeAwarenessUpdate(this.awareness, changed)
      )
      const buf = encoding.toUint8Array(encoder)
      for (const c of this.conns.keys()) send(this, c, buf)
    })

    this.on('update', updateHandler)

    if (isCallbackSet) {
      this.on(
        'update',
        debounce(callbackHandler, CALLBACK_DEBOUNCE_WAIT, {
          maxWait: CALLBACK_DEBOUNCE_MAXWAIT
        })
      )
    }
  }
}

export function getYDoc(docName, gc = true) {
  if (!docs.has(docName)) {
    const doc = new WSSharedDoc(docName)
    doc.gc = gc
    if (persistence) persistence.bindState(docName, doc)
    docs.set(docName, doc)
  }
  return docs.get(docName)
}

function closeConn(doc, conn) {
  if (!doc.conns.has(conn)) return
  const ctr = doc.conns.get(conn)
  doc.conns.delete(conn)
  awarenessProtocol.removeAwarenessStates(
    doc.awareness,
    Array.from(ctr),
    null
  )
  if (doc.conns.size === 0 && persistence) {
    persistence.writeState(doc.name, doc).then(() => doc.destroy())
    docs.delete(doc.name)
  }
  conn.close()
}

function send(doc, conn, m) {
  if (
    conn.readyState !== wsReadyStateConnecting &&
    conn.readyState !== wsReadyStateOpen
  ) {
    return closeConn(doc, conn)
  }
  try {
    conn.send(m, err => err && closeConn(doc, conn))
  } catch {
    closeConn(doc, conn)
  }
}

export function setupWSConnection(conn, req, { docName = req.url.slice(1).split('?')[0], gc = true } = {}) {
  conn.binaryType = 'arraybuffer'
  const doc = getYDoc(docName, gc)
  doc.conns.set(conn, new Set())

  conn.on('message', message => messageListener(conn, doc, new Uint8Array(message)))

  let pongOk = true
  const interval = setInterval(() => {
    if (!pongOk) {
      closeConn(doc, conn)
      clearInterval(interval)
    } else if (doc.conns.has(conn)) {
      pongOk = false
      conn.ping()
    }
  }, 30000)

  conn.on('close', () => {
    closeConn(doc, conn)
    clearInterval(interval)
  })
  conn.on('pong', () => (pongOk = true))

  // initial sync
  {
    const encoder = encoding.createEncoder()
    encoding.writeVarUint(encoder, messageSync)
    syncProtocol.writeSyncStep1(encoder, doc)
    send(doc, conn, encoding.toUint8Array(encoder))

    const states = doc.awareness.getStates()
    if (states.size) {
      const enc = encoding.createEncoder()
      encoding.writeVarUint(enc, messageAwareness)
      encoding.writeVarUint8Array(
        enc,
        awarenessProtocol.encodeAwarenessUpdate(doc.awareness, Array.from(states.keys()))
      )
      send(doc, conn, encoding.toUint8Array(enc))
    }
  }
}

function messageListener(conn, doc, message) {
  try {
    const decoder = decoding.createDecoder(message)
    const encoder = encoding.createEncoder()
    const msgType = decoding.readVarUint(decoder)
    switch (msgType) {
      case messageSync:
        encoding.writeVarUint(encoder, messageSync)
        syncProtocol.readSyncMessage(decoder, encoder, doc, conn)
        if (encoding.length(encoder) > 1) {
          send(doc, conn, encoding.toUint8Array(encoder))
        }
        break
      case messageAwareness:
        awarenessProtocol.applyAwarenessUpdate(
          doc.awareness,
          decoding.readVarUint8Array(decoder),
          conn
        )
        break
    }
  } catch (e) {
    console.error(e)
    doc.emit('error', [e])
  }
}
