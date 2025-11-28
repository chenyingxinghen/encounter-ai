import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import AssessmentPage from './pages/AssessmentPage'
import MatchingPage from './pages/MatchingPage'
import ChatPage from './pages/ChatPage'
import ProfilePage from './pages/ProfilePage'
import ReportPage from './pages/ReportPage'
import SettingsPage from './pages/SettingsPage'
import Navigation from './components/Navigation'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [currentUser, setCurrentUser] = useState(null)

  const handleLogin = (user) => {
    setIsAuthenticated(true)
    setCurrentUser(user)
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
    setCurrentUser(null)
  }

  return (
    <Router>
      {isAuthenticated && <Navigation onLogout={handleLogout} user={currentUser} />}
      <Routes>
        <Route 
          path="/login" 
          element={
            isAuthenticated ? <Navigate to="/matching" /> : <LoginPage onLogin={handleLogin} />
          } 
        />
        <Route 
          path="/register" 
          element={
            isAuthenticated ? <Navigate to="/assessment" /> : <RegisterPage onRegister={handleLogin} />
          } 
        />
        <Route 
          path="/assessment" 
          element={
            isAuthenticated ? <AssessmentPage user={currentUser} /> : <Navigate to="/login" />
          } 
        />
        <Route 
          path="/matching" 
          element={
            isAuthenticated ? <MatchingPage user={currentUser} /> : <Navigate to="/login" />
          } 
        />
        <Route 
          path="/chat/:conversationId?" 
          element={
            isAuthenticated ? <ChatPage user={currentUser} /> : <Navigate to="/login" />
          } 
        />
        <Route 
          path="/profile" 
          element={
            isAuthenticated ? <ProfilePage user={currentUser} /> : <Navigate to="/login" />
          } 
        />
        <Route 
          path="/report" 
          element={
            isAuthenticated ? <ReportPage user={currentUser} /> : <Navigate to="/login" />
          } 
        />
        <Route 
          path="/settings" 
          element={
            isAuthenticated ? <SettingsPage user={currentUser} /> : <Navigate to="/login" />
          } 
        />
        <Route path="/" element={<Navigate to={isAuthenticated ? "/matching" : "/login"} />} />
      </Routes>
    </Router>
  )
}

export default App
