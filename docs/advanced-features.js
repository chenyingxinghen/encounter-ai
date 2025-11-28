// 高级功能模块

// 1. 对话质量实时监测
class ConversationQualityMonitor {
    constructor() {
        this.metrics = {
            topicDepth: 0,
            responseConsistency: 0,
            emotionSync: 0,
            messageLength: [],
            responseTime: []
        };
    }
    
    // 分析消息质量
    analyzeMessage(message, previousMessages) {
        // 话题深度分析
        this.analyzeTopicDepth(message, previousMessages);
        
        // 回应一致性分析
        this.analyzeResponseConsistency(message, previousMessages);
        
        // 情感同步性分析
        this.analyzeEmotionSync(message, previousMessages);
        
        return this.getQualityScore();
    }
    
    analyzeTopicDepth(message, previousMessages) {
        // 简化的话题深度分析
        const keywords = ['为什么', '怎么', '如何', '原因', '想法', '感受', '经历'];
        const hasDeepKeyword = keywords.some(kw => message.content.includes(kw));
        const messageLength = message.content.length;
        
        this.metrics.topicDepth = hasDeepKeyword && messageLength > 20 ? 0.8 : 0.5;
    }
    
    analyzeResponseConsistency(message, previousMessages) {
        if (previousMessages.length === 0) {
            this.metrics.responseConsistency = 0.7;
            return;
        }
        
        const lastMessage = previousMessages[previousMessages.length - 1];
        const timeDiff = new Date(message.timestamp) - new Date(lastMessage.timestamp);
        
        // 响应时间合理性
        this.metrics.responseConsistency = timeDiff < 300000 ? 0.8 : 0.5; // 5分钟内
    }
    
    analyzeEmotionSync(message, previousMessages) {
        // 简化的情感分析
        const positiveWords = ['好', '棒', '开心', '高兴', '喜欢', '感谢', '谢谢'];
        const negativeWords = ['难过', '伤心', '压力', '焦虑', '困难', '问题'];
        
        const hasPositive = positiveWords.some(w => message.content.includes(w));
        const hasNegative = negativeWords.some(w => message.content.includes(w));
        
        if (previousMessages.length > 0) {
            const lastMessage = previousMessages[previousMessages.length - 1];
            const lastHasPositive = positiveWords.some(w => lastMessage.content.includes(w));
            const lastHasNegative = negativeWords.some(w => lastMessage.content.includes(w));
            
            // 情感一致性
            if ((hasPositive && lastHasPositive) || (hasNegative && lastHasNegative)) {
                this.metrics.emotionSync = 0.9;
            } else if ((hasPositive && lastHasNegative) || (hasNegative && lastHasPositive)) {
                this.metrics.emotionSync = 0.6; // 情感转换
            } else {
                this.metrics.emotionSync = 0.7;
            }
        } else {
            this.metrics.emotionSync = 0.7;
        }
    }
    
    getQualityScore() {
        return {
            topicDepth: Math.round(this.metrics.topicDepth * 100),
            responseConsistency: Math.round(this.metrics.responseConsistency * 100),
            emotionSync: Math.round(this.metrics.emotionSync * 100),
            overall: Math.round((this.metrics.topicDepth + this.metrics.responseConsistency + this.metrics.emotionSync) / 3 * 100)
        };
    }
}

// 2. 心理健康监测
class MentalHealthMonitor {
    constructor() {
        this.emotionHistory = [];
        this.riskKeywords = [
            '抑郁', '自杀', '绝望', '没有意义', '活不下去',
            '痛苦', '崩溃', '无助', '孤独', '失眠'
        ];
        this.negativeKeywords = [
            '难过', '伤心', '焦虑', '压力', '烦恼',
            '困难', '问题', '担心', '害怕', '紧张'
        ];
    }
    
    // 检测消息情绪
    detectEmotion(message) {
        const content = message.content;
        let emotionLevel = 'neutral'; // neutral, negative, risk
        let keywords = [];
        
        // 检测高风险关键词
        for (const keyword of this.riskKeywords) {
            if (content.includes(keyword)) {
                emotionLevel = 'risk';
                keywords.push(keyword);
            }
        }
        
        // 检测负面关键词
        if (emotionLevel === 'neutral') {
            for (const keyword of this.negativeKeywords) {
                if (content.includes(keyword)) {
                    emotionLevel = 'negative';
                    keywords.push(keyword);
                }
            }
        }
        
        const emotion = {
            timestamp: message.timestamp,
            level: emotionLevel,
            keywords: keywords,
            content: content
        };
        
        this.emotionHistory.push(emotion);
        
        return emotion;
    }
    
    // 检测持续低落情绪
    detectPersistentNegativeEmotion() {
        if (this.emotionHistory.length < 5) return false;
        
        const recent = this.emotionHistory.slice(-5);
        const negativeCount = recent.filter(e => e.level === 'negative' || e.level === 'risk').length;
        
        return negativeCount >= 3;
    }
    
    // 获取心理健康建议
    getHealthAdvice(emotion) {
        if (emotion.level === 'risk') {
            return {
                level: 'high',
                message: '我们注意到您可能正在经历困难时期。建议您：',
                suggestions: [
                    '与信任的朋友或家人交流',
                    '联系学校心理咨询中心',
                    '拨打心理援助热线：400-161-9995',
                    '如有紧急情况，请拨打120或前往医院'
                ],
                resources: [
                    { name: '清华大学心理咨询中心', phone: '010-62782502' },
                    { name: '北京市心理援助热线', phone: '010-82951332' },
                    { name: '全国心理援助热线', phone: '400-161-9995' }
                ]
            };
        } else if (emotion.level === 'negative') {
            return {
                level: 'medium',
                message: '感觉到您最近可能有些压力，这里有一些建议：',
                suggestions: [
                    '尝试深呼吸或冥想放松',
                    '进行适量运动，如散步或跑步',
                    '与朋友聊聊天，分享你的感受',
                    '保持规律作息，充足睡眠',
                    '做一些你喜欢的事情'
                ],
                resources: []
            };
        }
        
        return null;
    }
}

// 3. 用户画像动态更新
class ProfileUpdater {
    constructor() {
        this.interestExtractor = new InterestExtractor();
        this.personalityAnalyzer = new PersonalityAnalyzer();
    }
    
    // 从对话中提取信息
    extractInfoFromConversation(messages) {
        const updates = {
            newInterests: [],
            emotionTrends: [],
            topicPreferences: [],
            communicationStyle: {}
        };
        
        // 提取兴趣
        messages.forEach(msg => {
            const interests = this.interestExtractor.extract(msg.content);
            updates.newInterests.push(...interests);
        });
        
        // 去重
        updates.newInterests = [...new Set(updates.newInterests)];
        
        // 分析沟通风格
        updates.communicationStyle = this.analyzeCommunicationStyle(messages);
        
        return updates;
    }
    
    analyzeCommunicationStyle(messages) {
        const userMessages = messages.filter(m => m.sender_id === mockData.currentUser.user_id);
        
        if (userMessages.length === 0) return {};
        
        const avgLength = userMessages.reduce((sum, m) => sum + m.content.length, 0) / userMessages.length;
        const hasQuestions = userMessages.some(m => m.content.includes('？') || m.content.includes('?'));
        const hasEmotions = userMessages.some(m => /[！!😊😄😢😭]/.test(m.content));
        
        return {
            messageLength: avgLength > 50 ? 'detailed' : 'concise',
            interactive: hasQuestions ? 'high' : 'low',
            expressive: hasEmotions ? 'high' : 'low'
        };
    }
}

// 4. 兴趣提取器
class InterestExtractor {
    constructor() {
        this.interestKeywords = {
            academic: ['考研', '学习', '算法', '编程', '数学', '物理', '化学', '英语', '论文', '科研', '数据结构', '机器学习'],
            career: ['实习', '工作', '面试', '简历', '职业', '公司', '创业', '项目', '技术创业'],
            hobby: ['音乐', '电影', '阅读', '运动', '游戏', '旅行', '摄影', '绘画', '书法', '舞蹈', '跑步'],
            sports: ['跑步', '篮球', '足球', '游泳', '健身', '瑜伽', '羽毛球', '乒乓球'],
            entertainment: ['电影', '电视剧', '综艺', '动漫', '音乐', '演唱会', '话剧']
        };
        this.interestCount = {};
    }
    
    extract(text) {
        const interests = [];
        
        for (const category in this.interestKeywords) {
            for (const keyword of this.interestKeywords[category]) {
                if (text.includes(keyword)) {
                    interests.push(keyword);
                    // 统计提及次数
                    this.interestCount[keyword] = (this.interestCount[keyword] || 0) + 1;
                }
            }
        }
        
        return interests;
    }
    
    getTopInterests(limit = 10) {
        return Object.entries(this.interestCount)
            .sort((a, b) => b[1] - a[1])
            .slice(0, limit)
            .map(([interest, count]) => ({ interest, count }));
    }
}

// 5. 人格分析器
class PersonalityAnalyzer {
    analyze(messages) {
        // 简化的人格分析
        const traits = {
            extraversion: 0.5,
            agreeableness: 0.5,
            conscientiousness: 0.5,
            neuroticism: 0.5,
            openness: 0.5
        };
        
        const userMessages = messages.filter(m => m.sender_id === mockData.currentUser.user_id);
        
        if (userMessages.length === 0) return traits;
        
        // 外向性：消息频率和长度
        const avgLength = userMessages.reduce((sum, m) => sum + m.content.length, 0) / userMessages.length;
        traits.extraversion = Math.min(avgLength / 100, 1);
        
        // 宜人性：积极词汇
        const positiveWords = ['好', '棒', '谢谢', '感谢', '喜欢', '开心'];
        const positiveCount = userMessages.filter(m => 
            positiveWords.some(w => m.content.includes(w))
        ).length;
        traits.agreeableness = Math.min(positiveCount / userMessages.length * 2, 1);
        
        // 尽责性：问题和计划
        const planWords = ['计划', '安排', '目标', '准备', '学习'];
        const planCount = userMessages.filter(m => 
            planWords.some(w => m.content.includes(w))
        ).length;
        traits.conscientiousness = Math.min(planCount / userMessages.length * 2, 1);
        
        return traits;
    }
    
    // 生成AI画像描述
    generateProfileDescription(traits, messages, interests) {
        const userMessages = messages.filter(m => m.sender_id === mockData.currentUser.user_id);
        const avgLength = userMessages.length > 0 
            ? Math.round(userMessages.reduce((sum, m) => sum + m.content.length, 0) / userMessages.length)
            : 0;
        
        // 性格特征描述
        let personality = '';
        if (traits.extraversion < 0.4) {
            personality = '你是一个内向但富有创造力的人，在对话中表现出较强的同理心和倾听能力。';
        } else if (traits.extraversion > 0.6) {
            personality = '你是一个外向且善于表达的人，在对话中表现出积极主动的态度。';
        } else {
            personality = '你的性格介于内向和外向之间，能够灵活适应不同的社交场合。';
        }
        
        // 沟通风格描述
        let communication = '';
        if (avgLength > 60) {
            communication = `你的表达方式细腻且富有情感，平均消息长度较长（约${avgLength}字），说明你倾向于详细阐述自己的想法。`;
        } else if (avgLength < 30) {
            communication = `你的表达简洁明了，平均消息长度较短（约${avgLength}字），倾向于直接表达核心观点。`;
        } else {
            communication = `你的表达方式适中，平均消息长度约${avgLength}字，能够清晰传达想法。`;
        }
        
        return {
            personality,
            communication,
            avgLength
        };
    }
}

// 6. 内容审查系统
class ContentModerator {
    constructor() {
        this.violationKeywords = {
            harassment: ['骚扰', '威胁', '恐吓', '侮辱', '谩骂'],
            inappropriate: ['色情', '暴力', '血腥', '恐怖'],
            spam: ['广告', '推广', '加微信', '加QQ', '刷单'],
            sensitive: ['政治', '宗教', '种族']
        };
    }
    
    // 审查内容
    moderate(content) {
        const result = {
            passed: true,
            violationType: null,
            keywords: [],
            severity: 'none' // none, low, medium, high
        };
        
        for (const type in this.violationKeywords) {
            for (const keyword of this.violationKeywords[type]) {
                if (content.includes(keyword)) {
                    result.passed = false;
                    result.violationType = type;
                    result.keywords.push(keyword);
                    result.severity = this.getSeverity(type);
                    break;
                }
            }
            if (!result.passed) break;
        }
        
        return result;
    }
    
    getSeverity(type) {
        const severityMap = {
            harassment: 'high',
            inappropriate: 'high',
            spam: 'low',
            sensitive: 'medium'
        };
        return severityMap[type] || 'low';
    }
    
    // 获取处理建议
    getAction(severity) {
        const actions = {
            low: { action: 'warn', message: '您的消息包含不当内容，请注意言辞' },
            medium: { action: 'block', message: '您的消息包含敏感内容，已被拦截' },
            high: { action: 'block_and_report', message: '您的消息严重违规，已被拦截并记录' }
        };
        return actions[severity] || actions.low;
    }
}

// 7. 匹配算法优化器
class MatchingOptimizer {
    constructor() {
        this.feedbackData = [];
        this.weights = {
            personality: 0.25,
            interest: 0.30,
            scene: 0.25,
            emotion: 0.20
        };
    }
    
    // 收集反馈
    collectFeedback(matchId, userId, feedback) {
        this.feedbackData.push({
            matchId,
            userId,
            feedback, // positive, negative, neutral
            timestamp: new Date()
        });
        
        // 每收集10条反馈，优化一次权重
        if (this.feedbackData.length % 10 === 0) {
            this.optimizeWeights();
        }
    }
    
    // 优化权重
    optimizeWeights() {
        // 简化的权重优化逻辑
        const recentFeedback = this.feedbackData.slice(-50);
        const positiveCount = recentFeedback.filter(f => f.feedback === 'positive').length;
        const negativeCount = recentFeedback.filter(f => f.feedback === 'negative').length;
        
        const successRate = positiveCount / recentFeedback.length;
        
        // 根据成功率调整权重
        if (successRate < 0.6) {
            // 增加兴趣权重
            this.weights.interest += 0.05;
            this.weights.personality -= 0.05;
        }
        
        // 归一化权重
        const sum = Object.values(this.weights).reduce((a, b) => a + b, 0);
        for (const key in this.weights) {
            this.weights[key] /= sum;
        }
    }
    
    // 计算匹配度
    calculateMatchScore(userA, userB, scene) {
        const personalityScore = this.calculatePersonalityScore(userA, userB);
        const interestScore = this.calculateInterestScore(userA, userB);
        const sceneScore = this.calculateSceneScore(userA, userB, scene);
        const emotionScore = this.calculateEmotionScore(userA, userB);
        
        return (
            personalityScore * this.weights.personality +
            interestScore * this.weights.interest +
            sceneScore * this.weights.scene +
            emotionScore * this.weights.emotion
        ) * 100;
    }
    
    calculatePersonalityScore(userA, userB) {
        // MBTI兼容性矩阵
        const compatibility = {
            'INFP': ['ENFJ', 'ENTJ', 'INFJ', 'INTJ'],
            'INTJ': ['ENFP', 'ENTP', 'INFP', 'INTP'],
            'ENFP': ['INTJ', 'INFJ', 'ENTJ', 'ENFJ'],
            'INFJ': ['ENFP', 'ENTP', 'INFP', 'INTJ']
        };
        
        const typeA = userA.mbti_type;
        const typeB = userB.mbti_type;
        
        if (compatibility[typeA]?.includes(typeB)) {
            return 0.9;
        } else if (typeA === typeB) {
            return 0.7;
        } else {
            return 0.5;
        }
    }
    
