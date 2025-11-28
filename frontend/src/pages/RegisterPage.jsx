import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'

function RegisterPage({ onRegister }) {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    school: '',
    major: '',
    grade: ''
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
      const response = await axios.post('/api/auth/register', formData)
      onRegister(response.data.user)
      navigate('/assessment')
    } catch (err) {
      setError(err.response?.data?.detail || '注册失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', paddingTop: '40px', paddingBottom: '40px' }}>
      <div className="card" style={{ maxWidth: '500px', width: '100%' }}>
        <h1 style={{ textAlign: 'center', color: '#667eea', marginBottom: '24px' }}>
          青春伴行
        </h1>
        <h2 style={{ textAlign: 'center', marginBottom: '32px', color: '#334155' }}>
          注册账号
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
            <label className="label">用户名</label>
            <input
              type="text"
              name="username"
              className="input"
              value={formData.username}
              onChange={handleChange}
              required
              placeholder="请输入用户名"
            />
          </div>

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
              minLength="6"
              placeholder="请输入密码（至少6位）"
            />
          </div>

          <div>
            <label className="label">学校</label>
            <input
              type="text"
              name="school"
              className="input"
              value={formData.school}
              onChange={handleChange}
              required
              placeholder="请输入学校名称"
            />
          </div>

          <div>
            <label className="label">专业</label>
            <input
              type="text"
              name="major"
              className="input"
              value={formData.major}
              onChange={handleChange}
              required
              placeholder="请输入专业"
            />
          </div>

          <div>
            <label className="label">年级</label>
            <select
              name="grade"
              className="input"
              value={formData.grade}
              onChange={handleChange}
              required
            >
              <option value="">请选择年级</option>
              <option value="1">大一</option>
              <option value="2">大二</option>
              <option value="3">大三</option>
              <option value="4">大四</option>
              <option value="5">研一</option>
              <option value="6">研二</option>
              <option value="7">研三</option>
            </select>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{ width: '100%', marginTop: '8px' }}
            disabled={loading}
          >
            {loading ? '注册中...' : '注册'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '24px' }}>
          <span style={{ color: '#64748b' }}>已有账号？</span>
          <Link to="/login" style={{ color: '#667eea', marginLeft: '8px', textDecoration: 'none' }}>
            立即登录
          </Link>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage
