import React from 'react'
import { Link, useLocation } from 'react-router-dom'

function Navigation({ onLogout, user }) {
  const location = useLocation()

  return (
    <nav className="nav">
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <h2 style={{ color: '#667eea', margin: 0 }}>青春伴行</h2>
        <div className="nav-links">
          <Link 
            to="/matching" 
            className={`nav-link ${location.pathname === '/matching' ? 'active' : ''}`}
          >
            匹配
          </Link>
          <Link 
            to="/chat" 
            className={`nav-link ${location.pathname.startsWith('/chat') ? 'active' : ''}`}
          >
            对话
          </Link>
          <Link 
            to="/profile" 
            className={`nav-link ${location.pathname === '/profile' ? 'active' : ''}`}
          >
            个人中心
          </Link>
          <Link 
            to="/report" 
            className={`nav-link ${location.pathname === '/report' ? 'active' : ''}`}
          >
            成长报告
          </Link>
          <Link 
            to="/settings" 
            className={`nav-link ${location.pathname === '/settings' ? 'active' : ''}`}
          >
            设置
          </Link>
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <span style={{ color: '#64748b' }}>{user?.username || '用户'}</span>
        <button onClick={onLogout} className="btn btn-secondary">
          退出登录
        </button>
      </div>
    </nav>
  )
}

export default Navigation
