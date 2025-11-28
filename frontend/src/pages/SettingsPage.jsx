import React, { useState, useEffect } from 'react'
import axios from 'axios'

function SettingsPage({ user }) {
  const [settings, setSettings] = useState({
    ai_assistant_enabled: true,
    anonymous_mode: false,
    notification_enabled: true,
    data_collection_consent: true
  })
  const [loading, setLoading] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [showPrivacyPolicy, setShowPrivacyPolicy] = useState(false)

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      const response = await axios.get(`/api/users/settings/${user.user_id}`)
      setSettings(response.data)
    } catch (err) {
      console.error('获取设置失败', err)
    }
  }

  const handleToggle = async (key) => {
    const newSettings = { ...settings, [key]: !settings[key] }
    setSettings(newSettings)
    
    try {
      await axios.put(`/api/users/settings/${user.user_id}`, newSettings)
    } catch (err) {
      alert('保存设置失败')
      setSettings(settings) // Revert on error
    }
  }

  const handleDeleteAccount = async () => {
    setLoading(true)
    try {
      await axios.delete(`/api/users/${user.user_id}`)
      alert('账号已删除')
      window.location.href = '/login'
    } catch (err) {
      alert('删除账号失败')
    } finally {
      setLoading(false)
      setShowDeleteConfirm(false)
    }
  }

  const handleExportData = async () => {
    try {
      const response = await axios.get(
        `/api/users/data/export?user_id=${user.user_id}`,
        { responseType: 'blob' }
      )
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `user_data_${user.user_id}_${new Date().toISOString().split('T')[0]}.json`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      alert('导出数据失败')
    }
  }

  return (
    <div className="container" style={{ paddingTop: '40px', paddingBottom: '40px' }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <h2 style={{ color: '#334155', marginBottom: '32px' }}>设置</h2>

        {/* AI Assistant Settings */}
        <div className="card">
          <h3 style={{ marginBottom: '20px', color: '#334155' }}>AI助手设置</h3>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            padding: '16px 0',
            borderBottom: '1px solid #e2e8f0'
          }}>
            <div>
              <div style={{ fontWeight: '500', marginBottom: '4px' }}>启用AI对话助手</div>
              <div style={{ fontSize: '14px', color: '#64748b' }}>
                在对话沉默时提供话题建议和情绪支持
              </div>
            </div>
            <label style={{ 
              position: 'relative', 
              display: 'inline-block', 
              width: '50px', 
              height: '28px' 
            }}>
              <input
                type="checkbox"
                checked={settings.ai_assistant_enabled}
                onChange={() => handleToggle('ai_assistant_enabled')}
                style={{ opacity: 0, width: 0, height: 0 }}
              />
              <span style={{
                position: 'absolute',
                cursor: 'pointer',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: settings.ai_assistant_enabled ? '#667eea' : '#cbd5e1',
                transition: '0.3s',
                borderRadius: '28px'
              }}>
                <span style={{
                  position: 'absolute',
                  content: '',
                  height: '20px',
                  width: '20px',
                  left: settings.ai_assistant_enabled ? '26px' : '4px',
                  bottom: '4px',
                  background: 'white',
                  transition: '0.3s',
                  borderRadius: '50%'
                }} />
              </span>
            </label>
          </div>
        </div>

        {/* Privacy Settings */}
        <div className="card">
          <h3 style={{ marginBottom: '20px', color: '#334155' }}>隐私设置</h3>
          
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            padding: '16px 0',
            borderBottom: '1px solid #e2e8f0'
          }}>
            <div>
              <div style={{ fontWeight: '500', marginBottom: '4px' }}>匿名模式</div>
              <div style={{ fontSize: '14px', color: '#64748b' }}>
                隐藏真实身份信息（姓名、学校等）
              </div>
            </div>
            <label style={{ 
              position: 'relative', 
              display: 'inline-block', 
              width: '50px', 
              height: '28px' 
            }}>
              <input
                type="checkbox"
                checked={settings.anonymous_mode}
                onChange={() => handleToggle('anonymous_mode')}
                style={{ opacity: 0, width: 0, height: 0 }}
              />
              <span style={{
                position: 'absolute',
                cursor: 'pointer',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: settings.anonymous_mode ? '#667eea' : '#cbd5e1',
                transition: '0.3s',
                borderRadius: '28px'
              }}>
                <span style={{
                  position: 'absolute',
                  content: '',
                  height: '20px',
                  width: '20px',
                  left: settings.anonymous_mode ? '26px' : '4px',
                  bottom: '4px',
                  background: 'white',
                  transition: '0.3s',
                  borderRadius: '50%'
                }} />
              </span>
            </label>
          </div>

          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            padding: '16px 0',
            borderBottom: '1px solid #e2e8f0'
          }}>
            <div>
              <div style={{ fontWeight: '500', marginBottom: '4px' }}>数据收集授权</div>
              <div style={{ fontSize: '14px', color: '#64748b' }}>
                允许系统收集和分析数据以优化服务
              </div>
            </div>
            <label style={{ 
              position: 'relative', 
              display: 'inline-block', 
              width: '50px', 
              height: '28px' 
            }}>
              <input
                type="checkbox"
                checked={settings.data_collection_consent}
                onChange={() => handleToggle('data_collection_consent')}
                style={{ opacity: 0, width: 0, height: 0 }}
              />
              <span style={{
                position: 'absolute',
                cursor: 'pointer',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: settings.data_collection_consent ? '#667eea' : '#cbd5e1',
                transition: '0.3s',
                borderRadius: '28px'
              }}>
                <span style={{
                  position: 'absolute',
                  content: '',
                  height: '20px',
                  width: '20px',
                  left: settings.data_collection_consent ? '26px' : '4px',
                  bottom: '4px',
                  background: 'white',
                  transition: '0.3s',
                  borderRadius: '50%'
                }} />
              </span>
            </label>
          </div>

          <div style={{ padding: '16px 0' }}>
            <button 
              onClick={() => setShowPrivacyPolicy(!showPrivacyPolicy)}
              className="btn btn-secondary"
            >
              查看隐私政策
            </button>
          </div>

          {showPrivacyPolicy && (
            <div style={{ 
              background: '#f8fafc', 
              padding: '16px', 
              borderRadius: '8px',
              marginTop: '12px'
            }}>
              <h4 style={{ marginBottom: '12px', color: '#334155' }}>隐私政策</h4>
              <div style={{ fontSize: '14px', color: '#64748b', lineHeight: '1.6' }}>
                <p style={{ marginBottom: '8px' }}>
                  1. 我们收集的数据包括：基本信息、人格测评结果、对话内容、行为数据等
                </p>
                <p style={{ marginBottom: '8px' }}>
                  2. 数据用途：提供匹配服务、优化算法、生成成长报告、心理健康监测
                </p>
                <p style={{ marginBottom: '8px' }}>
                  3. 数据安全：使用HTTPS加密传输、AES-256加密存储
                </p>
                <p style={{ marginBottom: '8px' }}>
                  4. 用户权利：可随时查看、修改、删除个人数据
                </p>
                <p>
                  5. 数据保留：账号删除后24小时内完成数据清除
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Notification Settings */}
        <div className="card">
          <h3 style={{ marginBottom: '20px', color: '#334155' }}>通知设置</h3>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            padding: '16px 0'
          }}>
            <div>
              <div style={{ fontWeight: '500', marginBottom: '4px' }}>启用通知</div>
              <div style={{ fontSize: '14px', color: '#64748b' }}>
                接收新消息、匹配结果、报告生成等通知
              </div>
            </div>
            <label style={{ 
              position: 'relative', 
              display: 'inline-block', 
              width: '50px', 
              height: '28px' 
            }}>
              <input
                type="checkbox"
                checked={settings.notification_enabled}
                onChange={() => handleToggle('notification_enabled')}
                style={{ opacity: 0, width: 0, height: 0 }}
              />
              <span style={{
                position: 'absolute',
                cursor: 'pointer',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: settings.notification_enabled ? '#667eea' : '#cbd5e1',
                transition: '0.3s',
                borderRadius: '28px'
              }}>
                <span style={{
                  position: 'absolute',
                  content: '',
                  height: '20px',
                  width: '20px',
                  left: settings.notification_enabled ? '26px' : '4px',
                  bottom: '4px',
                  background: 'white',
                  transition: '0.3s',
                  borderRadius: '50%'
                }} />
              </span>
            </label>
          </div>
        </div>

        {/* Data Management */}
        <div className="card">
          <h3 style={{ marginBottom: '20px', color: '#334155' }}>数据管理</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <button onClick={handleExportData} className="btn btn-secondary">
              📥 导出我的数据
            </button>
            <button 
              onClick={() => setShowDeleteConfirm(true)}
              className="btn"
              style={{ 
                background: '#fee2e2', 
                color: '#991b1b',
                border: '1px solid #fecaca'
              }}
            >
              🗑️ 删除账号
            </button>
          </div>
        </div>

        {/* About */}
        <div className="card">
          <h3 style={{ marginBottom: '20px', color: '#334155' }}>关于</h3>
          <div style={{ fontSize: '14px', color: '#64748b', lineHeight: '1.8' }}>
            <p style={{ marginBottom: '8px' }}>
              <strong>青春伴行</strong> v1.0.0
            </p>
            <p style={{ marginBottom: '8px' }}>
              基于AI技术的大学生深度社交匹配平台
            </p>
            <p style={{ marginBottom: '8px' }}>
              © 2024 青春伴行团队
            </p>
            <div style={{ marginTop: '16px' }}>
              <a href="#" style={{ color: '#667eea', marginRight: '16px' }}>用户协议</a>
              <a href="#" style={{ color: '#667eea', marginRight: '16px' }}>隐私政策</a>
              <a href="#" style={{ color: '#667eea' }}>联系我们</a>
            </div>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div className="card" style={{ maxWidth: '400px', margin: '20px' }}>
            <h3 style={{ marginBottom: '16px', color: '#991b1b' }}>确认删除账号</h3>
            <p style={{ marginBottom: '24px', color: '#64748b' }}>
              删除账号后，所有数据将在24小时内永久删除，此操作不可恢复。
            </p>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button 
                onClick={() => setShowDeleteConfirm(false)}
                className="btn btn-secondary"
                style={{ flex: 1 }}
              >
                取消
              </button>
              <button 
                onClick={handleDeleteAccount}
                className="btn"
                style={{ 
                  flex: 1,
                  background: '#dc2626', 
                  color: 'white'
                }}
                disabled={loading}
              >
                {loading ? '删除中...' : '确认删除'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SettingsPage
