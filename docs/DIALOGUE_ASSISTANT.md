# AI对话助手系统

## 概述

AI对话助手系统是青春伴行平台的核心功能之一，旨在帮助用户克服"找不到话题"的障碍，在对话陷入沉默或遇到困难时提供智能引导和情绪支持。

## 核心功能

### 1. 沉默检测

系统通过两种方式检测对话沉默：

#### 时间沉默
- **阈值**: 15秒无回复
- **触发条件**: 距离最后一条消息超过15秒

#### 短消息沉默
- **阈值**: 连续3轮回复少于30字
- **触发条件**: 最近3条消息的内容都少于30个字符

### 2. 沉默类型识别

系统能够识别两种沉默类型：

#### 内向型沉默
- **特征**: 用户性格内向，不善于主动开启话题
- **情绪分析**: 消息情绪以中性为主
- **介入策略**: 提供简单、轻松的话题建议

#### 焦虑型沉默
- **特征**: 用户感到紧张、焦虑，不知道该说什么
- **情绪分析**: 消息中包含较多焦虑或负面情绪
- **介入策略**: 先提供情绪安抚，再给出话题建议

### 3. 话题建议生成

根据对话场景和沉默类型，生成适合的话题建议：

#### 考研自习室场景
- 备考进度交流
- 学习方法分享
- 目标院校讨论
- 学习困难互助

#### 职业咨询室场景
- 职业规划讨论
- 实习经验分享
- 行业发展交流
- 工作环境期望

#### 心理树洞场景
- 情绪倾诉引导
- 解压方式分享
- 心情感受交流
- 放松话题建议

#### 兴趣社群场景
- 共同兴趣讨论
- 有趣内容分享
- 兴趣培养经验
- 相关心得交流

### 4. 情绪支持

针对不同情绪状态提供相应支持：

#### 焦虑情绪
- 安抚语句："别紧张，慢慢来"
- 鼓励表达："对方也是来交流的朋友"
- 降低压力："可以先从简单的话题开始"

#### 负面情绪
- 共情理解："我感觉到你可能心情不太好"
- 倾诉引导："如果愿意的话，可以和对方聊聊"
- 情感支持："有时候倾诉出来会好受一些"

#### 积极情绪
- 正向反馈："看起来你们聊得很开心"
- 鼓励延续："继续保持这种轻松的氛围吧"

### 5. 介入频率控制

为避免过度干扰，系统实施严格的介入频率控制：

- **冷却期**: 20分钟
- **规则**: 在20分钟内最多介入1次
- **目的**: 给用户足够的自主交流空间

### 6. 用户偏好记录

尊重用户意愿，支持个性化设置：

- **启用/禁用**: 用户可以选择是否接受AI介入
- **拒绝记录**: 记录用户拒绝AI介入的次数和时间
- **偏好持久化**: 保存用户的偏好设置
- **自动暂停**: 用户明确拒绝后自动暂停介入

## 数据模型

### AIIntervention（AI介入记录）

```python
class AIIntervention:
    intervention_id: str          # 介入记录ID
    conversation_id: str          # 对话ID
    trigger_type: str             # 触发类型: silence, emotion_conflict, manual
    intervention_type: str        # 介入类型: topic_suggestion, emotional_support
    content: str                  # 介入内容
    user_response: Optional[str]  # 用户响应: accepted, rejected, ignored
    timestamp: datetime           # 介入时间
```

### SilenceType（沉默类型）

```python
class SilenceType:
    type: str          # 沉默类型: introverted, anxious, none
    confidence: float  # 置信度 (0-1)
```

### UserPreference（用户偏好）

```python
class UserPreference:
    user_id: str                      # 用户ID
    ai_intervention_enabled: bool     # 是否启用AI介入
    last_rejection_time: Optional[datetime]  # 最后拒绝时间
    rejection_count: int              # 拒绝次数
    updated_at: datetime              # 更新时间
```

## 服务接口

### DialogueAssistantService

#### detect_silence()
检测对话沉默状态

```python
def detect_silence(
    conversation_id: str,
    recent_messages: List[Message]
) -> Tuple[bool, Optional[SilenceType]]
```

**参数**:
- `conversation_id`: 对话ID
- `recent_messages`: 最近的消息列表

**返回**: (是否沉默, 沉默类型)

#### should_intervene()
判断是否应该介入

```python
def should_intervene(
    conversation_id: str,
    user_id: str
) -> bool
```

**参数**:
- `conversation_id`: 对话ID
- `user_id`: 用户ID

**返回**: 是否应该介入

#### generate_topic_suggestion()
生成话题建议

```python
def generate_topic_suggestion(
    conversation_id: str,
    scene: str,
    recent_messages: List[Message],
    silence_type: Optional[SilenceType] = None
) -> str
```

**参数**:
- `conversation_id`: 对话ID
- `scene`: 对话场景
- `recent_messages`: 最近的消息列表
- `silence_type`: 沉默类型（可选）

**返回**: 话题建议内容

#### provide_emotional_support()
提供情绪支持

```python
def provide_emotional_support(
    user_id: str,
    emotion: str,
    recent_messages: List[Message]
) -> str
```

**参数**:
- `user_id`: 用户ID
- `emotion`: 情绪类型
- `recent_messages`: 最近的消息列表

**返回**: 情绪支持内容

#### record_intervention()
记录AI介入

```python
def record_intervention(
    conversation_id: str,
    trigger_type: str,
    intervention_type: str,
    content: str
) -> AIIntervention
```

**参数**:
- `conversation_id`: 对话ID
- `trigger_type`: 触发类型
- `intervention_type`: 介入类型
- `content`: 介入内容

**返回**: AI介入记录

#### record_user_preference()
记录用户偏好

```python
def record_user_preference(
    user_id: str,
    ai_intervention_enabled: bool
) -> UserPreference
```

**参数**:
- `user_id`: 用户ID
- `ai_intervention_enabled`: 是否启用AI介入

**返回**: 用户偏好

## 使用示例

### 基本使用流程

```python
from src.services.dialogue_assistant_service import DialogueAssistantService
from src.services.conversation_service import ConversationService

# 初始化服务
dialogue_service = DialogueAssistantService()
conversation_service = ConversationService()

# 1. 检测沉默
is_silent, silence_type = dialogue_service.detect_silence(
    conversation_id,
    recent_messages
)

# 2. 判断是否介入
if is_silent:
    should = dialogue_service.should_intervene(conversation_id, user_id)
    
    if should:
        # 3. 生成话题建议
        suggestion = dialogue_service.generate_topic_suggestion(
            conversation_id,
            scene,
            recent_messages,
            silence_type
        )
        
        # 4. 记录介入
        intervention = dialogue_service.record_intervention(
            conversation_id,
            "silence",
            "topic_suggestion",
            suggestion
        )
        
        # 5. 更新对话统计
        conversation_service.increment_ai_intervention_count(conversation_id)
```

### 情绪支持示例

```python
# 检测到用户焦虑情绪
if message.emotion == "anxious":
    support = dialogue_service.provide_emotional_support(
        user_id,
        "anxious",
        recent_messages
    )
    
    # 记录情绪支持介入
    dialogue_service.record_intervention(
        conversation_id,
        "emotion_conflict",
        "emotional_support",
        support
    )
```

### 用户偏好管理示例

```python
# 用户拒绝AI介入
dialogue_service.record_user_preference(user_id, False)

# 用户重新启用AI介入
dialogue_service.record_user_preference(user_id, True)

# 查询用户偏好
preference = dialogue_service.get_user_preference(user_id)
if preference and not preference.ai_intervention_enabled:
    print("用户已禁用AI介入")
```

## 设计原则

### 1. 主动但有边界
- AI助手在适当时机主动介入
- 严格遵守介入频率限制
- 尊重用户的拒绝意愿

### 2. 场景化适配
- 根据不同场景提供针对性建议
- 考虑场景特点调整介入策略
- 话题建议符合场景需求

### 3. 情感智能
- 识别用户情绪状态
- 提供共情式支持
- 区分不同沉默类型

### 4. 用户为中心
- 支持个性化偏好设置
- 记录用户反馈
- 持续优化介入策略

## 未来优化方向

### 1. 集成ChatGLM模型
- 使用大语言模型生成更自然的话题建议
- 提供更个性化的情绪支持
- 实现上下文感知的对话引导

### 2. 深度学习优化
- 训练沉默类型识别模型
- 优化话题建议生成算法
- 提高情绪识别准确率

### 3. 用户反馈学习
- 收集用户对AI建议的反馈
- 基于反馈优化介入策略
- 个性化调整介入阈值

### 4. 多模态支持
- 支持语音消息分析
- 支持表情符号情感分析
- 综合多种信号判断沉默

## 测试覆盖

系统包含全面的单元测试，覆盖以下场景：

- ✅ 时间沉默检测
- ✅ 短消息沉默检测
- ✅ 沉默类型识别（内向型/焦虑型）
- ✅ 介入条件判断
- ✅ 介入频率控制（冷却期）
- ✅ 话题建议生成（各场景）
- ✅ 情绪支持提供
- ✅ AI介入记录
- ✅ 用户偏好管理
- ✅ 介入历史查询
- ✅ 集成测试流程

运行测试：
```bash
pytest tests/test_dialogue_assistant.py -v
```

## 相关文档

- [对话系统文档](CONVERSATION_SYSTEM.md)
- [场景管理文档](SCENE_MANAGEMENT.md)
- [人格识别文档](PERSONALITY_RECOGNITION.md)
