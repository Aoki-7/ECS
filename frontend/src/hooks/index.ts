/**
 * React Hooks
 * 
 * 版本: v4.0
 */

import { useState, useEffect, useCallback } from 'react'
import { wsClient } from '../services/api'

/**
 * WebSocket Hook
 * 
 * 使用:
 * const { connected, send } = useWebSocket()
 */
export function useWebSocket() {
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    wsClient.connect()

    // 简化处理：直接设置连接状态
    setTimeout(() => setConnected(true), 100)

    return () => {
      wsClient.disconnect()
    }
  }, [])

  const send = useCallback((action: string, data?: any) => {
    wsClient.send(action, data)
  }, [])

  return { connected, send }
}

/**
 * World Stats Hook
 * 
 * 使用:
 * const { stats, loading, error } = useWorldStats()
 */
export function useWorldStats() {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<any>(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const { worldApi } = await import('../services/api')
        const data: any = await worldApi.getStats()
        setStats(data)
      } catch (err: any) {
        setError(err)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  return { stats, loading, error }
}

/**
 * Entity List Hook
 * 
 * 使用:
 * const { entities, loading, error } = useEntityList(limit, offset)
 */
export function useEntityList(limit = 100, offset = 0) {
  const [entities, setEntities] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<any>(null)

  useEffect(() => {
    const fetchEntities = async () => {
      try {
        const { worldApi } = await import('../services/api')
        const data: any = await worldApi.getEntities(limit, offset)
        setEntities(data.entities || [])
      } catch (err: any) {
        setError(err)
      } finally {
        setLoading(false)
      }
    }

    fetchEntities()
  }, [limit, offset])

  return { entities, loading, error }
}

/**
 * System Status Hook
 * 
 * 使用:
 * const { status, run, pause, step } = useSystemStatus()
 */
export function useSystemStatus() {
  const [status, setStatus] = useState({
    running: false,
    paused: false,
    tick: 0,
  })

  const run = useCallback(async () => {
    try {
      const { systemApi } = await import('../services/api')
      await systemApi.run()
      setStatus(prev => ({ ...prev, running: true, paused: false }))
    } catch (err) {
      console.error('Run failed:', err)
    }
  }, [])

  const pause = useCallback(async () => {
    try {
      const { systemApi } = await import('../services/api')
      await systemApi.pause()
      setStatus(prev => ({ ...prev, running: false, paused: true }))
    } catch (err) {
      console.error('Pause failed:', err)
    }
  }, [])

  const step = useCallback(async (dt = 1.0) => {
    try {
      const { systemApi } = await import('../services/api')
      await systemApi.step(dt)
      setStatus(prev => ({ ...prev, tick: prev.tick + 1 }))
    } catch (err) {
      console.error('Step failed:', err)
    }
  }, [])

  return { status, run, pause, step }
}
