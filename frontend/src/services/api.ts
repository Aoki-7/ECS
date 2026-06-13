/**
 * API 服务层
 * 
 * 提供与后端 FastAPI 的通信:
 * - HTTP REST API
 * - WebSocket 实时事件
 * - 请求缓存
 * 
 * 版本: v4.0
 */

const API_BASE_URL = '/api'
const WS_URL = '/ws/events'

// 简单缓存
const cache = new Map<string, { data: any; timestamp: number }>()
const CACHE_TTL = 5000 // 5秒缓存

function getCacheKey(method: string, path: string, data?: string): string {
  return `${method}:${path}:${data || ''}`
}

function getCached<T>(key: string): T | null {
  const cached = cache.get(key)
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data
  }
  return null
}

function setCache(key: string, data: any): void {
  cache.set(key, { data, timestamp: Date.now() })
}

/**
 * HTTP GET 请求 (带缓存)
 */
export async function get<T>(path: string, useCache = true): Promise<T> {
  const cacheKey = getCacheKey('GET', path)
  
  if (useCache) {
    const cached = getCached<T>(cacheKey)
    if (cached) return cached
  }
  
  const response = await fetch(`${API_BASE_URL}${path}`)
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }
  const data = await response.json()
  
  if (useCache) {
    setCache(cacheKey, data)
  }
  
  return data
}

/**
 * HTTP POST 请求 (清除缓存)
 */
export async function post<T>(path: string, data?: object): Promise<T> {
  // POST 请求清除相关缓存
  cache.clear()
  
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: data ? JSON.stringify(data) : undefined,
  })
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }
  return response.json()
}

/**
 * HTTP PUT 请求
 */
export async function put<T>(path: string, data: object): Promise<T> {
  cache.clear()
  
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }
  return response.json()
}

/**
 * HTTP DELETE 请求
 */
export async function del<T>(path: string): Promise<T> {
  cache.clear()
  
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }
  return response.json()
}

/**
 * World API
 */
export const worldApi = {
  getStats: () => get('/world/stats'),
  query: (componentTypes: string[]) => get(`/world/query?component_types=${componentTypes.join(',')}`),
  getArchetypes: () => get('/world/archetypes'),
  getEntities: (limit = 100, offset = 0) => get(`/world/entities?limit=${limit}&offset=${offset}`),
}

/**
 * Entity API
 */
export const entityApi = {
  get: (id: number) => get(`/entity/${id}`),
  getComponents: (id: number) => get(`/entity/${id}/components`),
  create: (data: object) => post('/entity/', data),
  update: (id: number, data: object) => put(`/entity/${id}`, data),
  delete: (id: number) => del(`/entity/${id}`),
}

/**
 * System API
 */
export const systemApi = {
  run: () => post('/system/run'),
  pause: () => post('/system/pause'),
  resume: () => post('/system/resume'),
  step: (dt = 1.0) => post(`/system/step?dt=${dt}`),
  getStatus: () => get('/system/status'),
  list: () => get('/system/list'),
}

/**
 * Snapshot API
 */
export const snapshotApi = {
  save: (name: string, description?: string) => post('/snapshot/save', { name, description }),
  load: (id: number) => post(`/snapshot/load/${id}`),
  list: () => get('/snapshot/list'),
  get: (id: number) => get(`/snapshot/${id}`),
  delete: (id: number) => del(`/snapshot/${id}`),
}

/**
 * WebSocket 连接
 */
export class WebSocketClient {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private listeners: Map<string, ((data: any) => void)[]> = new Map()
  private heartbeatInterval: number | null = null

  connect() {
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}${WS_URL}`
    this.ws = new WebSocket(wsUrl)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      this.startHeartbeat()
    }

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      this.emit(message.type, message.data)
    }

    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
      this.stopHeartbeat()
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++
        setTimeout(() => this.connect(), 1000 * this.reconnectAttempts)
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }

  disconnect() {
    this.stopHeartbeat()
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  private startHeartbeat() {
    this.heartbeatInterval = window.setInterval(() => {
      this.send('ping')
    }, 30000)
  }

  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  on(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event)!.push(callback)
  }

  off(event: string, callback: (data: any) => void) {
    const callbacks = this.listeners.get(event)
    if (callbacks) {
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  private emit(event: string, data: any) {
    const callbacks = this.listeners.get(event)
    if (callbacks) {
      callbacks.forEach(callback => callback(data))
    }
  }

  send(action: string, data?: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action, data }))
    }
  }
}

// 全局 WebSocket 实例
export const wsClient = new WebSocketClient()
