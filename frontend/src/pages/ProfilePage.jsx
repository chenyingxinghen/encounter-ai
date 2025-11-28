import React, { useState, useEffect } from 'react'
import axios from 'axios'

function ProfilePage({ user }) {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [editData, setEditData] = useState({})

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`/api/users/profile/${user.user_id}`)
      setProfile(response.data)
      setEditData({
        school: response.data.school,
        major: response.data.major,
        grade: response.data.grade
      })
    } catch (err) {
      console.error('获取用户画像失败', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      await axios.put(`/api/users/profile/${user.user_id}`, editData)
      await fetchProfile()
      setEditing(false)
      alert('保存成功')
    } catch (err) {
      alert('保存失败')
    }
  }

  if (loading) {
    return (
      <div className="container" style={{ paddingTop: '40px', textAlign: 'center' }}>
        <p style={{ color: '#64748b' }}>加载中...</p>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="container" style={{ paddingTop: '40px', textAlign: 'center' }}>
        <p style={{ color: '#64748b' }}>无法加载用户画像</p>
      </div>
    )
  }

  return (
    <div className="container" style={{ paddingTop: '40px', paddingBottom: '40px' }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
          <h2 style={{ color: '#334155' }}>个人中心</h2>
          {!editing ? (
            <button onClick={() => setEditing(true)} className="btn btn-secondary">
              编辑资料
            </button>
          ) : (
            <div style={{ display: 'flex', gap: '12px' }}>
              <button onClick={() => setEditing(false)} className="btn btn-secondary">
                取消
              </button>
              <button onClick={handleSave} className="btn btn-primary">
                保存
              </button>
            </div>
          )}
        </div>

        {/* Basic Info */}
        <div className="card">
          <h3 style={{ marginBottom: '20px', color: '#334155' }}>基本信息</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
            <div>
              <label className="label">用户名</label>
              <input 
                type="text" 
                className="input" 
                value={profile.username} 
                disabled 
                style={{ background: '#f8fafc' }}
              />
            </div>
            <div>
              <label className="label">邮箱</label>
              <input 
                type="email" 
                className="input" 
                value={profile.email} 
                disabled 
                style={{ background: '#f8fafc' }}
              />
            </div>
            <div>
              <label className="label">学校</label>
              <input 
                type="text" 
                className="input" 
                value={editing ? editData.school : profile.school}
                onChange={(e) => setEditData({...editData, school: e.target.value})}
                disabled={!editing}
                style={{ background: editing ? 'white' : '#f8fafc' }}
              />
            </div>
            <div>
              <label className="label">专业</label>
              <input 
                type="text" 
                className="input" 
                value={editing ? editData.major : profile.major}
                onChange={(e) => setEditData({...editData, major: e.target.value})}
                disabled={!editing}
                style={{ background: editing ? 'white' : '#f8fafc' }}
              />
            </div>
            <div>
              <label className="label">年级</label>
              <select 
                className="input" 
                value={editing ? editData.grade : profile.grade}
                onChange={(e) => setEditData({...editData, grade: e.target.value})}
                disabled={!editing}
                style={{ background: editing ? 'white' : '#f8fafc' }}
              >
                <option value="1">大一</option>
                <option value="2">大二</option>
                <option value="3">大三</option>
                <option value="4">大四</option>
                <option value="5">研一</option>
                <option value="6">研二</option>
                <option value="7">研三</option>
              </select>
            </div>
          </div>
        </div>

        {/* Personality */}
        <div className="card">
          <h3 style={{ marginBottom: '20px', color: '#334155' }}>人格特质</h3>
          <div style={{ marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontWeight: '500' }}>MBTI类型</span>
              <span style={{ 
                background: '#f0f4ff', 
                color: '#667eea', 
                padding: '4px 16px', 
                borderRadius: '12px',
                fontWeight: 'bold'
              }}>
                {profile.mbti_type || 'N/A'}
              </span>
            </div>
          </div>
          
          {profile.big_five && (
            <div>
              <h4 style={{ marginBottom: '16px', color: '#64748b', fontSize: '14px' }}>大五人格得分</h4>
              {[
                { key: 'extraversion', label: '外向性', color: '#667eea' },
                { key: 'agreeableness', label: '宜人性', color: '#10b981' },
                { key: 'conscientiousness', label: '尽责性', color: '#f59e0b' },
                { key: 'neuroticism', label: '神经质', color: '#ef4444' },
                { key: 'openness', label: '开放性', color: '#8b5cf6' }
              ].map(trait => (
                <div key={trait.key} style={{ marginBottom: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ fontSize: '14px' }}>{trait.label}</span>
                    <span style={{ fontSize: '14px', fontWeight: '500' }}>
                      {Math.round((profile.big_five[trait.key] || 0) * 100)}%
                    </span>
                  </div>
                  <div style={{ 
                    height: '8px', 
                    background: '#e2e8f0', 
                    borderRadius: '4px',
                    overflow: 'hidden'
                  }}>
                    <div style={{ 
                      height: '100%', 
                      background: trait.color,
                      width: `${(profile.big_five[trait.key] || 0) * 100}%`,
                      transition: 'width 0.3s'
                    }} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Interests */}
        <div className="card">
          <h3 style={{ marginBottom: '20px', color: '#334155' }}>兴趣标签</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {(profile.interests || []).map((interest, idx) => (
              <span 
                key={idx}
                style={{ 
                  background: '#f0f4ff', 
                  color: '#667eea', 
                  padding: '8px 16px', 
                  borderRadius: '20px',
                  fontSize: '14px'
                }}
              >
                {interest}
              </span>
            ))}
            {(!profile.interests || profile.interests.length === 0) && (
              <p style={{ color: '#64748b' }}>暂无兴趣标签</p>
            )}
          </div>
        </div>

        {/* Scenes */}
        <div className="card">
          <h3 style={{ marginBottom: '20px', color: '#334155' }}>关注场景</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
            {(profile.current_scenes || []).map((scene, idx) => (
              <div 
                key={idx}
                style={{ 
                  padding: '16px', 
                  background: '#f8fafc', 
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0'
                }}
              >
                <span style={{ fontSize: '24px', marginRight: '8px' }}>
                  {scene === 'study' ? '📚' : 
                   scene === 'career' ? '💼' :
                   scene === 'mental' ? '💭' : '🎨'}
                </span>
                <span style={{ fontWeight: '500', color: '#334155' }}>
                  {scene === 'study' ? '考研自习室' : 
                   scene === 'career' ? '职业咨询室' :
                   scene === 'mental' ? '心理树洞' : '兴趣社群'}
                </span>
              </div>
            ))}
            {(!profile.current_scenes || profile.current_scenes.length === 0) && (
              <p style={{ color: '#64748b', gridColumn: '1 / -1' }}>暂无关注场景</p>
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="card">
          <h3 style={{ marginBottom: '20px', color: '#334155' }}>社交统计</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#667eea', marginBottom: '4px' }}>
                {profile.total_conversations || 0}
              </div>
              <div style={{ color: '#64748b', fontSize: '14px' }}>对话总数</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#10b981', marginBottom: '4px' }}>
                {profile.total_matches || 0}
              </div>
              <div style={{ color: '#64748b', fontSize: '14px' }}>匹配次数</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#f59e0b', marginBottom: '4px' }}>
                {Math.round((profile.average_quality || 0) * 10) / 10}
              </div>
              <div style={{ color: '#64748b', fontSize: '14px' }}>平均对话质量</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProfilePage
