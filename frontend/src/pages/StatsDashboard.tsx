import { useState } from 'react'
import './StatsDashboard.css'

function StatsDashboard() {
  const [stats] = useState({
    entities: { created: 100, destroyed: 10, active: 90 },
    components: { archetypeCount: 15, entityCount: 90, cacheHitRate: 0.95 },
    systems: { registered: 20, executed: 18, skipped: 2 },
  })

  return (
    <div className="stats-dashboard">
      <h2>统计面板</h2>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>实体</h3>
          <div className="stat-value">{stats.entities.active}</div>
          <div className="stat-detail">
            <p>创建: {stats.entities.created}</p>
            <p>销毁: {stats.entities.destroyed}</p>
          </div>
        </div>
        <div className="stat-card">
          <h3>组件</h3>
          <div className="stat-value">{stats.components.archetypeCount}</div>
          <div className="stat-detail">
            <p>实体: {stats.components.entityCount}</p>
            <p>缓存命中率: {(stats.components.cacheHitRate * 100).toFixed(1)}%</p>
          </div>
        </div>
        <div className="stat-card">
          <h3>系统</h3>
          <div className="stat-value">{stats.systems.executed}</div>
          <div className="stat-detail">
            <p>注册: {stats.systems.registered}</p>
            <p>跳过: {stats.systems.skipped}</p>
          </div>
        </div>
      </div>
      <div className="chart-placeholder">
        <p>图表区域 (TODO: 集成图表库)</p>
      </div>
    </div>
  )
}

export default StatsDashboard
