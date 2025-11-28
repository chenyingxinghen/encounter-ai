# 对话系统文档

## 概述

对话系统是青春伴行平台的核心功能之一，负责管理用户之间的对话交互。系统提供了完整的对话生命周期管理，包括对话创建、消息发送、历史记录查询、状态管理等功能。

## 功能特性

### 核心功能

1. **对话管理**
   - 创建新对话
   - 获取对话信息
   - 更新对话状态（活跃、暂停、结束）
   - 查询用户的所有对话

2. **消息管理**
   - 发送文本、图片、语音消息
   - 获取对话历史记录
   - 支持分页查询
   - 支持时间范围过滤

3. **统计与监测**
   - 消息计数
   - 沉默次数统计
   - AI介入次数统计
   - 对话质量指标（话题深度、情感同步性、满意度）

4. **安全控制**
   - 验证用户身份
   - 检查对话状态
   - 防止未授权访问

## 数据模型

### Conversation（对话）

对话是两个用户之间的交流会话。

```python
class Conversation(BaseModel):
    conversation_id: str          # 对话唯一标识
    user_a_id: str               # 用户A的ID
    user_b_id: str               # 用户B的ID
    scene: str                   # 对话场景
    status: str                  # 状态: active, paused, ended
    started_at: datetime         # 开始时间
    ended_at: Optional[datetime] # 结束时间
    message_count: int           # 消息总数
    silence_count: int           # 沉默次数
    ai_intervention_count: int   # AI介入次数
    topic_depth_score: float     # 话题深度得分 (0-10)
    emotion_sync_score: float    # 情感同步性得分 (0-1)
    satisfaction_score: float    # 满意度得分 (0-5)
```

**支持的场景**：
- 考研自习室
- 职业咨询室
- 心理树洞
- 兴趣社群

**对话状态**：
- `active`: 活跃状态，可以正常发送消息
- `paused`: 暂停状态，暂时不能发送消息
- `ended`: 结束状态，对话已结束

### Message（消息）

消息是对话中的单条交流内容。

```python
class Message(BaseModel):
    message_id: str              # 消息唯一标识
    conversation_id: str         # 所属对话ID
    sender_id: str              # 发送者ID
    content: str                # 消息内容
    message_type: str           # 消息类型: text, image, voice
    emotion: Optional[str]      # 情绪类型: positive, neutral, negative, anxious
    emotion_intensity: float    # 情绪强度 (0-1)
    timestamp: datetime         # 发送时间
```

**支持的消息类型**：
- `text`: 文本消息
- `image`: 图片消息
- `voice`: 语音消息

**情绪类型**：
- `positive`: 积极情绪
- `neutral`: 中性情绪
- `negative`: 消极情绪
- `anxious`: 焦虑情绪

## API 使用指南

### 初始化服务

```python
from src.services.conversation_service import ConversationService

service = ConversationService()
```

### 创建对话

```python
from src.models.conversation import ConversationCreateRequest

request = ConversationCreateRequest(
    user_a_id="user_001",
    user_b_id="user_002",
    scene="考研自习室"
)

conversation = service.create_conversation(request)
print(f"对话ID: {conversation.conversation_id}")
```

### 发送消息

```python
from src.models.conversation import MessageSendRequest

request = MessageSendRequest(
    conversation_id=conversation.conversation_id,
    sender_id="user_001",
    content="你好，你也在准备考研吗？",
    message_type="text"
)

message = service.send_message(request)
print(f"消息已发送: {message.message_id}")
```

### 获取对话历史

```python
from src.models.conversation import ConversationHistoryRequest

request = ConversationHistoryRequest(
    conversation_id=conversation.conversation_id,
    limit=50,      # 每页50条
    offset=0       # 从第0条开始
)

messages = service.get_conversation_history(request)
for msg in messages:
    print(f"[{msg.timestamp}] {msg.sender_id}: {msg.content}")
```

### 更新对话状态

```python
from src.models.conversation import ConversationStatusUpdateRequest

# 暂停对话
request = ConversationStatusUpdateRequest(
    conversation_id=conversation.conversation_id,
    status="paused"
)
conversation = service.update_conversation_status(request)

# 结束对话
request = ConversationStatusUpdateRequest(
    conversation_id=conversation.conversation_id,
    status="ended"
)
conversation = service.update_conversation_status(request)
```

### 获取用户的所有对话

```python
# 获取所有对话
conversations = service.get_user_conversations("user_001")

# 只获取活跃对话
active_conversations = service.get_user_conversations("user_001", status="active")

# 只获取已结束对话
ended_conversations = service.get_user_conversations("user_001", status="ended")
```

### 更新质量指标

```python
conversation = service.update_quality_metrics(
    conversation_id=conversation.conversation_id,
    topic_depth_score=8.5,      # 话题深度得分
    emotion_sync_score=0.92,    # 情感同步性得分
    satisfaction_score=4.5      # 满意度得分
)
```

### 增加统计计数

```python
# 增加沉默计数
service.increment_silence_count(conversation.conversation_id)

# 增加AI介入计数
service.increment_ai_intervention_count(conversation.conversation_id)
```

## 错误处理

系统定义了以下异常类型：

### ConversationNotFoundError

当尝试访问不存在的对话时抛出。

```python
from src.utils.exceptions import ConversationNotFoundError

try:
    conversation = service.get_conversation("invalid_id")
except ConversationNotFoundError as e:
    print(f"对话不存在: {e.message}")
```

### InvalidConversationStateError

当对话状态不允许执行某操作时抛出（例如向已结束的对话发送消息）。

```python
from src.utils.exceptions import InvalidConversationStateError

try:
    service.send_message(request)
except InvalidConversationStateError as e:
    print(f"对话状态错误: {e.message}")
```

### UnauthorizedAccessError

当用户尝试访问不属于自己的对话时抛出。

```python
from src.utils.exceptions import UnauthorizedAccessError

try:
    service.send_message(request)
except UnauthorizedAccessError as e:
    print(f"未授权访问: {e.message}")
```

## 使用场景示例

### 场景1：完整的对话流程

```python
# 1. 创建对话
create_request = ConversationCreateRequest(
    user_a_id="user_001",
    user_b_id="user_002",
    scene="考研自习室"
)
conversation = service.create_conversation(create_request)

# 2. 用户A发送消息
msg1_request = MessageSendRequest(
    conversation_id=conversation.conversation_id,
    sender_id="user_001",
    content="你好！",
    message_type="text"
)
service.send_message(msg1_request)

# 3. 用户B回复
msg2_request = MessageSendRequest(
    conversation_id=conversation.conversation_id,
    sender_id="user_002",
    content="你好！很高兴认识你",
    message_type="text"
)
service.send_message(msg2_request)

# 4. 查看对话历史
history_request = ConversationHistoryRequest(
    conversation_id=conversation.conversation_id,
    limit=10,
    offset=0
)
messages = service.get_conversation_history(history_request)

# 5. 更新质量指标
service.update_quality_metrics(
    conversation_id=conversation.conversation_id,
    topic_depth_score=7.5,
    emotion_sync_score=0.85
)

# 6. 结束对话
end_request = ConversationStatusUpdateRequest(
    conversation_id=conversation.conversation_id,
    status="ended"
)
service.update_conversation_status(end_request)
```

### 场景2：沉默检测与AI介入

```python
# 检测到沉默
service.increment_silence_count(conversation.conversation_id)

# AI助手介入
service.increment_ai_intervention_count(conversation.conversation_id)

# 查看统计
conversation = service.get_conversation(conversation.conversation_id)
print(f"沉默次数: {conversation.silence_count}")
print(f"AI介入次数: {conversation.ai_intervention_count}")
```

### 场景3：分页查询历史消息

```python
# 第一页
page1_request = ConversationHistoryRequest(
    conversation_id=conversation.conversation_id,
    limit=20,
    offset=0
)
page1_messages = service.get_conversation_history(page1_request)

# 第二页
page2_request = ConversationHistoryRequest(
    conversation_id=conversation.conversation_id,
    limit=20,
    offset=20
)
page2_messages = service.get_conversation_history(page2_request)
```

## 最佳实践

### 1. 错误处理

始终使用try-except捕获异常：

```python
try:
    message = service.send_message(request)
except ConversationNotFoundError:
    # 对话不存在
    pass
except InvalidConversationStateError:
    # 对话状态不允许发送消息
    pass
except UnauthorizedAccessError:
    # 用户无权访问此对话
    pass
```

### 2. 状态检查

发送消息前检查对话状态：

```python
conversation = service.get_conversation(conversation_id)
if conversation.status == "active":
    service.send_message(request)
else:
    print("对话未处于活跃状态")
```

### 3. 分页查询

处理大量历史消息时使用分页：

```python
limit = 50
offset = 0
all_messages = []

while True:
    request = ConversationHistoryRequest(
        conversation_id=conversation_id,
        limit=limit,
        offset=offset
    )
    messages = service.get_conversation_history(request)
    
    if not messages:
        break
    
    all_messages.extend(messages)
    offset += limit
```

### 4. 质量指标更新

定期更新对话质量指标以便后续分析：

```python
# 在对话过程中定期更新
service.update_quality_metrics(
    conversation_id=conversation_id,
    topic_depth_score=calculate_topic_depth(),
    emotion_sync_score=calculate_emotion_sync()
)

# 对话结束时更新满意度
service.update_quality_metrics(
    conversation_id=conversation_id,
    satisfaction_score=user_satisfaction_rating
)
```

## 性能考虑

### 内存存储

当前实现使用内存存储数据。在生产环境中，应该：

1. 使用MySQL存储对话和消息的结构化数据
2. 使用MongoDB存储消息内容和历史记录
3. 使用Redis缓存热点对话数据

### 查询优化

1. 对话历史查询使用分页，避免一次加载过多数据
2. 使用索引优化数据库查询
3. 缓存频繁访问的对话信息

## 相关需求

本模块实现了以下需求：

- **需求 4.1**: AI对话助手的基础对话管理
- **需求 6.1**: 对话质量监测的实时监测功能
- **需求 6.2**: 对话质量报告生成的数据基础

## 下一步开发

1. 集成数据库持久化
2. 实现消息情感分析
3. 实现沉默自动检测
4. 集成AI对话助手
5. 实现对话质量实时分析

## 运行示例

查看完整的使用示例：

```bash
python examples/conversation_demo.py
```

## 测试

运行测试套件：

```bash
pytest tests/test_conversation_system.py -v
```

测试覆盖：
- 数据模型验证
- 服务功能测试
- 异常处理测试
- 集成场景测试
