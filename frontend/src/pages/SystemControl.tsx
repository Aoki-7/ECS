import { useState } from 'react'
import './SystemControl.css'

function SystemControl() {
  const [running, setRunning] = useState(false)
  const [paused, setPaused] = useState(false)
  const [systems] = useState([
    { name: 'PhysiologyNeedsSystem', enabled: true, tickInterval: 5 },
    { name: 'PerceptionSystem', enabled: true, tickInterval: 10 },
    { name: 'EmotionSystem', enabled: true, tickInterval: 10 },
    { name: 'DecisionSystem', enabled: true, tickInterval: 15 },
    { name: 'ActionSystem', enabled: true, tickInterval: 1 },
  ])

  return (
    <div className="system-control">
      <div className="control-panel">
        <h2>模拟控制</h2>
        <div className="buttons">
          <button
            className={running ? 'active' : ''}
            onClick={() => setRunning(true)}
          >
            ▶ 运行
          </button>
          <button
            className={paused ? 'active' : ''}
            onClick={() => { setPaused(true); setRunning(false) }}
          >
            ⏸ 暂停
          </button>
          <button onClick={() => { setRunning(false); setPaused(false) }}>
            ⏹ 停止
          </button>
          <button>⏭ 步进</button>
        </div>
        <div className="status">
          <p>状态: {running ? '运行中' : paused ? '已暂停' : '已停止'}</p>
          <p>Tick: 0</p>
          <p>FPS: 60</p>
        </div>
      </div>
      <div className="system-list">
        <h2>系统列表</h2>
        <table>
          <thead>
            <tr>
              <th>系统名称</th>
              <th>状态</th>
              <th>Tick间隔</th>
            </tr>
          </thead>
          <tbody>
            {systems.map(system => (
              <tr key={system.name}>
                <td>{system.name}</td>
                <td>
                  <span className={system.enabled ? 'enabled' : 'disabled'}>
                    {system.enabled ? '●' : '○'}
                  </span>
                </td>
                <td>{system.tickInterval}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default SystemControl
