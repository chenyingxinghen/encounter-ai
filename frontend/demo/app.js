// 模拟数据
const mockData = {
    currentUser: {
        user_id: 'user-001',
        username: '张三',
        email: 'zhangsan@example.com',
        school: '清华大学',
        major: '计算机科学',
        grade: 3,
        mbti_type: 'INFP',
        big_five: {
            neuroticism: 0.45,
            agreeableness: 0.78,
            extraversion: 0.52,
            openness: 0.85,
            conscientiousness: 0.72
        },
        interests: {
            academic: ['考研', '算法', '人工智能'],
            career: ['软件工程师', '产品经理'],
            hobby: ['阅读', '音乐', '摄影']
        }
    },
    
    matches: {
        study: [
            {
                user_id: 'user-002',
                username: '李四',
                school: '清华大学',
                major: '计算机科学',
                grade: 3,
                mbti_type: 'INTJ',
                match_score: 92,
                personality_score: 88,
                interest_score: 95,
                scene_score: 93,
                emotion_sync_score: 90,
                match_reason: '你们都在准备考研，目标院校相同，学习习惯相似',
                common_interests: ['考研', '算法', '阅读']
            },
            {
                user_id: 'user-003',
                username: '王五',
                school: '北京大学',
                major: '数学',
                grade: 3,
                mbti_type: 'INFJ',
                match_score: 85,
                personality_score: 90,
                interest_score: 82,
                scene_score: 85,
                emotion_sync_score: 83,
                match_reason: '性格互补，都喜欢深度思考，可以互相激励',
                common_interests: ['考研', '阅读']
            },
            {
                user_id: 'user-004',
                username: '赵六',
                school: '清华大学',
                major: '软件工程',
                grade: 2,
                mbti_type: 'ENFP',
                match_score: 78,
                personality_score: 75,
                interest_score: 80,
                scene_score: 78,
                emotion_sync_score: 79,
                match_reason: '学习目标一致，可以分享学习资源和经验',
                common_interests: ['算法', '人工智能']
            }
        ],
        career: [
            {
                user_id: 'user-005',
                username: '孙七',
                school: '清华大学',
                major: '计算机科学',
                grade: 4,
                mbti_type: 'ENTJ',
                match_score: 88,
                personality_score: 85,
                interest_score: 90,
                scene_score: 89,
                emotion_sync_score: 87,
                match_reason: '职业规划相似，有丰富的实习经验可以分享',
                common_interests: ['软件工程师', '产品经理']
            }
        ],
        mental: [
            {
                user_id: 'user-006',
                username: '周八',
                school: '北京大学',
                major: '心理学',
                grade: 3,
                mbti_type: 'INFP',
                match_score: 90,
                personality_score: 95,
                interest_score: 85,
                scene_score: 90,
                emotion_sync_score: 92,
                match_reason: '情感共鸣强，善于倾听和理解，可以互相支持',
                common_interests: ['阅读', '音乐']
            }
        ],
        hobby: [
            {
                user_id: 'user-007',
                username: '吴九',
                school: '清华大学',
                major: '艺术设计',
                grade: 2,
                mbti_type: 'ISFP',
                match_score: 82,
                personality_score: 80,
                interest_score: 85,
                scene_score: 82,
                emotion_sync_score: 81,
                match_reason: '兴趣爱好高度重合，可以一起探索新的爱好',
                common_interests: ['音乐', '摄影', '阅读']
            }
        ]
    },
    
    conversations: [
        {
            conversation_id: 'conv-001',
            partner_id: 'user-002',
            partner_name: '李四',
            scene: 'study',
            scene_name: '考研自习室',
            last_message: '今天的学习进度怎么样？',
            last_time: '10分钟前',
            unread: 2
        },
        {
            conversation_id: 'conv-002',
            partner_id: 'user-006',
            partner_name: '周八',
            scene: 'mental',
            scene_name: '心理树洞',
            last_message: '最近感觉压力有点大',
            last_time: '1小时前',
            unread: 0
        },
        {
            conversation_id: 'conv-003',
            partner_id: 'user-005',
            partner_name: '孙七',
            scene: 'career',
            scene_name: '职业咨询室',
            last_message: '我可以分享一些面试经验',
            last_time: '昨天',
            unread: 1
        }
    ],
    
    messages: {
        'conv-001': [
            {
                message_id: 'msg-001',
                sender_id: 'user-002',
                sender_name: '李四',
                content: '你好！很高兴认识你',
                timestamp: '2024-01-15 09:00:00',
                type: 'text'
            },
            {
                message_id: 'msg-002',
                sender_id: 'user-001',
                sender_name: '张三',
                content: '你好！我也很高兴认识你',
                timestamp: '2024-01-15 09:01:00',
                type: 'text'
            },
            {
                message_id: 'msg-003',
                sender_id: 'user-002',
                sender_name: '李四',
                content: '看到你也在准备考研，目标院校是哪里？',
                timestamp: '2024-01-15 09:02:00',
                type: 'text'
            },
            {
                message_id: 'msg-004',
                sender_id: 'user-001',
                sender_name: '张三',
                content: '我准备考清华的计算机专业，你呢？',
                timestamp: '2024-01-15 09:03:00',
                type: 'text'
            },
            {
                message_id: 'msg-005',
                sender_id: 'user-002',
                sender_name: '李四',
                content: '我也是！我们可以一起学习，互相监督',
                timestamp: '2024-01-15 09:04:00',
                type: 'text'
            },
            {
                message_id: 'msg-006',
                sender_id: 'user-001',
                sender_name: '张三',
                content: '太好了！那我们可以分享一下学习资料',
                timestamp: '2024-01-15 09:05:00',
                type: 'text'
            },
            {
                message_id: 'msg-007',
                sender_id: 'user-002',
                sender_name: '李四',
                content: '今天的学习进度怎么样？',
                timestamp: '2024-01-15 14:50:00',
                type: 'text'
            }
        ],
        'conv-002': [
            {
                message_id: 'msg-101',
                sender_id: 'user-006',
                sender_name: '周八',
                content: '你好，看到你也喜欢阅读和音乐',
                timestamp: '2024-01-15 10:00:00',
                type: 'text'
            },
            {
                message_id: 'msg-102',
                sender_id: 'user-001',
                sender_name: '张三',
                content: '是的，这些都是我放松的方式',
                timestamp: '2024-01-15 10:05:00',
                type: 'text'
            },
            {
                message_id: 'msg-103',
                sender_id: 'user-006',
                sender_name: '周八',
                content: '最近感觉压力有点大',
                timestamp: '2024-01-15 13:00:00',
                type: 'text'
            }
        ],
        'conv-003': [
            {
                message_id: 'msg-201',
                sender_id: 'user-005',
                sender_name: '孙七',
                content: '你好！看到你对软件工程师这个职业感兴趣',
                timestamp: '2024-01-14 15:00:00',
                type: 'text'
            },
            {
                message_id: 'msg-202',
                sender_id: 'user-001',
                sender_name: '张三',
                content: '是的，我想了解一下这个行业的情况',
                timestamp: '2024-01-14 15:10:00',
                type: 'text'
            },
            {
                message_id: 'msg-203',
                sender_id: 'user-005',
                sender_name: '孙七',
                content: '我可以分享一些面试经验',
                timestamp: '2024-01-14 15:15:00',
                type: 'text'
            }
        ]
    },
    
    aiAssistantMessages: {
        study: [
            '哈哈我刚才也在刷题，做到一道超难的算法题，差点把我整崩溃了😂 你们最近有遇到什么难题吗？',
            '诶对了，我昨天熬夜到凌晨两点才把那个知识点搞懂，现在想想真是太拼了...你们一般学到几点啊？',
            '说起来，我最近发现图书馆三楼那个角落特别安静，适合学习！就是人有点多，得早点去占座😅',
            '突然想到个问题，你们觉得是早上学习效率高还是晚上？我是典型的夜猫子，越晚越清醒哈哈',
            '刚才看到食堂新出了个套餐，看起来还不错！要不要一起去试试？学累了也得好好吃饭嘛～'
        ],
        career: [
            '我最近在纠结要不要转行做产品经理，感觉技术岗压力好大...你们有这种想法吗？',
            '昨天面试被问到一个超奇葩的问题，当场就懵了😂 你们面试遇到过什么离谱的事吗？',
            '诶，我有个学长去年进了字节，听说工作强度真的很大，但成长也快。你们怎么看大厂996这个事？',
            '说实话，我现在对未来还挺迷茫的，不知道该选稳定还是选挑战...你们有明确的职业目标吗？',
            '刚看到个招聘信息，薪资还挺诱人的，但要求三年经验。我们这种应届生真的太难了😭'
        ],
        mental: [
            '最近压力确实挺大的，我昨晚失眠到三点才睡着...你们会不会也这样？',
            '说起来，我上周末一个人去爬山了，感觉心情好了很多！你们平时怎么解压的？',
            '有时候真的很想找个人好好聊聊天，但又不知道该说什么...你们懂这种感觉吗？',
            '我发现最近情绪波动有点大，可能是季节变化的原因？你们会不会也有这种情况？',
            '诶，要不我们组个局出去玩玩？感觉大家都需要放松一下，老憋着也不是办法～'
        ],
        hobby: [
            '我周末刚去看了那部新上映的电影，超级好看！你们看了吗？可以一起讨论剧情哈哈',
            '最近迷上了摄影，但拍出来的照片总感觉差点意思...你们有什么拍照技巧吗？',
            '诶对了，我发现学校附近新开了家咖啡店，环境超棒！有空一起去打卡吗？',
            '说起来，我最近在学吉他，但手指按弦好痛啊😭 你们有玩乐器的吗？求指导！',
            '周末想组个局打羽毛球或者桌游，你们有兴趣吗？人多才热闹嘛～'
        ]
    }
};

