import { Outlet, NavLink } from 'react-router-dom'
import './Layout.css'

function Layout() {
  return (
    <div className="layout">
      <nav className="sidebar">
        <div className="logo">ECS World</div>
        <ul className="nav-list">
          <li>
            <NavLink to="/" end className={({ isActive }) => isActive ? 'active' : ''}>
              🌍 世界视图
            </NavLink>
          </li>
          <li>
            <NavLink to="/entities" className={({ isActive }) => isActive ? 'active' : ''}>
              👤 实体检查
            </NavLink>
          </li>
          <li>
            <NavLink to="/systems" className={({ isActive }) => isActive ? 'active' : ''}>
              ⚙️ 系统控制
            </NavLink>
          </li>
          <li>
            <NavLink to="/stats" className={({ isActive }) => isActive ? 'active' : ''}>
              📊 统计面板
            </NavLink>
          </li>
        </ul>
        <div className="status-bar">
          <ConnectionStatus />
        </div>
      </nav>
      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}

function ConnectionStatus() {
  // TODO: 使用 WebSocket hook
  return (
    <div className="connection-status connected">
      ● 已连接
    </div>
  )
}

export default Layout
