// 集成高级功能到演示系统

// 初始化高级功能模块
const qualityMonitor = new ConversationQualityMonitor();
const mentalHealthMonitor = new MentalHealthMonitor();
const profileUpdater = new ProfileUpdater();
const contentModerator = new ContentModerator();
const matchingOptimizer = new MatchingOptimizer();
const virtualUserManager = new VirtualUserManager();

// 增强的发送消息功能
const originalSendMessage = window.sendMessage;
window.sendMessage = function() {
    const input = document.getElementById('messageInput');
    const content = input.value.trim();
    
    if (!content || !currentConversation) return;
    
    // 1. 内容审查
    const moderationResult = contentModerator.moderate(content);
    if (!moderationResult.passed) {
        const action = contentModerator.getAction(moderationResult.severity);
        alert(action.message);
        
        if (moderationResult.severity === 'high') {
            // 记录违规
            console.log('违规记录:', {
                user_id: mockData.currentUser.user_id,
                content: content,
                violation_type: moderationResult.violationType,
                keywords: moderationResult.keywords,
                timestamp: new Date()
            });
        }
        
        if (action.action !== 'warn') {
            return; // 拦截消息
        }
    }
    
    // 2. 创建消息
    const message = {
        message_id: `msg-${Date.now()}`,
        sender_id: mockData.currentUser.user_id,
        sender_name: mockData.currentUser.username,
        content: content,
        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
        type: 'text'
    };
    
    // 3. 心理健康监测
    const emotion = mentalHealthMonitor.detectEmotion(message);
    if (emotion.level === 'risk' || emotion.level === 'negative') {
        const advice = mentalHealthMonitor.getHealthAdvice(emotion);
        if (advice) {
            setTimeout(() => showHealthAdvice(advice), 1000);
        }
    }
    
    // 检测持续低落情绪
    if (mentalHealthMonitor.detectPersistentNegativeEmotion()) {
        setTimeout(() => {
            showHealthAdvice({
                level: 'medium',
                message: '我们注意到您最近可能情绪不太好，需要帮助吗？',
                suggestions: [
                    '与朋友或家人聊聊',
                    '尝试一些放松活动',
                    '如需要，可以联系心理咨询服务'
                ],
                resources: []
            });
        }, 2000);
    }
    
    // 4. 添加到消息列表
    if (!mockData.messages[currentConversation.conversation_id]) {
        mockData.messages[currentConversation.conversation_id] = [];
    }
    mockData.messages[currentConversation.conversation_id].push(message);
    
    // 5. 对话质量监测
    const messages = mockData.messages[currentConversation.conversation_id];
    const qualityScore = qualityMonitor.analyzeMessage(message, messages.slice(0, -1));
    
    // 显示质量评分（可选）
    console.log('对话质量评分:', qualityScore);
    
    // 6. 更新用户画像
    const profileUpdates = profileUpdater.extractInfoFromConversation([message]);
    if (profileUpdates.newInterests.length > 0) {
        console.log('发现新兴趣:', profileUpdates.newInterests);
        // 可以在这里更新UI显示新发现的兴趣
    }
    
    // 7. 更新对话最后消息
    currentConversation.last_message = content;
    currentConversation.last_time = '刚刚';
    
    // 8. 清空输入框
    input.value = '';
    
    // 9. 重新加载消息
    loadConversation(currentConversation.conversation_id);
    
    // 10. 清除AI建议
    document.getElementById('aiSuggestionBox').innerHTML = '';
    
    // 11. 重置沉默检测
    messageCount++;
    startSilenceDetection();
    
    // 12. 模拟对方回复
    setTimeout(() => {
        simulateReply();
    }, 2000 + Math.random() * 3000);
};