// 全局状态
let currentScene = 'study';
let currentConversation = null;
let silenceTimer = null;
let messageCount = 0;

// 页面切换
function showPage(pageName) {
    // 隐藏所有页面
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // 显示目标页面
    document.getElementById(pageName).classList.add('active');
    
    // 更新导航按钮状态
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // 加载页面数据
    if (pageName === 'matching') {
        loadMatches();
    } else if (pageName === 'chat') {
        loadConversations();
    }
}

// 场景选择
function selectScene(scene) {
    currentScene = scene;
    
    // 更新场景按钮状态
    document.querySelectorAll('.scene-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.closest('.scene-btn').classList.add('active');
    
    // 更新场景提示
    const sceneNames = {
        study: '考研自习室',
        career: '职业咨询室',
        mental: '心理树洞',
        hobby: '兴趣社群'
    };
    const sceneDescriptions = {
        study: '为你推荐志同道合的学习伙伴',
        career: '连接有经验的职场前辈',
        mental: '找到能够倾听和理解你的朋友',
        hobby: '发现兴趣相投的伙伴'
    };
    
    safeSetText('currentScene', sceneNames[scene]);
    const alertInfo = document.querySelector('.alert-info');
    if (alertInfo) {
        alertInfo.innerHTML = `💡 当前场景：<strong>${sceneNames[scene]}</strong> - ${sceneDescriptions[scene]}`;
    }
    
    // 重新加载匹配结果
    loadMatches();
}

// 加载匹配结果
function loadMatches() {
    const matches = mockData.matches[currentScene] || [];
    const container = document.getElementById('matchResults');
    
    // 更新匹配数量
    safeSetText('matchCount', matches.length);
    
    // 显示AI分析动画
    showAIAnalysisAnimation();
    
    if (matches.length === 0) {
        container.innerHTML = '<div class="card">暂无匹配结果</div>';
        return;
    }
    
    // 添加加载动画
    container.innerHTML = '<div style="text-align: center; padding: 40px; color: #5288c1;">🤖 AI正在分析匹配结果...</div>';
    
    // 模拟AI分析延迟
    setTimeout(() => {
        container.innerHTML = matches.map(match => `
        <div class="match-card" onclick="viewMatchDetail('${match.user_id}')">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 16px;">
                <div>
                    <h3 style="color: #c5d1de; margin-bottom: 8px; font-weight: 600;">${match.username}</h3>
                    <p style="color: #8b98a5; font-size: 14px;">${match.school} · ${match.major} · ${match.grade}年级</p>
                </div>
                <div class="score-badge">${match.match_score}分</div>
            </div>
            
            <div style="margin-bottom: 16px;">
                <p style="color: #c5d1de; margin-bottom: 8px;">
                    <strong>🤖 AI匹配理由：</strong>
                </p>
                <p style="color: #8b98a5; font-size: 14px; background: rgba(82, 136, 193, 0.1); padding: 10px; border-radius: 8px; border-left: 3px solid #5288c1;">
                    ${match.match_reason}
                </p>
            </div>
            
            <div style="margin-bottom: 16px;">
                <p style="color: #c5d1de; margin-bottom: 8px;"><strong>共同兴趣：</strong></p>
                ${match.common_interests.map(interest => `<span class="tag">${interest}</span>`).join('')}
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 16px; font-size: 12px;">
                <div style="background: rgba(255, 255, 255, 0.03); padding: 8px; border-radius: 8px;">
                    <div style="color: #8b98a5;">人格匹配</div>
                    <div style="color: #5288c1; font-weight: 600; font-size: 16px; margin-top: 4px;">${match.personality_score}分</div>
                </div>
                <div style="background: rgba(255, 255, 255, 0.03); padding: 8px; border-radius: 8px;">
                    <div style="color: #8b98a5;">兴趣匹配</div>
                    <div style="color: #5288c1; font-weight: 600; font-size: 16px; margin-top: 4px;">${match.interest_score}分</div>
                </div>
                <div style="background: rgba(255, 255, 255, 0.03); padding: 8px; border-radius: 8px;">
                    <div style="color: #8b98a5;">场景匹配</div>
                    <div style="color: #5288c1; font-weight: 600; font-size: 16px; margin-top: 4px;">${match.scene_score}分</div>
                </div>
                <div style="background: rgba(255, 255, 255, 0.03); padding: 8px; border-radius: 8px;">
                    <div style="color: #8b98a5;">情感同步</div>
                    <div style="color: #5288c1; font-weight: 600; font-size: 16px; margin-top: 4px;">${match.emotion_sync_score}分</div>
                </div>
            </div>
            
            <div style="display: flex; gap: 8px;">
                <button class="btn btn-primary" style="flex: 1;" onclick="event.stopPropagation(); startChat('${match.user_id}')">
                    💬 开始对话
                </button>
                <button class="btn btn-secondary" onclick="event.stopPropagation(); viewProfile('${match.user_id}')">
                    👤 查看画像
                </button>
            </div>
        </div>
    `).join('');
    }, 800); // 800ms延迟模拟AI分析
}

// AI分析动画
function showAIAnalysisAnimation() {
    const texts = [
        '正在分析你的人格特质...',
        '计算兴趣相似度...',
        '评估场景适配性...',
        '预测情感同步度...',
        '生成匹配推荐...'
    ];
    
    let index = 0;
    const textElement = document.getElementById('aiAnalysisText');
    
    if (!textElement) return;
    
    const interval = setInterval(() => {
        if (index < texts.length) {
            textElement.textContent = texts[index];
            index++;
        } else {
            textElement.textContent = '✓ 分析完成！已为你找到最佳匹配';
            clearInterval(interval);
        }
    }, 150);
}

// 查看匹配详情
function viewMatchDetail(userId) {
    // 这里可以显示更详细的匹配信息
    console.log('查看匹配详情:', userId);
}

// 查看用户画像
function viewProfile(userId) {
    alert('查看用户画像功能（演示版本）');
}

// 开始对话
function startChat(userId) {
    // 查找或创建对话
    let conversation = mockData.conversations.find(c => c.partner_id === userId);
    
    if (!conversation) {
        // 创建新对话
        const partner = findUserById(userId);
        conversation = {
            conversation_id: `conv-${Date.now()}`,
            partner_id: userId,
            partner_name: partner.username,
            scene: currentScene,
            scene_name: getSceneName(currentScene),
            last_message: '',
            last_time: '刚刚',
            unread: 0
        };
        mockData.conversations.unshift(conversation);
        mockData.messages[conversation.conversation_id] = [];
    }
    
    // 切换到对话页面
    showPage('chat');
    loadConversation(conversation.conversation_id);
}

// 查找用户
function findUserById(userId) {
    for (const scene in mockData.matches) {
        const match = mockData.matches[scene].find(m => m.user_id === userId);
        if (match) return match;
    }
    return null;
}

// 获取场景名称
function getSceneName(scene) {
    const names = {
        study: '考研自习室',
        career: '职业咨询室',
        mental: '心理树洞',
        hobby: '兴趣社群'
    };
    return names[scene] || scene;
}

// 安全的DOM元素更新
function safeSetText(elementId, text) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = text;
    }
}

