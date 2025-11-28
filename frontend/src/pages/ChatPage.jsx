import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'

function ChatPage({ user }) {
  const { conversationId } = useParams()
  const navigate = useNavigate()
  const [conversations, setConversations] = useState([])
  const [currentConversation, setCurrentConversation] = useState(null)
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [aiSuggestion, setAiSuggestion] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    fetchConversations()
  }, [])

  useEffect(() => {
    if (conversationId) {
      fetchConversation(conversationId)
      fetchMessages(conversationId)
      const interval = setInterval(() => fetchMessages(conversationId), 3000)
      return () => clearInterval(interval)
    }
  }, [conversationId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const fetchConversations = async () => {
    try {
      const response = await axios.get(`/api/conversations/list?user_id=${user.user_id}`)
      setConversations(response.data.conversations || [])
    } catch (err) {
      console.error('获取对话列表失败', err)
    }
  }

  const fetchConversation = async (convId) => {
    try {
      const response = await axios.get(`/api/conversations/${convId}`)
      setCurrentConversation(response.data)
    } catch (err) {
      console.error('获取对话详情失败', err)
    }
  }

  const fetchMessages = async (convId) => {
    try {
      const response = await axios.get(`/api/conversations/${convId}/messages`)
      setMessages(response.data.messages || [])
      
      // Check for AI suggestions
      if (response.data.ai_suggestion) {
        setAiSuggestion(response.data.ai_suggestion)
      }
    } catch (err) {
      console.error('获取消息失败', err)
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!newMessage.trim() || !conversationId) return

    setLoading(true)
    try {
      await axios.post('/api/conversations/message', {
        conversation_id: conversationId,
        sender_id: user.user_id,
        content: newMessage
      })
      setNewMessage('')
      setAiSuggestion(null)
      await fetchMessages(conversationId)
    } catch (err) {
      alert('发送消息失败')
    } finally {
      setLoading(false)
    }
  }

  const handleUseSuggestion = () => {
    if (aiSuggestion) {
      setNewMessage(aiSuggestion.content)
      setAiSuggestion(null)
    }
  }

  const getOtherUserName = () => {
    if (!currentConversation) return '对话'
    return currentConversation.user_a_id === user.user_id 
      ? currentConversation.user_b_username 
      : currentConversation.user_a_username
  }

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 64px)' }}>
      {/* Conversation List */}
      <div style={{ 
        width: '300px', 
        background: 'white', 
        borderRight: '1px solid #e2e8f0',
        overflowY: 'auto'
      }}>
        <div style={{ padding: '20px', borderBottom: '1px solid #e2e8f0' }}>
          <h3 style={{ color: '#334155' }}>对话列表</h3>
        </div>
        {conversations.map(conv => (
          <div
            key={conv.conversation_id}
            onClick={() => navigate(`/chat/${conv.conversation_id}`)}
            style={{
              padding: '16px 20px',
              borderBottom: '1px solid #e2e8f0',
              cursor: 'pointer',
              background: conv.conversation_id === conversationId ? '#f0f4ff' : 'white'
            }}
          >
            <div style={{ fontWeight: '500', color: '#334155', marginBottom: '4px' }}>
              {conv.user_a_id === user.user_id ? conv.user_b_username : conv.user_a_username}
            </div>
            <div style={{ fontSize: '14px', color: '#64748b' }}>
              {conv.scene === 'study' ? '📚 考研自习室' : 
               conv.scene === 'career' ? '💼 职业咨询室' :
               conv.scene === 'mental' ? '💭 心理树洞' : '🎨 兴趣社群'}
            </div>
          </div>
        ))}
        {conversations.length === 0 && (
          <div style={{ padding: '40px 20px', textAlign: 'center', color: '#64748b' }}>
            暂无对话
          </div>
        )}
      </div>

      {/* Chat Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: '#f8fafc' }}>
        {conversationId ? (
          <>
            {/* Chat Header */}
            <div style={{ 
              background: 'white', 
              padding: '20px', 
              borderBottom: '1px solid #e2e8f0',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <h3 style={{ color: '#334155' }}>{getOtherUserName()}</h3>
              {currentConversation && (
                <span style={{ 
                  background: '#f0f4ff', 
                  color: '#667eea', 
                  padding: '6px 12px', 
                  borderRadius: '12px',
                  fontSize: '14px'
                }}>
                  {currentConversation.scene === 'study' ? '📚 考研自习室' : 
                   currentConversation.scene === 'career' ? '💼 职业咨询室' :
                   currentConversation.scene === 'mental' ? '💭 心理树洞' : '🎨 兴趣社群'}
                </span>
              )}
            </div>

            {/* Messages */}
            <div style={{ 
              flex: 1, 
              overflowY: 'auto', 
              padding: '20px',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px'
            }}>
              {messages.map(msg => (
                <div
                  key={msg.message_id}
                  style={{
                    display: 'flex',
                    justifyContent: msg.sender_id === user.user_id ? 'flex-end' : 'flex-start'
                  }}
                >
                  <div style={{
                    maxWidth: '60%',
                    padding: '12px 16px',
                    borderRadius: '12px',
                    background: msg.sender_id === user.user_id ? '#667eea' : 'white',
                    color: msg.sender_id === user.user_id ? 'white' : '#334155',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                  }}>
                    <p style={{ margin: 0 }}>{msg.content}</p>
                    <div style={{ 
                      fontSize: '12px', 
                      marginTop: '4px',
                      opacity: 0.7
                    }}>
                      {new Date(msg.timestamp).toLocaleTimeString('zh-CN', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* AI Suggestion */}
            {aiSuggestion && (
              <div style={{ 
                background: '#fffbeb', 
                padding: '12px 20px',
                borderTop: '1px solid #fef3c7',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '12px', color: '#92400e', marginBottom: '4px' }}>
                    💡 AI助手建议
                  </div>
                  <div style={{ color: '#78350f' }}>{aiSuggestion.content}</div>
                </div>
                <button 
                  onClick={handleUseSuggestion}
                  className="btn btn-secondary"
                  style={{ marginLeft: '12px' }}
                >
                  使用
                </button>
              </div>
            )}

            {/* Message Input */}
            <form onSubmit={handleSendMessage} style={{ 
              background: 'white', 
              padding: '20px',
              borderTop: '1px solid #e2e8f0'
            }}>
              <div style={{ display: 'flex', gap: '12px' }}>
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="输入消息..."
                  className="input"
                  style={{ flex: 1, marginBottom: 0 }}
                />
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={loading || !newMessage.trim()}
                >
                  发送
                </button>
              </div>
            </form>
          </>
        ) : (
          <div style={{ 
            flex: 1, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            color: '#64748b'
          }}>
            <div style={{ textAlign: 'center' }}>
              <p style={{ fontSize: '18px', marginBottom: '8px' }}>选择一个对话开始聊天</p>
              <p>或者去匹配页面寻找新的伙伴</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatPage
