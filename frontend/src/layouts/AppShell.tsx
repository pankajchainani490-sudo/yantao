import { NavLink, Outlet } from 'react-router-dom'

import { consoleRoutes } from '../router/routes'

function AppShell() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">机器学习流量安全</p>
          <h1>恶意流量识别控制台</h1>
          <p className="subtitle">
            基于决策树和随机森林的恶意流量识别与处置演示系统。
          </p>
        </div>

        <nav className="nav-links" aria-label="主导航">
          {consoleRoutes.map((route) => (
            <NavLink
              key={route.path}
              to={route.navPath}
              className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
              end={route.index}
            >
              {route.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}

export default AppShell