function safeSetHTML(elementId, html) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = html;
    }
}

// 加载对话列表
function loadConversations() {
    const container = document.getElementById('chatList');
    const conversations = mockData.conversations;
    
    if (conversations.length === 0) {
        container.innerHTML = '<div style="padding: 20px; text-align: center; color: #6d7883;">暂无对话</div>';
        return;
    }
    
    container.innerHTML = conversations.map(conv => `
        <div class="chat-item ${currentConversation?.conversation_id === conv.conversation_id ? 'active' : ''}" 
             onclick="loadConversation('${conv.conversation_id}')">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 6px;">
                <strong style="color: #c5d1de; font-weight: 600;">${conv.partner_name}</strong>
                ${conv.unread > 0 ? `<span style="background: #5288c1; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600;">${conv.unread}</span>` : ''}
            </div>
            <div style="font-size: 12px; color: #6d7883; margin-bottom: 6px;">
                ${getSceneIcon(conv.scene)} ${conv.scene_name}
            </div>
            <div style="font-size: 13px; color: #8b98a5; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                ${conv.last_message}
            </div>
            <div style="font-size: 11px; color: #6d7883; margin-top: 6px;">
                ${conv.last_time}
            </div>
        </div>
    `).join('');
}

// 获取场景图标
function getSceneIcon(scene) {
    const icons = {
        study: '📚',
        career: '💼',
        mental: '💭',
        hobby: '🎨'
    };
    return icons[scene] || '💬';
}