    calculateInterestScore(userA, userB) {
        // 安全检查
        if (!userA.interests || !userB.interests) return 0.5;
        
        const interestsA = [
            ...(userA.interests.academic || []), 
            ...(userA.interests.career || []), 
            ...(userA.interests.hobby || [])
        ];
        const interestsB = [
            ...(userB.interests.academic || []), 
            ...(userB.interests.career || []), 
            ...(userB.interests.hobby || [])
        ];
        
        if (interestsA.length === 0 || interestsB.length === 0) return 0.5;
        
        const common = interestsA.filter(i => interestsB.includes(i));
        const total = new Set([...interestsA, ...interestsB]).size;
        
        return total > 0 ? common.length / total : 0.5;
    }
    
    calculateSceneScore(userA, userB, scene) {
        // 场景相关性评分
        return 0.8; // 简化实现
    }
    
    calculateEmotionScore(userA, userB) {
        // 情感同步性评分
        return 0.75; // 简化实现
    }
}

// 8. 虚拟用户管理器
class VirtualUserManager {
    constructor() {
        this.virtualUsers = [];
        this.realUserCount = 0;
        this.virtualUserWeight = 1.0;
    }
    
    // 生成虚拟用户
    generateVirtualUser(mbtiType, scene) {
        const names = ['小明', '小红', '小刚', '小丽', '小华', '小芳', '小强', '小美'];
        const schools = ['清华大学', '北京大学', '复旦大学', '上海交通大学'];
        const majors = ['计算机科学', '软件工程', '数学', '物理', '化学', '经济学'];
        const academicInterests = ['考研', '学习', '算法', '编程', '数学', '英语'];
        const careerInterests = ['软件工程师', '产品经理', '数据分析师', '研究员'];
        const hobbyInterests = ['阅读', '音乐', '运动', '电影', '旅行', '摄影'];
        
        return {
            user_id: `virtual-${Date.now()}-${Math.random()}`,
            username: names[Math.floor(Math.random() * names.length)],
            school: schools[Math.floor(Math.random() * schools.length)],
            major: majors[Math.floor(Math.random() * majors.length)],
            grade: Math.floor(Math.random() * 4) + 1,
            mbti_type: mbtiType,
            is_virtual: true,
            scene_preference: scene,
            interests: {
                academic: [academicInterests[Math.floor(Math.random() * academicInterests.length)]],
                career: [careerInterests[Math.floor(Math.random() * careerInterests.length)]],
                hobby: [hobbyInterests[Math.floor(Math.random() * hobbyInterests.length)]]
            }
        };
    }
    
    // 更新虚拟用户权重
    updateVirtualUserWeight(realUserCount) {
        this.realUserCount = realUserCount;
        
        // 真实用户越多，虚拟用户权重越低
        if (realUserCount < 100) {
            this.virtualUserWeight = 1.0;
        } else if (realUserCount < 500) {
            this.virtualUserWeight = 0.5;
        } else if (realUserCount < 1000) {
            this.virtualUserWeight = 0.2;
        } else {
            this.virtualUserWeight = 0.1;
        }
    }
    
    // 模拟虚拟用户行为
    simulateVirtualUserBehavior(virtualUser, conversation) {
        // 生成回复
        const responses = [
            '我也有类似的想法',
            '这个话题很有意思',
            '我们可以深入讨论一下',
            '你说得很有道理',
            '我也遇到过类似的情况'
        ];
        
        return responses[Math.floor(Math.random() * responses.length)];
    }
}

// 导出所有类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ConversationQualityMonitor,
        MentalHealthMonitor,
        ProfileUpdater,
        InterestExtractor,
        PersonalityAnalyzer,
        ContentModerator,
        MatchingOptimizer,
        VirtualUserManager
    };
}
