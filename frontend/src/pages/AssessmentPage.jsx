import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const MBTI_QUESTIONS = [
  { id: 1, question: '在社交场合中，你更倾向于：', options: ['主动与他人交谈 (E)', '等待他人主动 (I)'] },
  { id: 2, question: '处理问题时，你更依赖：', options: ['实际经验和事实 (S)', '直觉和可能性 (N)'] },
  { id: 3, question: '做决定时，你更看重：', options: ['逻辑和客观分析 (T)', '情感和价值观 (F)'] },
  { id: 4, question: '你的生活方式更倾向于：', options: ['有计划和组织 (J)', '灵活和随性 (P)'] }
]

const BIG_FIVE_QUESTIONS = [
  { id: 1, dimension: 'extraversion', question: '我喜欢参加社交活动' },
  { id: 2, dimension: 'agreeableness', question: '我总是愿意帮助他人' },
  { id: 3, dimension: 'conscientiousness', question: '我做事有条理，注重细节' },
  { id: 4, dimension: 'neuroticism', question: '我经常感到焦虑或担心' },
  { id: 5, dimension: 'openness', question: '我喜欢尝试新事物和新体验' }
]

const INTEREST_TAGS = {
  academic: ['考研', '保研', '学术研究', '竞赛', '英语学习'],
  career: ['求职', '实习', '创业', '职业规划', '技能提升'],
  hobby: ['阅读', '音乐', '运动', '旅行', '摄影', '游戏', '美食']
}

const SCENES = [
  { id: 'study', name: '考研自习室', description: '找到志同道合的考研伙伴' },
  { id: 'career', name: '职业咨询室', description: '探讨职业发展和规划' },
  { id: 'mental', name: '心理树洞', description: '倾诉心声，获得支持' },
  { id: 'interest', name: '兴趣社群', description: '结识有共同爱好的朋友' }
]

