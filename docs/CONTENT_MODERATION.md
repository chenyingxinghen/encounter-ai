# 内容审查与监管系统

## 概述

内容审查与监管系统是青春伴行平台的重要安全保障模块，负责实时审查用户发送的消息内容，检测和处理违规行为，维护健康的社交环境。

## 核心功能

### 1. 消息实时审查

系统对用户发送的每条消息进行实时审查，检测是否包含违规内容：

- **暴力内容**：包含暴力、攻击、伤害等关键词
- **色情内容**：包含色情、淫秽等不当内容
- **骚扰内容**：包含侮辱、威胁、人身攻击等
- **垃圾信息**：包含广告、推广、刷单等
- **政治敏感**：包含政治敏感词汇

### 2. 违规内容分级处理

根据违规内容的严重程度和置信度，系统采取不同的处理措施：

- **允许通过** (allow)：正常内容，直接发送
- **拦截** (block)：高置信度违规，直接拦截并通知用户
- **人工审核** (review)：中等置信度，标记为待审核

### 3. 用户举报功能

用户可以举报其他用户的不当行为：

- **举报类型**：骚扰、不当内容、虚假资料等
- **证据提交**：可以提交相关消息ID或截图
- **审查流程**：系统自动启动审查流程

### 4. 累计违规统计

系统记录每个用户的违规历史：

- 违规次数统计
- 违规类型分布
- 违规严重程度
- 处罚记录

### 5. 自动处罚机制

根据用户累计违规次数，系统自动施加相应处罚：

- **第1次违规**：警告 (warning)
- **第3次违规**：禁言1天 (mute)
- **第5次违规**：暂停7天 (suspend)
- **第10次违规**：永久封号 (ban)

### 6. 用户申诉功能

用户可以对违规判定提出申诉：

- 提交申诉理由
- 人工复核
- 状态更新

## 数据模型

### ModerationResult（审查结果）

```python
@dataclass
class ModerationResult:
    content_id: str              # 内容ID
    is_approved: bool            # 是否通过审查
    violation_types: List[str]   # 违规类型列表
    confidence_score: float      # 置信度 (0-1)
    flagged_keywords: List[str]  # 触发的关键词
    action: str                  # 处理动作: "allow", "block", "review"
    reviewed_at: datetime        # 审查时间
```

### Violation（违规记录）

```python
@dataclass
class Violation:
    violation_id: str        # 违规记录ID
    user_id: str            # 违规用户ID
    content_id: str         # 违规内容ID
    violation_type: str     # 违规类型
    severity: str           # 严重程度: "low", "medium", "high", "critical"
    content_snapshot: str   # 违规内容快照
    detected_at: datetime   # 检测时间
    reviewed_by: str        # 审核人员ID
    status: str            # 状态: "pending", "confirmed", "dismissed", "appealed"
```

### UserReport（用户举报）

```python
@dataclass
class UserReport:
    report_id: str          # 举报ID
    reporter_id: str        # 举报人ID
    reported_id: str        # 被举报人ID
    report_type: str        # 举报类型
    reason: str            # 举报原因
    evidence: List[str]    # 证据列表
    status: str           # 状态: "pending", "investigating", "resolved", "rejected"
    created_at: datetime  # 举报时间
    resolved_at: datetime # 处理时间
    resolution: str       # 处理结果
```

### Penalty（处罚记录）

```python
@dataclass
class Penalty:
    penalty_id: str       # 处罚ID
    user_id: str         # 被处罚用户ID
    violation_id: str    # 关联的违规记录ID
    penalty_type: str    # 处罚类型: "warning", "mute", "suspend", "ban"
    duration: int        # 处罚时长（秒），-1表示永久
    reason: str         # 处罚原因
    applied_at: datetime # 处罚时间
    expires_at: datetime # 过期时间
    status: str         # 状态: "active", "expired", "revoked"
```

## 服务接口

### ContentModerationService

#### moderate_message()

审查消息内容

```python
def moderate_message(
    message: str,
    user_id: str,
    message_id: Optional[str] = None
) -> ModerationResult
```

**参数：**
- `message`: 消息内容
- `user_id`: 用户ID
- `message_id`: 消息ID（可选）

**返回：**
- `ModerationResult`: 审查结果

#### detect_violation()

检测违规内容类型

```python
def detect_violation(content: str) -> List[str]
```

**参数：**
- `content`: 内容文本

**返回：**
- `List[str]`: 违规类型列表

#### handle_user_report()

处理用户举报

```python
def handle_user_report(
    reporter_id: str,
    reported_id: str,
    report_type: str,
    reason: str,
    evidence: List[str]
) -> UserReport
```

**参数：**
- `reporter_id`: 举报人ID
- `reported_id`: 被举报人ID
- `report_type`: 举报类型
- `reason`: 举报原因
- `evidence`: 证据列表

**返回：**
- `UserReport`: 举报记录

#### review_flagged_content()

审核标记的内容

```python
def review_flagged_content(
    content_id: str,
    reviewer_id: str,
    decision: str
) -> None
```

**参数：**
- `content_id`: 内容ID
- `reviewer_id`: 审核人员ID
- `decision`: 审核决定 ("confirm", "dismiss")

#### get_user_violation_history()

获取用户违规历史

```python
def get_user_violation_history(user_id: str) -> List[Violation]
```

**参数：**
- `user_id`: 用户ID

