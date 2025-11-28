import React, { useState, useEffect } from 'react'
import axios from 'axios'

function ReportPage({ user }) {
  const [reportType, setReportType] = useState('weekly')
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchReport()
  }, [reportType])

  const fetchReport = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await axios.get(`/api/reports/${reportType}?user_id=${user.user_id}`)
      setReport(response.data)
    } catch (err) {
      if (err.response?.status === 404) {
        setError('暂无报告数据')
      } else {
        setError('获取报告失败')
      }
      setReport(null)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    try {
      const response = await axios.get(
        `/api/reports/${reportType}/download?user_id=${user.user_id}`,
        { responseType: 'blob' }
      )
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `成长报告_${reportType}_${new Date().toISOString().split('T')[0]}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      alert('下载失败')
    }
  }

  const reportTypes = [
    { id: 'weekly', name: '周报', icon: '📅' },
    { id: 'monthly', name: '月报', icon: '📊' },
    { id: 'annual', name: '年报', icon: '🎯' }
  ]

  return (
    <div className="container" style={{ paddingTop: '40px', paddingBottom: '40px' }}>
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        <div style={{ marginBottom: '32px' }}>
          <h2 style={{ color: '#334155', marginBottom: '16px' }}>成长报告</h2>
          <div style={{ display: 'flex', gap: '12px' }}>
            {reportTypes.map(type => (
              <button
                key={type.id}
                onClick={() => setReportType(type.id)}
                className={`btn ${reportType === type.id ? 'btn-primary' : 'btn-secondary'}`}
              >
                <span style={{ marginRight: '8px' }}>{type.icon}</span>
                {type.name}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
            <p style={{ color: '#64748b' }}>加载中...</p>
          </div>
        ) : error ? (
          <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
            <p style={{ color: '#64748b' }}>{error}</p>
            <p style={{ color: '#94a3b8', fontSize: '14px', marginTop: '8px' }}>
              {reportType === 'weekly' && '使用平台满1周后可查看周报'}
              {reportType === 'monthly' && '使用平台满1个月后可查看月报'}
              {reportType === 'annual' && '使用平台满1年后可查看年报'}
            </p>
          </div>
        ) : report ? (
          <>
            {/* Report Header */}
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '20px' }}>
                <div>
                  <h3 style={{ color: '#334155', marginBottom: '8px' }}>
                    {reportType === 'weekly' ? '本周成长报告' : 
                     reportType === 'monthly' ? '本月成长报告' : '年度成长报告'}
                  </h3>
                  <p style={{ color: '#64748b', fontSize: '14px' }}>
                    统计周期: {new Date(report.period_start).toLocaleDateString()} - {new Date(report.period_end).toLocaleDateString()}
                  </p>
                </div>
                <button onClick={handleDownload} className="btn btn-secondary">
                  📥 下载报告
                </button>
              </div>
            </div>

            {/* Key Metrics */}
            <div className="card">
              <h3 style={{ marginBottom: '20px', color: '#334155' }}>核心数据</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#667eea', marginBottom: '8px' }}>
                    {report.total_conversations || 0}
                  </div>
                  <div style={{ color: '#64748b', fontSize: '14px' }}>对话总数</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#10b981', marginBottom: '8px' }}>
                    {report.total_messages || 0}
                  </div>
                  <div style={{ color: '#64748b', fontSize: '14px' }}>消息总数</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#f59e0b', marginBottom: '8px' }}>
                    {Math.round((report.average_conversation_quality || 0) * 10) / 10}
                  </div>
                  <div style={{ color: '#64748b', fontSize: '14px' }}>平均对话质量</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#8b5cf6', marginBottom: '8px' }}>
                    {Math.round((report.social_skill_score || 0) * 10) / 10}
                  </div>
                  <div style={{ color: '#64748b', fontSize: '14px' }}>社交能力</div>
                </div>
              </div>
            </div>

            {/* Emotion Health */}
            <div className="card">
              <h3 style={{ marginBottom: '20px', color: '#334155' }}>情绪健康</h3>
              <div style={{ marginBottom: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontWeight: '500' }}>情绪健康得分</span>
                  <span style={{ fontWeight: 'bold', color: '#10b981' }}>
                    {Math.round((report.emotion_health_score || 0) * 100)}%
                  </span>
                </div>
                <div style={{ 
                  height: '12px', 
                  background: '#e2e8f0', 
                  borderRadius: '6px',
                  overflow: 'hidden'
                }}>
                  <div style={{ 
                    height: '100%', 
                    background: 'linear-gradient(90deg, #10b981 0%, #34d399 100%)',
                    width: `${(report.emotion_health_score || 0) * 100}%`,
                    transition: 'width 0.3s'
                  }} />
                </div>
              </div>
              {report.emotion_trend && (
                <div style={{ 
                  background: '#f0fdf4', 
                  padding: '12px', 
                  borderRadius: '8px',
                  border: '1px solid #bbf7d0'
                }}>
                  <p style={{ color: '#166534', fontSize: '14px' }}>
                    📈 {report.emotion_trend}
                  </p>
                </div>
              )}
            </div>

            {/* Highlights */}
            {report.highlights && report.highlights.length > 0 && (
              <div className="card">
                <h3 style={{ marginBottom: '20px', color: '#334155' }}>成长亮点</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {report.highlights.map((highlight, idx) => (
                    <div 
                      key={idx}
                      style={{ 
                        padding: '16px', 
                        background: '#fef3c7', 
                        borderRadius: '8px',
                        borderLeft: '4px solid #f59e0b'
                      }}
                    >
                      <p style={{ color: '#78350f', margin: 0 }}>
                        ⭐ {highlight}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Suggestions */}
            {report.suggestions && report.suggestions.length > 0 && (
              <div className="card">
                <h3 style={{ marginBottom: '20px', color: '#334155' }}>改进建议</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {report.suggestions.map((suggestion, idx) => (
                    <div 
                      key={idx}
                      style={{ 
                        padding: '16px', 
                        background: '#dbeafe', 
                        borderRadius: '8px',
                        borderLeft: '4px solid #3b82f6'
                      }}
                    >
                      <p style={{ color: '#1e3a8a', margin: 0 }}>
                        💡 {suggestion}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Visualization */}
            {report.visualization_data && (
              <div className="card">
                <h3 style={{ marginBottom: '20px', color: '#334155' }}>数据可视化</h3>
                <div style={{ 
                  background: '#f8fafc', 
                  padding: '40px', 
                  borderRadius: '8px',
                  textAlign: 'center'
                }}>
                  <p style={{ color: '#64748b' }}>
                    📊 图表数据已准备就绪
                  </p>
                  <p style={{ color: '#94a3b8', fontSize: '14px', marginTop: '8px' }}>
                    包含社交能力曲线、情绪健康趋势等可视化内容
                  </p>
                </div>
              </div>
            )}

            {/* Share */}
            <div className="card" style={{ textAlign: 'center' }}>
              <h3 style={{ marginBottom: '16px', color: '#334155' }}>分享你的成长</h3>
              <p style={{ color: '#64748b', marginBottom: '20px' }}>
                将你的成长报告分享给朋友，一起见证进步
              </p>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                <button className="btn btn-secondary">
                  分享到微信
                </button>
                <button className="btn btn-secondary">
                  分享到朋友圈
                </button>
                <button className="btn btn-secondary">
                  复制链接
                </button>
              </div>
            </div>
          </>
        ) : null}
      </div>
    </div>
  )
}

export default ReportPage
