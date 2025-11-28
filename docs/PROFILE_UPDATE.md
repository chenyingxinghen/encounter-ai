# 用户画像动态更新系统

## 概述

用户画像动态更新系统是青春伴行平台的核心功能之一，负责根据用户的对话内容和行为模式持续优化用户画像，从而提供更精准的匹配服务。

## 功能特性

### 1. 对话内容分析

系统能够自动分析用户的对话内容，提取以下关键信息：

- **话题识别**：识别对话中讨论的主要话题
- **情绪分析**：分析用户在对话中表现的情绪状态（积极、消极、焦虑、中性）
- **兴趣提取**：从对话内容中提取用户的兴趣点

### 2. 关键信息提取

系统使用关键词匹配和语义分析技术，从对话中提取：

- **学业兴趣**：考研、学习、课程、论文等
- **职业兴趣**：工作、实习、求职、面试等
- **兴趣爱好**：电影、音乐、运动、游戏等

### 3. 兴趣标签自动更新

根据对话内容自动更新用户的兴趣标签：

- 新发现的兴趣会自动添加到用户画像
- 兴趣按类别分类（学业、职业、爱好）
- 避免重复添加已有的兴趣

### 4. 情感特征更新

动态调整用户的情感特征：

- **情绪稳定性**：根据负面和焦虑情绪的比例计算
- **社交能量**：根据积极情绪的比例计算
- 使用指数移动平均平滑更新，避免剧烈波动

### 5. 匹配度重新计算触发

当用户画像发生显著变化时：

- 自动触发匹配度重新计算
- 为用户当前关注的所有场景重新查找匹配对象
- 确保推荐的匹配对象始终是最合适的

### 6. 画像更新通知

当画像变化达到阈值（默认15%）时：

- 生成画像更新通知
- 告知用户画像的主要变化
- 提供查看详细画像的入口

### 7. 行为模式分析

根据用户的行为模式动态调整人格特质：

- **情绪波动** → 影响神经质维度
- **互动友好度** → 影响宜人性维度
- **社交活跃度** → 影响外向性维度
- **话题多样性** → 影响开放性维度
- **回复及时性** → 影响尽责性维度

## 技术实现

### 核心类

#### ProfileUpdateService

主要服务类，提供以下方法：

```python
class ProfileUpdateService:
    def analyze_conversation(conversation_id, messages) -> Dict
    def update_profile_from_conversation(user_id, conversation_data) -> Dict
    def update_personality_from_behavior(user_id, behavior_data) -> BigFiveScores
    def generate_profile_update_notification(user_id, update_result) -> Dict
```

### 数据流

```
对话消息
    ↓
analyze_conversation() - 分析对话内容
    ↓
提取话题、情绪、兴趣
    ↓
update_profile_from_conversation() - 更新画像
    ↓
更新兴趣标签、情感特征
    ↓
计算画像变化程度
    ↓
是否达到通知阈值？
    ↓ 是
触发匹配度重新计算
    ↓
生成画像更新通知
```

### 算法说明

#### 情绪分析算法

使用关键词匹配方法：

```python
EMOTION_KEYWORDS = {
    'positive': ['开心', '高兴', '快乐', '兴奋', ...],
    'negative': ['难过', '伤心', '失望', '沮丧', ...],
    'anxious': ['焦虑', '紧张', '担心', '害怕', ...],
    'neutral': ['还行', '一般', '普通', ...]
}
```

#### 情感特征更新算法

使用指数移动平均（EMA）：

```python
# 情绪稳定性
new_instability = (negative_ratio + anxious_ratio) / 2
new_stability = 1.0 - new_instability
updated_stability = alpha * new_stability + (1 - alpha) * current_stability

# 社交能量
new_energy = positive_ratio
updated_energy = alpha * new_energy + (1 - alpha) * current_energy
```

其中 `alpha = 0.3` 为平滑系数。

#### 画像变化计算

综合考虑多个维度的变化：

```python
change_magnitude = (
    emotion_stability_change +
    social_energy_change +
    interest_count_change +
    big_five_change
) / 4
```

## 使用示例

### 基本使用

```python
from src.services.profile_update_service import ProfileUpdateService
from src.services.user_profile_service import UserProfileService
from src.services.matching_service import MatchingService

# 初始化服务
user_profile_service = UserProfileService()
matching_service = MatchingService(user_profile_service=user_profile_service)
profile_update_service = ProfileUpdateService(
    user_profile_service=user_profile_service,
    matching_service=matching_service
)

# 分析对话
conversation_data = profile_update_service.analyze_conversation(
    conversation_id="conv_123",
    messages=messages
)

# 更新画像
update_result = profile_update_service.update_profile_from_conversation(
    user_id="user_123",
    conversation_data=conversation_data
)

# 生成通知
if update_result['should_notify']:
    notification = profile_update_service.generate_profile_update_notification(
        user_id="user_123",
        update_result=update_result
    )
```

### 行为模式更新

```python
# 准备行为数据
behavior_data = {
    'emotion_volatility': 0.3,
    'interaction_friendliness': 0.8,
    'social_activity': 0.7,
    'topic_diversity': 0.6,
    'response_timeliness': 0.9
}

# 更新人格特质
updated_scores = profile_update_service.update_personality_from_behavior(
    user_id="user_123",
    behavior_data=behavior_data
)
```

## 配置参数

### 更新阈值

```python
UPDATE_THRESHOLD = 0.15  # 画像变化超过15%时通知用户
```

### 平滑系数

```python
alpha = 0.3  # 情感特征更新的平滑系数
alpha = 0.2  # 人格特质更新的平滑系数
```

## 性能优化

1. **批量处理**：对话结束后批量分析，而非实时分析每条消息
2. **缓存机制**：缓存画像快照，避免重复计算
3. **异步更新**：匹配度重新计算可以异步执行
4. **增量更新**：只更新变化的部分，而非重新计算整个画像

## 测试

运行测试：

```bash
python -m pytest tests/test_profile_update.py -v
```

运行演示：

```bash
python examples/profile_update_demo.py
```

## 验证需求

该实现满足以下需求：

- **需求 5.1**：对话完成后分析内容并提取关键信息 ✓
- **需求 5.2**：更新用户画像中的兴趣标签和情感特征 ✓
- **需求 5.3**：画像更新后重新计算匹配度 ✓
- **需求 5.4**：根据行为模式动态调整人格特质评分 ✓
- **需求 5.5**：画像更新达到阈值时通知用户 ✓

## 未来改进

1. **深度学习模型**：使用BERT等模型进行更精确的语义分析
2. **情感强度分析**：不仅识别情绪类型，还分析情绪强度
3. **长期趋势分析**：跟踪用户画像的长期变化趋势
4. **个性化阈值**：根据用户特点动态调整通知阈值
5. **多模态分析**：结合文本、语音、图片等多种信息源

## 相关文档

- [用户画像服务](./USER_PROFILE.md)
- [匹配系统](./MATCHING_SYSTEM.md)
- [对话系统](./CONVERSATION_SYSTEM.md)
