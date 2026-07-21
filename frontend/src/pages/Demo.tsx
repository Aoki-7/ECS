import React, { useEffect, useRef, useState, useCallback } from 'react'
import PixelCanvas, { WorldSnapshot, EntitySnapshot } from '../components/PixelCanvas'
import './Demo.css'

interface ControlMessage {
  type: 'control'
  action: 'pause' | 'resume' | 'toggle' | 'set_speed' | 'step' | 'reset'
  value?: number
}

const Demo: React.FC = () => {
  const wsRef = useRef<WebSocket | null>(null)
  const [snapshot, setSnapshot] = useState<WorldSnapshot | null>(null)
  const [connected, setConnected] = useState(false)
  const [selected, setSelected] = useState<EntitySnapshot | null>(null)
  const [speed, setSpeed] = useState(1)
  const [paused, setPaused] = useState(false)
  const [entityDetail, setEntityDetail] = useState<Record<string, any> | null>(null)

  useEffect(() => {
    const ws = new WebSocket('/ws/world')
    wsRef.current = ws

    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)
    ws.onerror = (err) => {
      console.error('WebSocket error', err)
      setConnected(false)
    }
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'snapshot') {
          setSnapshot(data)
          setPaused(data.config.paused)
          setSpeed(data.config.speed)
        } else if (data.type === 'entity_detail') {
          setEntityDetail(data.entity)
        }
      } catch (e) {
        console.error('parse ws message failed', e)
      }
    }

    return () => {
      ws.close()
    }
  }, [])

  const sendControl = useCallback((action: ControlMessage['action'], value?: number) => {
    const ws = wsRef.current
    if (!ws || ws.readyState !== WebSocket.OPEN) return
    const msg: ControlMessage = { type: 'control', action }
    if (value !== undefined) msg.value = value
    ws.send(JSON.stringify(msg))
  }, [])

  const handleEntityClick = useCallback((entity: EntitySnapshot) => {
    setSelected(entity)
    const ws = wsRef.current
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'query_entity', entity_id: entity.id }))
    }
  }, [])

  const stats = snapshot?.stats || {}
  const tick = snapshot?.tick || 0

  return (
    <div className="demo-container">
      <header className="demo-header">
        <h1>ECS 世界模拟</h1>
        <div className="demo-status">
          <span className={`status-dot ${connected ? 'online' : 'offline'}`} />
          {connected ? '实时连接' : '连接断开'}
          <span className="tick">步数 {tick}</span>
        </div>
      </header>

      <div className="demo-main">
        <div className="demo-canvas-panel">
          {snapshot ? (
            <PixelCanvas
              snapshot={snapshot}
              scale={8}
              onEntityClick={handleEntityClick}
            />
          ) : (
            <div className="loading">正在连接世界…</div>
          )}
        </div>

        <aside className="demo-sidebar">
          <section className="panel controls">
            <h2>控制</h2>
            <div className="control-row">
              <button onClick={() => sendControl('toggle')}>
                {paused ? '▶ 继续' : '⏸ 暂停'}
              </button>
              <button onClick={() => sendControl('step')}>⏭ 单步</button>
              <button onClick={() => sendControl('reset')}>↺ 重置</button>
            </div>
            <div className="control-row speed">
              <label>速度</label>
              <input
                type="range"
                min={0}
                max={5}
                step={0.5}
                value={speed}
                onChange={(e) => {
                  const v = parseFloat(e.target.value)
                  setSpeed(v)
                  sendControl('set_speed', v)
                }}
              />
              <span>{speed.toFixed(1)}x</span>
            </div>
          </section>

          <section className="panel stats">
            <h2>统计</h2>
            <div className="stat-grid">
              <div><span>总人口</span><strong>{stats.humans ?? '-'}</strong></div>
              <div><span>植物</span><strong>{stats.plants ?? '-'}</strong></div>
              <div><span>动物</span><strong>{stats.animals ?? '-'}</strong></div>
              <div><span>食物</span><strong>{stats.food ?? '-'}</strong></div>
              <div><span>水源</span><strong>{stats.water ?? '-'}</strong></div>
              <div><span>建筑</span><strong>{stats.buildings ?? '-'}</strong></div>
              <div><span>总实体</span><strong>{stats.total ?? '-'}</strong></div>
              <div><span>出生/死亡</span><strong>{stats.births ?? 0}/{stats.deaths ?? 0}</strong></div>
            </div>
          </section>

          <section className="panel inspector">
            <h2>实体详情</h2>
            {selected ? (
              <div className="entity-card">
                <div className="entity-title">
                  <span
                    className="entity-dot"
                    style={{
                      background:
                        selected.type === 'human'
                          ? '#f5e6d3'
                          : selected.type === 'plant'
                          ? '#4caf50'
                          : selected.type === 'water'
                          ? '#2196f3'
                          : '#ff9800',
                    }}
                  />
                  {selected.type} #{selected.id}
                </div>
                <div className="entity-pos">
                  x:{selected.x} y:{selected.y}
                </div>
                {selected.state && (
                  <ul className="entity-state">
                    {Object.entries(selected.state).map(([k, v]) => (
                      <li key={k}>
                        <span>{k}</span>
                        <span>{String(v)}</span>
                      </li>
                    ))}
                  </ul>
                )}
                {entityDetail && entityDetail.components && (
                  <details className="entity-components">
                    <summary>全部组件</summary>
                    <ul>
                      {Object.keys(entityDetail.components).map((name) => (
                        <li key={name}>{name}</li>
                      ))}
                    </ul>
                  </details>
                )}
              </div>
            ) : (
              <p className="placeholder">点击像素查看实体</p>
            )}
          </section>
        </aside>
      </div>
    </div>
  )
}

export default Demo
