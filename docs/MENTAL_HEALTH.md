# 心理健康监测与支持系统

## 概述

心理健康监测与支持系统是青春伴行平台的核心功能之一，旨在通过AI技术实时监测用户的心理健康状况，及时发现潜在风险，并提供相应的支持和资源。

## 核心功能

### 1. 情感分析

系统能够分析用户发送的文本内容，识别情绪类型和强度：

- **情绪类型**：positive（正面）、neutral（中性）、negative（负面）、anxious（焦虑）、depressed（抑郁）
- **情绪强度**：0.0-1.0，数值越高表示情绪越强烈
- **关键词检测**：识别焦虑、抑郁、自杀风险等关键词

### 2. 负面情绪关键词检测

系统维护了一个负面情绪关键词库，包括：

- **焦虑类**：焦虑、紧张、不安、担心、害怕、恐惧、压力大、烦躁
- **抑郁类**：抑郁、沮丧、绝望、无助、痛苦、难过、伤心、失落、孤独、空虚、麻木
- **自杀风险**：自杀、结束生命、不想活、活不下去、想死、了结、解脱
- **自残类**：自残、伤害自己、割伤、烫伤、打自己

### 3. 情绪状态标记

每次情感分析后，系统会创建情绪状态记录，包含：

- 用户ID
- 情绪类型
- 情绪强度
- 检测到的关键词
- 来源消息ID
- 检测时间

### 4. 持续低落情绪监控

系统会追踪用户的情绪历史，计算：

- **连续负面情绪天数**：统计用户连续多少天出现负面情绪
- **情绪稳定性得分**：基于情绪波动和负面情绪占比计算
- **风险等级**：low（低）、medium（中）、high（高）、critical（严重）

**触发条件**：
- 连续3天负面情绪 → 推送心理健康资源
- 连续7天负面情绪 → 创建专业转介
- 检测到自杀风险关键词 → 立即触发严重预警

### 5. 心理健康资源推送

系统内置心理健康资源库，根据用户情绪类型推送相关资源：

**资源类型**：
- **热线**：24小时心理援助热线
- **咨询**：校园心理咨询中心
- **文章**：心理健康科普文章
- **视频**：心理健康教育视频

**推送策略**：
- 按优先级排序
- 每次最多推送3个资源
- 记录推送历史

### 6. 高风险预警机制

当检测到严重心理健康风险时，系统会：

1. **创建风险预警**
   - 记录风险等级（high/critical）
   - 记录预警类型（suicide_risk/severe_depression/self_harm）
   - 记录检测内容和置信度
   - 标记为待处理状态

2. **通知工作人员**
   - 严重风险（critical）立即通知人工客服
   - 记录通知状态

3. **推送紧急资源**
   - 心理危机热线
   - 急救电话
   - 专业心理咨询机构

### 7. 匿名倾诉功能

在心理树洞场景中，用户可以选择匿名模式：

- **匿名ID生成**：系统为用户生成唯一的匿名ID
- **身份隐藏**：对外只显示匿名ID，不显示真实身份
- **会话管理**：支持创建、查询、结束匿名会话
- **隐私保护**：系统内部保留真实用户ID用于监测，但不对外暴露

### 8. 专业资源转介

当用户需要专业心理咨询时，系统提供转介服务：

**转介类型**：
- **counseling**：心理咨询
- **psychiatry**：精神科医疗
- **emergency**：紧急干预

**紧急程度**：
- **low**：建议预约咨询
- **medium**：建议尽快咨询
- **high**：请尽快联系专业机构
- **emergency**：请立即拨打急救电话

**转介流程**：
1. 系统评估用户状况
2. 创建转介记录
3. 提供联系方式和建议
4. 跟踪转介状态

## 数据模型

### EmotionState（情绪状态）

```python
{
    "user_id": "用户ID",
    "emotion_type": "情绪类型",
    "intensity": 0.8,
    "detected_keywords": ["焦虑", "压力大"],
    "source_message_id": "消息ID",
    "timestamp": "2024-01-01T12:00:00"
}
```

### MentalHealthStatus（心理健康状态）

```python
{
    "user_id": "用户ID",
    "risk_level": "风险等级",
    "emotion_stability_score": 0.6,
    "negative_emotion_days": 5,
    "last_negative_emotion_date": "2024-01-01T12:00:00",
    "recent_emotions": [...],
    "updated_at": "2024-01-01T12:00:00"
}
```

### RiskAlert（风险预警）

```python
{
    "alert_id": "预警ID",
    "user_id": "用户ID",
    "risk_level": "critical",
    "alert_type": "suicide_risk",
    "detected_content": "检测到的内容",
    "confidence": 0.9,
    "status": "pending",
    "notified_staff": true,
    "created_at": "2024-01-01T12:00:00"
}
```

## API接口

### 1. 分析情感

```python
request = EmotionAnalysisRequest(
    text="用户文本",
    user_id="user_001",
    message_id="msg_001"
)
emotion = service.analyze_emotion(request)
```

### 2. 检查心理健康

```python
request = MentalHealthCheckRequest(
    user_id="user_001",
    check_recent_days=7
)
status = service.check_mental_health(request)
```

### 3. 推送资源

```python
resources = service.push_mental_health_resources(
    user_id="user_001",
    emotion_type="anxious"
)
```

### 4. 创建风险预警

```python
alert = service.create_risk_alert(
    user_id="user_001",
    alert_type="suicide_risk",
    detected_content="检测内容",
    confidence=0.9
)
```

### 5. 创建匿名会话

```python
session = service.create_anonymous_session(user_id="user_001")
```

### 6. 创建专业转介

```python
referral = service.create_professional_referral(
    user_id="user_001",
    referral_type="counseling",
    reason="持续负面情绪",
    urgency="high"
)
```

### 7. 综合监测

```python
result = service.monitor_and_respond(
    user_id="user_001",
    text="用户文本",
    message_id="msg_001"
)
```

## 使用示例

### 场景1：正常对话监测

```python
service = MentalHealthService()

# 用户发送消息
result = service.monitor_and_respond(
    user_id="user_001",
    text="今天学习了新知识，感觉不错"
)

# 结果：检测到正面情绪，无需特殊处理
```

### 场景2：检测到焦虑情绪

```python
result = service.monitor_and_respond(
    user_id="user_002",
    text="我很焦虑，考试压力太大了"
)

# 结果：
# - 检测到焦虑情绪
# - 推送心理健康资源（热线、文章等）
```

### 场景3：持续负面情绪

```python
# 用户连续7天发送负面消息
for day in range(7):
    service.monitor_and_respond(
        user_id="user_003",
        text="感觉很抑郁，什么都不想做"
    )

# 结果：
# - 推送心理健康资源
# - 创建专业转介
# - 建议联系心理咨询中心
```

### 场景4：检测到自杀风险

```python
result = service.monitor_and_respond(
    user_id="user_004",
    text="我不想活了，太痛苦了"
)

# 结果：
# - 创建严重风险预警（critical）
# - 立即通知人工客服
# - 创建紧急转介
# - 推送紧急资源（危机热线、急救电话）
```

### 场景5：匿名倾诉

```python
# 用户进入心理树洞场景
session = service.create_anonymous_session(user_id="user_005")

# 用户以匿名身份进行对话
# 对外显示：anonymous_abc123
# 系统内部：user_005（用于监测）

# 结束会话
service.end_anonymous_session(session.session_id)
```

## 监测指标

### 情绪稳定性得分计算

```
情绪稳定性 = (1 - 情绪波动方差) × (1 - 负面情绪占比 × 0.5)
```

### 风险等级判定

- **critical（严重）**：检测到自杀风险或自残关键词
- **high（高）**：严重抑郁（强度>0.8）或连续负面情绪≥7天
- **medium（中）**：连续负面情绪≥3天或情绪稳定性<0.4
- **low（低）**：其他情况

## 隐私保护

1. **数据加密**：敏感数据使用AES-256加密存储
2. **匿名模式**：心理树洞场景支持完全匿名
3. **访问控制**：严格的权限管理，只有授权人员可查看预警
4. **数据保留**：情绪记录只保留30天
5. **用户同意**：专业转介需要用户明确同意

## 注意事项

1. **AI辅助，非替代**：系统提供辅助监测，不能替代专业心理咨询
2. **及时干预**：严重风险必须立即通知人工客服
3. **尊重隐私**：在提供帮助的同时保护用户隐私
4. **持续优化**：根据反馈不断优化关键词库和算法
5. **多重保障**：建立多层次的心理健康支持体系

## 未来改进

1. **深度学习模型**：集成更先进的情感分析模型
2. **多模态分析**：支持语音、图片等多种输入
3. **个性化资源**：根据用户特征推荐个性化资源
4. **预测模型**：预测用户心理健康趋势
5. **社区支持**：建立用户互助社区
