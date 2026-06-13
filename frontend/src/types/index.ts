/**
 * 类型定义
 * 
 * 版本: v4.0
 */

export interface Entity {
  id: number
  generation: number
  components?: Record<string, any>
}

export interface WorldStats {
  entities: {
    created: number
    destroyed: number
    active: number
  }
  components: {
    archetypeCount: number
    entityCount: number
    cacheHitRate: number
  }
  systems: {
    registered: number
    executed: number
    skipped: number
  }
}

export interface SystemInfo {
  name: string
  enabled: boolean
  tickInterval: number
  priority: number
}

export interface Snapshot {
  id: number
  name: string
  description?: string
  createdAt: string
  size: number
}

export interface HistoryEntry {
  id: number
  tick: number
  entityId?: number
  eventType: string
  eventData: Record<string, any>
  createdAt: string
}

export interface WebSocketMessage {
  type: string
  data: any
  timestamp: number
}
