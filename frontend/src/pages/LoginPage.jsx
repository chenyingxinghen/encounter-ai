import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'

function LoginPage({ onLogin }) {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await axios.post('/api/auth/login', formData)
      onLogin(response.data.user)
    } catch (err) {
      setError(err.response?.data?.detail || '登录失败，请检查邮箱和密码')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
      <div className="card" style={{ maxWidth: '400px', width: '100%' }}>
        <h1 style={{ textAlign: 'center', color: '#667eea', marginBottom: '24px' }}>
          青春伴行
        </h1>
        <h2 style={{ textAlign: 'center', marginBottom: '32px', color: '#334155' }}>
          登录
        </h2>
        
        {error && (
          <div style={{ 
            padding: '12px', 
            background: '#fee2e2', 
            color: '#991b1b', 
            borderRadius: '8px', 
            marginBottom: '16px' 
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div>
            <label className="label">邮箱</label>
            <input
              type="email"
              name="email"
              className="input"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="请输入邮箱"
            />
          </div>

          <div>
            <label className="label">密码</label>
            <input
              type="password"
              name="password"
              className="input"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="请输入密码"
            />
          </div>

          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{ width: '100%', marginTop: '8px' }}
            disabled={loading}
          >
            {loading ? '登录中...' : '登录'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '24px' }}>
          <span style={{ color: '#64748b' }}>还没有账号？</span>
          <Link to="/register" style={{ color: '#667eea', marginLeft: '8px', textDecoration: 'none' }}>
            立即注册
          </Link>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