// 加载对话
function loadConversation(conversationId) {
    currentConversation = mockData.conversations.find(c => c.conversation_id === conversationId);
    if (!currentConversation) return;
    
    // 更新对话列表选中状态
    loadConversations();
    
    // 加载消息
    const messages = mockData.messages[conversationId] || [];
    const container = document.getElementById('chatMessages');
    
    container.innerHTML = messages.map(msg => {
        const isAI = msg.is_ai || msg.sender_id === 'ai-assistant';
        const isSent = msg.sender_id === mockData.currentUser.user_id;
        const messageClass = isAI ? 'ai' : (isSent ? 'sent' : 'received');
        
        return `
            <div class="message ${messageClass}">
                <div class="message-bubble">
                    ${isAI ? '<div style="font-weight: bold; margin-bottom: 4px;">🤖 AI助手小智<span class="ai-badge">AI</span></div>' : ''}
                    <div>${msg.content}</div>
                    <div style="font-size: 12px; margin-top: 4px; opacity: 0.7;">
                        ${formatTime(msg.timestamp)}
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    // 滚动到底部
    container.scrollTop = container.scrollHeight;
    
    // 清除未读标记
    currentConversation.unread = 0;
    
    // 启动沉默检测
    startSilenceDetection();
}

// 格式化时间
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
}

// 发送消息
function sendMessage() {
    const input = document.getElementById('messageInput');
    const content = input.value.trim();
    
    if (!content || !currentConversation) return;
    
    // 创建新消息
    const message = {
        message_id: `msg-${Date.now()}`,
        sender_id: mockData.currentUser.user_id,
        sender_name: mockData.currentUser.username,
        content: content,
        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
        type: 'text'
    };
    
    // 添加到消息列表
    if (!mockData.messages[currentConversation.conversation_id]) {
        mockData.messages[currentConversation.conversation_id] = [];
    }
    mockData.messages[currentConversation.conversation_id].push(message);
    
    // 更新对话最后消息
    currentConversation.last_message = content;
    currentConversation.last_time = '刚刚';
    
    // 清空输入框
    input.value = '';
    
    // 重新加载消息
    loadConversation(currentConversation.conversation_id);
    
    // 清除AI建议
    document.getElementById('aiSuggestionBox').innerHTML = '';
    
    // 重置沉默检测
    messageCount++;
    startSilenceDetection();
    
    // 模拟对方回复
    setTimeout(() => {
        simulateReply();
    }, 2000 + Math.random() * 3000);
}

// 模拟对方回复
function simulateReply() {
    if (!currentConversation) return;
    
    const replies = [
        '我也是这么想的',
        '说得对，我们可以一起努力',
        '这个想法不错',
        '我有类似的经历',
        '谢谢你的分享',
        '我们可以交流一下经验',
        '这个话题很有意思',
        '我也遇到过类似的问题'
    ];
    
    const message = {
        message_id: `msg-${Date.now()}`,
        sender_id: currentConversation.partner_id,
        sender_name: currentConversation.partner_name,
        content: replies[Math.floor(Math.random() * replies.length)],
        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
        type: 'text'
    };
    
    mockData.messages[currentConversation.conversation_id].push(message);
    currentConversation.last_message = message.content;
    currentConversation.last_time = '刚刚';
    
    loadConversation(currentConversation.conversation_id);
    messageCount++;
}

// 沉默检测
function startSilenceDetection() {
    // 清除之前的计时器
    if (silenceTimer) {
        clearTimeout(silenceTimer);
    }
    
    // 30秒后AI助手参与对话
    silenceTimer = setTimeout(() => {
        aiAssistantJoinChat();
    }, 30000);
}

// AI助手参与对话
function aiAssistantJoinChat() {
    if (!currentConversation) return;
    
    const messages = mockData.messages[currentConversation.conversation_id] || [];
    const scene = currentConversation.scene;
    
    // 根据场景选择合适的AI消息
    const sceneMessages = mockData.aiAssistantMessages[scene] || mockData.aiAssistantMessages.hobby;
    const aiMessage = sceneMessages[Math.floor(Math.random() * sceneMessages.length)];
    
    // 创建AI消息
    const message = {
        message_id: `msg-ai-${Date.now()}`,
        sender_id: 'ai-assistant',
        sender_name: 'AI助手小智',
        content: aiMessage,
        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
        type: 'ai',
        is_ai: true
    };
    
    mockData.messages[currentConversation.conversation_id].push(message);
    currentConversation.last_message = aiMessage;
    currentConversation.last_time = '刚刚';
    
    // 重新加载消息
    loadConversation(currentConversation.conversation_id);
    
    // 显示AI参与提示
    showAIJoinNotification();
}

// 显示AI参与通知
function showAIJoinNotification() {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: linear-gradient(135deg, #5288c1 0%, #4a7aad 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 14px;
        box-shadow: 0 6px 20px rgba(82, 136, 193, 0.4);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
        border: 1px solid rgba(255, 255, 255, 0.1);
    `;
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="font-size: 28px;">🤖</div>
            <div>
                <div style="font-weight: 600; margin-bottom: 4px;">小智来啦～</div>
                <div style="font-size: 12px; opacity: 0.95;">一起聊聊天吧！</div>
            </div>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // 3秒后自动消失
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 添加动画样式
if (!document.getElementById('ai-animations')) {
    const style = document.createElement('style');
    style.id = 'ai-animations';
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// 刷新画像
function refreshProfile() {
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = '🔄 AI正在分析...';
    
    // 模拟AI分析过程
    setTimeout(() => {
        btn.textContent = '✓ 画像已更新';
        setTimeout(() => {
            btn.disabled = false;
            btn.textContent = '🔄 刷新画像';
            alert('画像已根据最新对话记录更新！\n\n更新内容：\n- 新增兴趣标签：机器学习\n- 开放性提升 2%\n- 对话深度评分提升');
        }, 1000);
    }, 2000);
}

// 导出画像
function downloadProfile() {
    alert('画像导出功能（演示版本）\n\n将导出包含以下内容的PDF文件：\n- AI综合评价\n- 人格特质分析\n- 兴趣图谱\n- 行为特征\n- 成长建议');
}

// 加载报告
function loadReport(type) {
    const types = {
        weekly: '周报',
        monthly: '月报',
        annual: '年报'
    };
    alert(`加载${types[type]}（演示版本）`);
}

// 下载报告
function downloadReport() {
    alert('报告下载功能（演示版本）');
}

// 分享报告
function shareReport() {
    alert('报告分享功能（演示版本）\n分享链接：https://youth-companion.com/reports/share/abc123');
}

// 修改密码
function changePassword() {
    const newPassword = prompt('请输入新密码：');
    if (newPassword) {
        alert('密码修改成功（演示版本）');
    }
}

// 导出数据
function exportData() {
    alert('数据导出功能（演示版本）\n您的数据将以JSON格式导出');
}

// 删除账号
function deleteAccount() {
    if (confirm('确定要删除账号吗？此操作不可恢复！')) {
        alert('账号删除功能（演示版本）');
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    // 延迟加载匹配，确保所有脚本都已加载
    setTimeout(() => {
        loadMatches();
    }, 100);
    
    // 监听回车键发送消息
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    // 点击模态框背景关闭
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });
});