// 显示心理健康建议
function showHealthAdvice(advice) {
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3 style="color: #334155;">💚 心理健康关怀</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
            </div>
            <div>
                <div class="alert ${advice.level === 'high' ? 'alert-warning' : 'alert-info'}" style="margin-bottom: 16px;">
                    ${advice.message}
                </div>
                
                ${advice.suggestions.length > 0 ? `
                    <h4 style="margin-bottom: 12px; color: #334155;">建议：</h4>
                    <ul style="margin-bottom: 16px; padding-left: 20px;">
                        ${advice.suggestions.map(s => `<li style="margin-bottom: 8px;">${s}</li>`).join('')}
                    </ul>
                ` : ''}
                
                ${advice.resources && advice.resources.length > 0 ? `
                    <h4 style="margin-bottom: 12px; color: #334155;">专业资源：</h4>
                    <div style="margin-bottom: 16px;">
                        ${advice.resources.map(r => `
                            <div style="padding: 12px; background: #f8fafc; border-radius: 8px; margin-bottom: 8px;">
                                <strong>${r.name}</strong><br>
                                <span style="color: #667eea;">📞 ${r.phone}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                <button class="btn btn-primary" onclick="this.closest('.modal').remove()">
                    我知道了
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

// 增强的匹配功能
const originalLoadMatches = window.loadMatches;
window.loadMatches = function() {
    let matches = mockData.matches[currentScene] || [];
    
    // 使用优化的匹配算法重新计算分数（如果用户数据完整）
    if (mockData.currentUser && mockData.currentUser.interests) {
        matches = matches.map(match => {
            // 确保match有完整的数据
            if (match.interests) {
                const score = matchingOptimizer.calculateMatchScore(
                    mockData.currentUser,
                    match,
                    currentScene
                );
                return {
                    ...match,
                    match_score: Math.round(score)
                };
            }
            return match;
        });
    }
    
    // 按分数排序
    matches.sort((a, b) => b.match_score - a.match_score);
    
    // 渲染匹配结果
    const container = document.getElementById('matchResults');
    
    if (matches.length === 0) {
        container.innerHTML = '<div class="card">暂无匹配结果</div>';
        return;
    }
    
    container.innerHTML = matches.map(match => `
        <div class="match-card" onclick="viewMatchDetail('${match.user_id}')">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 16px;">
                <div>
                    <h3 style="color: #334155; margin-bottom: 8px;">
                        ${match.username}
                        ${match.is_virtual ? '<span style="font-size: 12px; color: #94a3b8;">🤖</span>' : ''}
                    </h3>
                    <p style="color: #64748b; font-size: 14px;">${match.school} · ${match.major} · ${match.grade}年级</p>
                </div>
                <div class="score-badge">${match.match_score}分</div>
            </div>
            
            <div style="margin-bottom: 16px;">
                <p style="color: #334155; margin-bottom: 8px;"><strong>匹配理由：</strong></p>
                <p style="color: #64748b; font-size: 14px;">${match.match_reason}</p>
            </div>
            
            <div style="margin-bottom: 16px;">
                <p style="color: #334155; margin-bottom: 8px;"><strong>共同兴趣：</strong></p>
                ${match.common_interests.map(interest => `<span class="tag">${interest}</span>`).join('')}
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-bottom: 16px; font-size: 12px;">
                <div>
                    <div style="color: #64748b;">人格匹配</div>
                    <div style="color: #667eea; font-weight: bold;">${match.personality_score}分</div>
                </div>
                <div>
                    <div style="color: #64748b;">兴趣匹配</div>
                    <div style="color: #667eea; font-weight: bold;">${match.interest_score}分</div>
                </div>
                <div>
                    <div style="color: #64748b;">场景匹配</div>
                    <div style="color: #667eea; font-weight: bold;">${match.scene_score}分</div>
                </div>
                <div>
                    <div style="color: #64748b;">情感同步</div>
                    <div style="color: #667eea; font-weight: bold;">${match.emotion_sync_score}分</div>
                </div>
            </div>
            
            <div style="display: flex; gap: 8px;">
                <button class="btn btn-primary" style="flex: 1;" onclick="event.stopPropagation(); startChat('${match.user_id}')">
                    开始对话
                </button>
                <button class="btn btn-secondary" onclick="event.stopPropagation(); viewProfile('${match.user_id}')">
                    查看画像
                </button>
            </div>
        </div>
    `).join('');
};

// 添加对话质量实时显示
function showConversationQuality() {
    if (!currentConversation) return;
    
    const messages = mockData.messages[currentConversation.conversation_id] || [];
    if (messages.length === 0) return;
    
    const lastMessage = messages[messages.length - 1];
    const qualityScore = qualityMonitor.analyzeMessage(lastMessage, messages.slice(0, -1));
    
    const qualityDisplay = document.createElement('div');
    qualityDisplay.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: white;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        z-index: 100;
        min-width: 200px;
    `;
    qualityDisplay.innerHTML = `
        <h4 style="margin-bottom: 12px; color: #334155;">对话质量</h4>
        <div style="margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-size: 12px; color: #64748b;">话题深度</span>
                <span style="font-size: 12px; font-weight: bold; color: #667eea;">${qualityScore.topicDepth}%</span>
            </div>
            <div class="progress-bar" style="height: 4px;">
                <div class="progress-fill" style="width: ${qualityScore.topicDepth}%"></div>
            </div>
        </div>
        <div style="margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-size: 12px; color: #64748b;">回应一致性</span>
                <span style="font-size: 12px; font-weight: bold; color: #667eea;">${qualityScore.responseConsistency}%</span>
            </div>
            <div class="progress-bar" style="height: 4px;">
                <div class="progress-fill" style="width: ${qualityScore.responseConsistency}%"></div>
            </div>
        </div>
        <div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-size: 12px; color: #64748b;">情感同步</span>
                <span style="font-size: 12px; font-weight: bold; color: #667eea;">${qualityScore.emotionSync}%</span>
            </div>
            <div class="progress-bar" style="height: 4px;">
                <div class="progress-fill" style="width: ${qualityScore.emotionSync}%"></div>
            </div>
        </div>
        <div style="margin-top: 12px; text-align: center;">
            <div style="font-size: 24px; font-weight: bold; color: #667eea;">${qualityScore.overall}分</div>
            <div style="font-size: 12px; color: #64748b;">综合评分</div>
        </div>
        <button class="btn btn-secondary" style="width: 100%; margin-top: 12px; font-size: 12px;" onclick="this.parentElement.remove()">
            关闭
        </button>
    `;
    
    // 移除旧的质量显示
    const oldDisplay = document.querySelector('[data-quality-display]');
    if (oldDisplay) oldDisplay.remove();
    
    qualityDisplay.setAttribute('data-quality-display', 'true');
    document.body.appendChild(qualityDisplay);
    
    // 5秒后自动关闭
    setTimeout(() => qualityDisplay.remove(), 5000);
}

// 添加查看对话质量按钮
document.addEventListener('DOMContentLoaded', () => {
    // 延迟添加按钮，确保页面元素已加载
    setTimeout(() => {
        const chatPage = document.getElementById('chat');
        if (chatPage && !chatPage.querySelector('[data-quality-btn]')) {
            const qualityBtn = document.createElement('button');
            qualityBtn.className = 'btn btn-secondary';
            qualityBtn.textContent = '📊 查看对话质量';
            qualityBtn.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 100;';
            qualityBtn.setAttribute('data-quality-btn', 'true');
            qualityBtn.onclick = showConversationQuality;
            chatPage.appendChild(qualityBtn);
        }
    }, 200);
});

// 添加匹配反馈功能
window.provideFeedback = function(matchId, feedback) {
    matchingOptimizer.collectFeedback(matchId, mockData.currentUser.user_id, feedback);
    alert(`感谢您的反馈！这将帮助我们优化匹配算法。`);
};

// 生成虚拟用户示例
function addVirtualUsers() {
    // 确保mockData存在
    if (typeof mockData === 'undefined') {
        console.warn('mockData未定义，跳过虚拟用户生成');
        return;
    }
    
    const mbtiTypes = ['INFP', 'INTJ', 'ENFP', 'INFJ', 'ENTJ', 'ENTP'];
    const scenes = ['study', 'career', 'mental', 'hobby'];
    
    scenes.forEach(scene => {
        if (!mockData.matches[scene]) {
            mockData.matches[scene] = [];
        }
        
        // 为每个场景添加2个虚拟用户
        for (let i = 0; i < 2; i++) {
            const mbtiType = mbtiTypes[Math.floor(Math.random() * mbtiTypes.length)];
            const virtualUser = virtualUserManager.generateVirtualUser(mbtiType, scene);
            
            // 添加匹配信息
            mockData.matches[scene].push({
                ...virtualUser,
                match_score: 70 + Math.floor(Math.random() * 20),
                personality_score: 70 + Math.floor(Math.random() * 20),
                interest_score: 70 + Math.floor(Math.random() * 20),
                scene_score: 70 + Math.floor(Math.random() * 20),
                emotion_sync_score: 70 + Math.floor(Math.random() * 20),
                match_reason: '系统推荐的优质匹配对象',
                common_interests: ['学习', '交流']
            });
        }
    });
}

// 延迟初始化，确保mockData已加载
setTimeout(() => {
    try {
        // 初始化时添加虚拟用户
        addVirtualUsers();
        
        // 更新虚拟用户权重
        virtualUserManager.updateVirtualUserWeight(50); // 假设有50个真实用户
        
        console.log('✅ 高级功能已集成！');
        console.log('  - 对话质量监测');
        console.log('  - 心理健康监测');
        console.log('  - 用户画像动态更新');
        console.log('  - 内容审查系统');
        console.log('  - 匹配算法优化');
        console.log('  - 虚拟用户管理');
    } catch (error) {
        console.error('高级功能初始化失败:', error);
    }
}, 100);