function AssessmentPage({ user }) {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [mbtiAnswers, setMbtiAnswers] = useState({})
  const [bigFiveAnswers, setBigFiveAnswers] = useState({})
  const [selectedInterests, setSelectedInterests] = useState([])
  const [selectedScenes, setSelectedScenes] = useState([])
  const [loading, setLoading] = useState(false)

  const handleMbtiAnswer = (questionId, answer) => {
    setMbtiAnswers({ ...mbtiAnswers, [questionId]: answer })
  }

  const handleBigFiveAnswer = (questionId, score) => {
    setBigFiveAnswers({ ...bigFiveAnswers, [questionId]: score })
  }

  const toggleInterest = (interest) => {
    if (selectedInterests.includes(interest)) {
      setSelectedInterests(selectedInterests.filter(i => i !== interest))
    } else {
      setSelectedInterests([...selectedInterests, interest])
    }
  }

  const toggleScene = (sceneId) => {
    if (selectedScenes.includes(sceneId)) {
      setSelectedScenes(selectedScenes.filter(s => s !== sceneId))
    } else {
      setSelectedScenes([...selectedScenes, sceneId])
    }
  }

  const handleSubmit = async () => {
    setLoading(true)
    try {
      await axios.post('/api/users/profile/assessment', {
        user_id: user.user_id,
        mbti_answers: mbtiAnswers,
        big_five_answers: bigFiveAnswers,
        interests: selectedInterests,
        scenes: selectedScenes
      })
      navigate('/matching')
    } catch (err) {
      alert('提交失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container" style={{ paddingTop: '40px', paddingBottom: '40px' }}>
      <div className="card" style={{ maxWidth: '800px', margin: '0 auto' }}>
        <div style={{ marginBottom: '32px' }}>
          <h2 style={{ color: '#334155', marginBottom: '8px' }}>完善个人画像</h2>
          <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
            {[1, 2, 3, 4].map(s => (
              <div 
                key={s}
                style={{ 
                  flex: 1, 
                  height: '4px', 
                  background: s <= step ? '#667eea' : '#e2e8f0',
                  borderRadius: '2px'
                }}
              />
            ))}
          </div>
        </div>

        {step === 1 && (
          <div>
            <h3 style={{ marginBottom: '24px' }}>MBTI人格测试</h3>
            {MBTI_QUESTIONS.map(q => (
              <div key={q.id} style={{ marginBottom: '24px' }}>
                <p style={{ marginBottom: '12px', fontWeight: '500' }}>{q.question}</p>
                <div style={{ display: 'flex', gap: '12px' }}>
                  {q.options.map((option, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleMbtiAnswer(q.id, idx)}
                      className={`btn ${mbtiAnswers[q.id] === idx ? 'btn-primary' : 'btn-secondary'}`}
                      style={{ flex: 1 }}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              </div>
            ))}
            <button 
              onClick={() => setStep(2)} 
              className="btn btn-primary"
              disabled={Object.keys(mbtiAnswers).length < MBTI_QUESTIONS.length}
            >
              下一步
            </button>
          </div>
        )}

        {step === 2 && (
          <div>
            <h3 style={{ marginBottom: '24px' }}>大五人格评估</h3>
            <p style={{ marginBottom: '24px', color: '#64748b' }}>
              请根据自己的实际情况，选择1-5分（1=非常不同意，5=非常同意）
            </p>
            {BIG_FIVE_QUESTIONS.map(q => (
              <div key={q.id} style={{ marginBottom: '24px' }}>
                <p style={{ marginBottom: '12px', fontWeight: '500' }}>{q.question}</p>
                <div style={{ display: 'flex', gap: '8px' }}>
                  {[1, 2, 3, 4, 5].map(score => (
                    <button
                      key={score}
                      onClick={() => handleBigFiveAnswer(q.id, score)}
                      className={`btn ${bigFiveAnswers[q.id] === score ? 'btn-primary' : 'btn-secondary'}`}
                      style={{ flex: 1 }}
                    >
                      {score}
                    </button>
                  ))}
                </div>
              </div>
            ))}
            <div style={{ display: 'flex', gap: '12px' }}>
              <button onClick={() => setStep(1)} className="btn btn-secondary">
                上一步
              </button>
              <button 
                onClick={() => setStep(3)} 
                className="btn btn-primary"
                disabled={Object.keys(bigFiveAnswers).length < BIG_FIVE_QUESTIONS.length}
              >
                下一步
              </button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div>
            <h3 style={{ marginBottom: '24px' }}>选择兴趣标签</h3>
            {Object.entries(INTEREST_TAGS).map(([category, tags]) => (
              <div key={category} style={{ marginBottom: '24px' }}>
                <h4 style={{ marginBottom: '12px', color: '#64748b' }}>
                  {category === 'academic' ? '学业' : category === 'career' ? '职业' : '兴趣爱好'}
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {tags.map(tag => (
                    <button
                      key={tag}
                      onClick={() => toggleInterest(tag)}
                      className={`btn ${selectedInterests.includes(tag) ? 'btn-primary' : 'btn-secondary'}`}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            ))}
            <div style={{ display: 'flex', gap: '12px' }}>
              <button onClick={() => setStep(2)} className="btn btn-secondary">
                上一步
              </button>
              <button 
                onClick={() => setStep(4)} 
                className="btn btn-primary"
                disabled={selectedInterests.length === 0}
              >
                下一步
              </button>
            </div>
          </div>
        )}

        {step === 4 && (
          <div>
            <h3 style={{ marginBottom: '24px' }}>选择关注场景</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
              {SCENES.map(scene => (
                <div
                  key={scene.id}
                  onClick={() => toggleScene(scene.id)}
                  style={{
                    padding: '20px',
                    border: `2px solid ${selectedScenes.includes(scene.id) ? '#667eea' : '#e2e8f0'}`,
                    borderRadius: '12px',
                    cursor: 'pointer',
                    background: selectedScenes.includes(scene.id) ? '#f0f4ff' : 'white'
                  }}
                >
                  <h4 style={{ marginBottom: '8px', color: '#334155' }}>{scene.name}</h4>
                  <p style={{ color: '#64748b', fontSize: '14px' }}>{scene.description}</p>
                </div>
              ))}
            </div>
            <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
              <button onClick={() => setStep(3)} className="btn btn-secondary">
                上一步
              </button>
              <button 
                onClick={handleSubmit} 
                className="btn btn-primary"
                disabled={selectedScenes.length === 0 || loading}
              >
                {loading ? '提交中...' : '完成'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default AssessmentPage
