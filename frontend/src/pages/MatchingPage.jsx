import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

function MatchingPage({ user }) {
  const navigate = useNavigate()
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedScene, setSelectedScene] = useState('study')
  const [error, setError] = useState('')

  const scenes = [
    { id: 'study', name: '考研自习室', icon: '📚' },
    { id: 'career', name: '职业咨询室', icon: '💼' },
    { id: 'mental', name: '心理树洞', icon: '💭' },
    { id: 'interest', name: '兴趣社群', icon: '🎨' }
  ]

  useEffect(() => {
    fetchMatches()
  }, [selectedScene])

  const fetchMatches = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await axios.get(`/api/matching/find?user_id=${user.user_id}&scene=${selectedScene}&limit=10`)
      setMatches(response.data.matches || [])
    } catch (err) {
      setError('获取匹配结果失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleStartChat = async (matchUserId) => {
    try {
      const response = await axios.post('/api/conversations/create', {
        user_a_id: user.user_id,
        user_b_id: matchUserId,
        scene: selectedScene
      })
      navigate(`/chat/${response.data.conversation_id}`)
    } catch (err) {
      alert('创建对话失败')
    }
  }

  return (
    <div className="container" style={{ paddingTop: '40px' }}>
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ color: '#334155', marginBottom: '16px' }}>发现成长伙伴</h2>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          {scenes.map(scene => (
            <button
              key={scene.id}
              onClick={() => setSelectedScene(scene.id)}
              className={`btn ${selectedScene === scene.id ? 'btn-primary' : 'btn-secondary'}`}
            >
              <span style={{ marginRight: '8px' }}>{scene.icon}</span>
              {scene.name}
            </button>
          ))}
        </div>
      </div>

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

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <p style={{ color: '#64748b' }}>正在为你寻找合适的伙伴...</p>
        </div>
      ) : matches.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <p style={{ color: '#64748b' }}>暂时没有找到合适的匹配对象</p>
          <button onClick={fetchMatches} className="btn btn-primary" style={{ marginTop: '16px' }}>
            重新匹配
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '20px' }}>
          {matches.map(match => (
            <div key={match.match_id} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '16px' }}>
                <div>
                  <h3 style={{ color: '#334155', marginBottom: '4px' }}>
                    {match.user_b_username || '匿名用户'}
                  </h3>
                  <p style={{ color: '#64748b', fontSize: '14px' }}>
                    {match.user_b_school} · {match.user_b_major}
                  </p>
                </div>
                <div style={{ 
                  background: '#f0f4ff', 
                  color: '#667eea', 
                  padding: '8px 16px', 
                  borderRadius: '20px',
                  fontWeight: 'bold'
                }}>
                  {Math.round(match.match_score)}分
                </div>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <p style={{ fontSize: '14px', color: '#334155', marginBottom: '8px' }}>
                  <strong>MBTI:</strong> {match.user_b_mbti || 'N/A'}
                </p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '8px' }}>
                  {(match.user_b_interests || []).slice(0, 5).map((interest, idx) => (
                    <span 
                      key={idx}
                      style={{ 
                        background: '#e2e8f0', 
                        padding: '4px 12px', 
                        borderRadius: '12px',
                        fontSize: '12px',
                        color: '#334155'
                      }}
                    >
                      {interest}
                    </span>
                  ))}
                </div>
              </div>

              <div style={{ 
                background: '#f8fafc', 
                padding: '12px', 
                borderRadius: '8px',
                marginBottom: '16px'
              }}>
                <p style={{ fontSize: '14px', color: '#64748b' }}>
                  💡 {match.match_reason || '你们有很多共同点'}
                </p>
              </div>

              <button 
                onClick={() => handleStartChat(match.user_b_id)}
                className="btn btn-primary"
                style={{ width: '100%' }}
              >
                开始对话
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default MatchingPage