**返回：**
- `List[Violation]`: 违规记录列表

#### apply_penalty()

施加处罚

```python
def apply_penalty(
    user_id: str,
    violation_id: str,
    penalty_type: Optional[str] = None
) -> Penalty
```

**参数：**
- `user_id`: 用户ID
- `violation_id`: 违规记录ID
- `penalty_type`: 处罚类型（可选，自动根据违规次数确定）

**返回：**
- `Penalty`: 处罚记录

#### is_user_penalized()

检查用户是否正在被处罚

```python
def is_user_penalized(user_id: str) -> bool
```

**参数：**
- `user_id`: 用户ID

**返回：**
- `bool`: 是否被处罚

#### handle_appeal()

处理用户申诉

```python
def handle_appeal(
    user_id: str,
    violation_id: str,
    appeal_reason: str
) -> bool
```

**参数：**
- `user_id`: 用户ID
- `violation_id`: 违规记录ID
- `appeal_reason`: 申诉原因

**返回：**
- `bool`: 是否接受申诉

#### get_moderation_stats()

获取审查统计数据

```python
def get_moderation_stats() -> Dict
```

**返回：**
- `Dict`: 统计数据，包含：
  - `total_violations`: 总违规数
  - `total_reports`: 总举报数
  - `total_penalties`: 总处罚数
  - `violations_by_type`: 按类型统计的违规
  - `penalties_by_type`: 按类型统计的处罚
  - `users_with_violations`: 违规用户数

## 使用示例

### 1. 审查消息

```python
from src.services.content_moderation_service import ContentModerationService

service = ContentModerationService()

# 审查消息
message = "你好，很高兴认识你！"
result = service.moderate_message(message, "user1")

if result.is_approved:
    print("消息通过审查")
else:
    print(f"消息被{result.action}: {result.violation_types}")
```

### 2. 处理用户举报

```python
# 用户举报
report = service.handle_user_report(
    reporter_id="user1",
    reported_id="user2",
    report_type="harassment",
    reason="该用户持续骚扰我",
    evidence=["msg1", "msg2"]
)

print(f"举报已提交，状态: {report.status}")
```

### 3. 查看违规历史

```python
# 获取用户违规历史
violations = service.get_user_violation_history("user1")

for v in violations:
    print(f"违规类型: {v.violation_type}, 严重程度: {v.severity}")
```

### 4. 检查处罚状态

```python
# 检查用户是否被处罚
if service.is_user_penalized("user1"):
    print("用户当前被处罚中")
    penalties = service.get_user_penalties("user1")
    for p in penalties:
        print(f"处罚类型: {p.penalty_type}, 剩余时长: {p.duration}秒")
```

### 5. 提交申诉

```python
# 用户申诉
violations = service.get_user_violation_history("user1")
if violations:
    result = service.handle_appeal(
        "user1",
        violations[0].violation_id,
        "这是误判，我没有违规"
    )
    print(f"申诉{'成功' if result else '失败'}")
```

## 工作流程

### 消息审查流程

```
用户发送消息
    ↓
实时内容审查
    ↓
关键词匹配检测
    ↓
计算置信度
    ↓
判断处理动作
    ├─ 允许：直接发送
    ├─ 拦截：阻止发送，通知用户
    └─ 审核：标记待审核
        ↓
    人工审核
        ├─ 确认违规：记录违规，可能触发处罚
        └─ 驳回：恢复正常
```

### 自动处罚流程

```
检测到违规
    ↓
记录违规
    ↓
累计违规次数+1
    ↓
检查违规阈值
    ├─ 第1次：警告
    ├─ 第3次：禁言1天
    ├─ 第5次：暂停7天
    └─ 第10次：永久封号
        ↓
    施加处罚
        ↓
    通知用户
```

### 用户举报流程

```
用户提交举报
    ↓
记录举报信息
    ↓
启动审查流程
    ↓
状态更新为"调查中"
    ↓
人工审核
    ├─ 确认违规：处罚被举报用户
    └─ 驳回举报：通知举报人
        ↓
    更新举报状态
        ↓
    通知相关用户
```

## 配置说明

### 违规阈值配置

```python
violation_thresholds = {
    "warning": 1,   # 第1次违规：警告
    "mute": 3,      # 第3次违规：禁言
    "suspend": 5,   # 第5次违规：暂停
    "ban": 10       # 第10次违规：封号
}
```

### 处罚时长配置

```python
penalty_durations = {
    "warning": 0,           # 警告无时长
    "mute": 86400,          # 禁言1天
    "suspend": 604800,      # 暂停7天
    "ban": -1               # 永久封号
}
```

## 注意事项

1. **关键词库维护**：定期更新违规关键词库，提高检测准确率
2. **误报处理**：建立人工审核机制，及时处理误报
3. **申诉响应**：及时响应用户申诉，维护用户体验
4. **数据隐私**：违规内容快照仅保存必要信息，保护用户隐私
5. **处罚公平**：确保处罚机制公平透明，避免滥用

## 未来优化方向

1. **AI模型集成**：集成更先进的内容审查AI模型，提高检测准确率
2. **多语言支持**：支持多语言内容审查
3. **上下文分析**：考虑对话上下文，减少误报
4. **实时监控**：建立实时监控面板，及时发现异常
5. **自动学习**：基于人工审核结果，持续优化检测算法
