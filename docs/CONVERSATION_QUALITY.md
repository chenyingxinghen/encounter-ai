# 对话质量监测系统

## 概述

对话质量监测系统是青春伴行平台的核心功能之一，负责实时监测对话质量、生成质量报告、收集用户反馈，并为低质量对话提供改进建议。

## 功能特性

### 1. 实时质量监测

系统能够实时监测对话的多个维度：

- **话题深度分析**：评估对话的深度和广度
- **回应一致性分析**：评估对话的流畅性和互动平衡性
- **情感同步性分析**：评估对话双方的情感共鸣程度

### 2. 质量报告生成

系统为每个对话生成详细的质量报告，包括：

- 对话基本信息（时长、消息数量等）
- 多维度质量指标
- 用户满意度反馈
- 个性化改进建议

### 3. 满意度反馈收集

系统支持收集用户的满意度反馈：

- 5分制满意度评分
- 文字反馈
- 预定义标签（话题有趣、聊得投机、对方友善等）

### 4. 低质量对话检测

系统能够自动检测低质量对话并提供建议：

- 识别话题深度不足
- 识别回应不一致
- 识别情感不同步
- 提供针对性改进建议

## 核心组件

### ConversationQualityService

对话质量监测服务的核心类，提供以下主要方法：

#### monitor_conversation_quality(request)

实时监测对话质量，返回质量指标。

**参数：**
- `request`: QualityMonitoringRequest - 质量监测请求

**返回：**
- `QualityMetrics` - 质量指标对象

**示例：**
```python
from src.services.conversation_quality_service import ConversationQualityService
from src.models.quality import QualityMonitoringRequest

quality_service = ConversationQualityService(conversation_service)

request = QualityMonitoringRequest(conversation_id="conv_123")
metrics = quality_service.monitor_conversation_quality(request)

print(f"整体质量得分: {metrics.overall_quality_score}/10")
print(f"话题深度得分: {metrics.topic_depth_score}/10")
print(f"情感同步性得分: {metrics.emotion_sync_score}")
```

#### generate_conversation_report(conversation_id)

生成对话质量报告。

**参数：**
- `conversation_id`: str - 对话ID

**返回：**
- `ConversationReport` - 对话质量报告

**示例：**
```python
report = quality_service.generate_conversation_report("conv_123")

print(f"对话时长: {report.duration_seconds}秒")
print(f"消息总数: {report.message_count}")
print(f"用户A满意度: {report.user_a_satisfaction}/5")
print(f"是否低质量对话: {report.is_low_quality}")
```

#### collect_satisfaction_feedback(request)

收集用户满意度反馈。

**参数：**
- `request`: SatisfactionFeedbackRequest - 满意度反馈请求

**返回：**
- `SatisfactionFeedback` - 满意度反馈对象

**示例：**
```python
from src.models.quality import SatisfactionFeedbackRequest

feedback_request = SatisfactionFeedbackRequest(
    conversation_id="conv_123",
    user_id="user_001",
    satisfaction_score=4.5,
    feedback_text="聊得很开心！",
    feedback_tags=["话题有趣", "聊得投机"]
)

feedback = quality_service.collect_satisfaction_feedback(feedback_request)
```

#### detect_low_quality_conversation(conversation_id)

检测低质量对话并提供建议。

**参数：**
- `conversation_id`: str - 对话ID

**返回：**
- `Tuple[bool, List[str]]` - (是否为低质量对话, 建议列表)

**示例：**
```python
is_low_quality, suggestions = quality_service.detect_low_quality_conversation("conv_123")

if is_low_quality:
    print("检测到低质量对话")
    print("改进建议:")
    for suggestion in suggestions:
        print(f"  - {suggestion}")
```

## 数据模型

### QualityMetrics

质量指标模型，包含以下字段：

- `conversation_id`: 对话ID
- `topic_depth_score`: 话题深度得分 (0-10)
- `topic_count`: 话题数量
- `average_topic_duration`: 平均话题持续时间
- `response_consistency_score`: 回应一致性得分 (0-1)
- `average_response_time`: 平均回应时间（秒）
- `response_length_variance`: 回应长度方差
- `emotion_sync_score`: 情感同步性得分 (0-1)
- `emotion_alignment_rate`: 情绪一致率 (0-1)
- `overall_quality_score`: 整体质量得分 (0-10)

### ConversationReport

对话质量报告模型，包含以下字段：

- `report_id`: 报告ID
- `conversation_id`: 对话ID
- `user_a_id`: 用户A的ID
- `user_b_id`: 用户B的ID
- `scene`: 对话场景
- `started_at`: 开始时间
- `ended_at`: 结束时间
- `duration_seconds`: 对话时长（秒）
- `message_count`: 消息总数
- `metrics`: 质量指标
- `user_a_satisfaction`: 用户A满意度 (0-5)
- `user_b_satisfaction`: 用户B满意度 (0-5)
- `suggestions`: 改进建议列表
- `is_low_quality`: 是否为低质量对话

### SatisfactionFeedback

满意度反馈模型，包含以下字段：

- `feedback_id`: 反馈ID
- `conversation_id`: 对话ID
- `user_id`: 用户ID
- `satisfaction_score`: 满意度得分 (0-5)
- `feedback_text`: 文字反馈
- `feedback_tags`: 反馈标签列表

## 质量评估算法

### 话题深度分析

话题深度分析通过以下步骤进行：

1. **话题分割**：根据关键词相似度将对话分割成多个话题片段
2. **深度评分**：为每个话题片段计算深度得分，考虑：
   - 消息长度（更长的消息表示更深入的讨论）
   - 消息数量（更多的消息表示持续的讨论）
   - 词汇多样性（更多样的词汇表示更丰富的内容）
3. **综合评分**：结合平均深度和话题多样性计算最终得分

### 回应一致性分析

回应一致性分析评估对话的流畅性：

1. **回应时间一致性**：回应时间越稳定越好
2. **回应长度一致性**：消息长度越稳定越好
3. **交互平衡性**：双方消息数量应该相对平衡

### 情感同步性分析

情感同步性分析评估对话双方的情感共鸣：

1. **情感识别**：使用关键词识别消息的情感（积极、消极、焦虑、中性）
2. **情感匹配**：计算相邻消息的情感一致性
3. **同步评分**：基于情感一致率计算同步性得分

## 质量阈值

系统使用以下阈值判断对话质量：

- **低质量阈值**：整体质量得分 < 5.0
- **最小消息数**：至少10条消息才进行完整分析

## 改进建议生成

系统根据质量指标自动生成个性化建议：

### 话题深度建议

- 话题深度 < 5.0：建议深入探讨话题，分享更多细节
- 话题数量 < 3：建议探索更多不同话题

### 回应一致性建议

- 回应一致性 < 0.5：建议保持稳定的回应节奏
- 平均回应时间 > 60秒：建议及时回复消息

### 情感同步性建议

- 情感同步性 < 0.5：建议关注对方情绪，给予情感回应

### 场景特定建议

- **考研自习室**：建议分享学习方法和备考经验
- **心理树洞**：建议给予情感支持和共情

## 使用场景

### 场景1：实时监测对话质量

在对话进行过程中，系统可以实时监测质量指标，帮助用户了解当前对话状态。

### 场景2：对话结束后生成报告

对话结束后，系统生成详细的质量报告，帮助用户回顾对话效果。

### 场景3：收集用户反馈

对话结束后，系统收集用户的满意度反馈，用于优化匹配算法。

### 场景4：检测低质量对话

系统自动检测低质量对话，并建议用户尝试其他匹配对象。

## 最佳实践

1. **定期监测**：建议每隔一定消息数量（如10条）监测一次质量
2. **及时反馈**：鼓励用户在对话结束后及时提供满意度反馈
3. **关注建议**：用户应该关注系统提供的改进建议，提升社交能力
4. **场景适配**：不同场景的质量标准可能不同，应该灵活调整

## 性能考虑

- 质量分析是计算密集型操作，建议异步执行
- 对于长对话（>100条消息），可以只分析最近的消息
- 质量报告可以缓存，避免重复计算

## 未来改进

1. **机器学习模型**：使用深度学习模型进行更准确的质量评估
2. **个性化阈值**：根据用户历史数据调整质量阈值
3. **实时建议**：在对话过程中实时提供改进建议
4. **多模态分析**：支持语音、图片等多模态内容的质量分析

## 相关文档

- [对话系统文档](CONVERSATION_SYSTEM.md)
- [AI对话助手文档](DIALOGUE_ASSISTANT.md)
- [用户画像更新文档](PROFILE_UPDATE.md)

## 示例代码

完整的使用示例请参考：`examples/conversation_quality_demo.py`

## 测试

运行测试：

```bash
python -m pytest tests/test_conversation_quality.py -v
```

## 需求映射

本功能实现了以下需求：

- **需求 6.1**：实时监测话题深度、回应一致性和情感同步性
- **需求 6.2**：生成对话质量报告
- **需求 6.3**：展示报告并收集满意度反馈
- **需求 6.4**：将反馈数据用于优化匹配算法
- **需求 6.5**：检测低质量对话并提供建议
