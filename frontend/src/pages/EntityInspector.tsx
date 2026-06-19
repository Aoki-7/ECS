import { useState } from 'react'
import './EntityInspector.css'

function EntityInspector() {
  const [selectedEntity, setSelectedEntity] = useState<number | null>(null)
  const [entities] = useState([
    { id: 1, type: 'Human', position: '(10, 20)' },
    { id: 2, type: 'Animal', position: '(15, 25)' },
    { id: 3, type: 'Plant', position: '(30, 40)' },
  ])

  return (
    <div className="entity-inspector">
      <div className="entity-list">
        <h2>实体列表</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>类型</th>
              <th>位置</th>
            </tr>
          </thead>
          <tbody>
            {entities.map(entity => (
              <tr
                key={entity.id}
                className={selectedEntity === entity.id ? 'selected' : ''}
                onClick={() => setSelectedEntity(entity.id)}
              >
                <td>{entity.id}</td>
                <td>{entity.type}</td>
                <td>{entity.position}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="entity-detail">
        <h2>实体详情</h2>
        {selectedEntity ? (
          <div>
            <p>ID: {selectedEntity}</p>
            <p>组件: (TODO)</p>
          </div>
        ) : (
          <p className="placeholder">选择一个实体查看详情</p>
        )}
      </div>
    </div>
  )
}

export default EntityInspector
