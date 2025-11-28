# 虚拟用户库与冷启动系统

## 概述

虚拟用户库与冷启动系统是青春伴行平台的重要组成部分，用于解决平台初期用户量不足的问题。通过生成基于MBTI类型的多样化虚拟用户，确保每个真实用户都能找到合适的交流对象，提升用户体验。

## 核心功能

### 1. 虚拟用户生成

系统能够自动生成具有以下特征的虚拟用户：

- **完整的用户画像**：包括MBTI类型、大五人格得分、兴趣标签、场景偏好等
- **多样化背景**：覆盖不同学校、专业、年级
- **MBTI类型覆盖**：确保16种MBTI类型都有代表
- **个性化特征**：每个虚拟用户都有独特的对话风格和行为特征

### 2. 虚拟用户身份标识

虚拟用户具有明确的身份标识：

- **用户名标识**：用户名包含"AI伙伴"标签
- **用户ID前缀**：用户ID以"virtual_"开头
- **is_virtual标志**：数据模型中明确标记为虚拟用户
- **透明展示**：在匹配结果中明确显示虚拟用户身份

### 3. 对话行为模拟

虚拟用户能够模拟符合其人格类型的对话行为：

- **回复速度**：根据MBTI类型设置不同的回复速度范围
  - 外向型(E)：5-20秒
  - 内向型(I)：15-40秒

- **消息长度**：根据人格特征设置消息长度范围
  - 思考型(T)/判断型(J)：50-200字符
  - 其他类型：30-150字符

- **回复风格**：每种MBTI类型都有独特的回复风格
  - INTJ：简洁理性，注重逻辑和效率
  - ENFP：热情开放，充满创意和想象
  - ISFJ：温暖体贴，关心他人需求
  - 等等...

### 4. 匹配权重动态调整

系统根据真实用户数量自动调整虚拟用户的匹配权重：

| 真实用户数量 | 虚拟用户权重 | 说明 |
|------------|------------|------|
| < 1,000 | 1.0 | 完全参与匹配 |
| 1,000 - 10,000 | 线性递减 | 逐步减少推送 |
| ≥ 10,000 | 0.0 | 停止主动推送 |

权重计算公式：
```
weight = 1.0 - (real_user_count - 1000) / 9000  (当1000 ≤ count < 10000时)
```

### 5. 真实用户数量监控

系统持续监控真实用户数量，并自动触发权重调整：

- 实时统计真实用户总数
- 自动更新虚拟用户匹配权重
- 记录权重调整日志
- 提供统计数据查询接口

## 数据模型

### VirtualUser（虚拟用户）

```python
class VirtualUser:
    user_id: str                    # 虚拟用户ID（以"virtual_"开头）
    username: str                   # 用户名（包含"AI伙伴"标识）
    is_virtual: bool                # 虚拟用户标志（True）
    school: str                     # 学校
    major: str                      # 专业
    grade: int                      # 年级
    mbti_type: str                  # MBTI类型
    response_style: str             # 回复风格描述
    response_speed_range: tuple     # 回复速度范围（秒）
    message_length_range: tuple     # 消息长度范围（字符数）
    match_weight: float             # 匹配权重（0.0-1.0）
    created_at: datetime            # 创建时间
    last_active: datetime           # 最后活跃时间
```

### VirtualUserStats（统计信息）

```python
class VirtualUserStats:
    total_virtual_users: int        # 虚拟用户总数
    total_real_users: int           # 真实用户总数
    virtual_user_weight: float      # 当前虚拟用户权重
    mbti_distribution: dict         # MBTI类型分布
    active_virtual_users: int       # 活跃虚拟用户数
    timestamp: datetime             # 统计时间
```

## API接口

### 初始化虚拟用户库

```python
service = VirtualUserService()
config = VirtualUserGenerationConfig(total_count=100)
virtual_users = service.initialize_virtual_users(config)
```

### 获取虚拟用户信息

```python
# 获取单个虚拟用户
virtual_user = service.get_virtual_user(user_id)

# 获取虚拟用户画像
profile = service.get_virtual_profile(user_id)

# 判断是否为虚拟用户
is_virtual = service.is_virtual_user(user_id)
```

### 模拟对话行为

```python
response_data = service.simulate_response(
    virtual_user_id=user_id,
    message="你好，最近在准备考研吗？",
    context={"scene": "考研自习室"}
)

# 返回数据包含：
# - response_delay: 预计回复延迟
# - expected_length: 预期消息长度
# - response_style: 回复风格
# - response_hint: 回复提示
```

### 更新真实用户数量

```python
# 更新真实用户数量，自动触发权重调整
service.update_real_user_count(5000)
```

### 获取统计信息

```python
stats = service.get_statistics()
print(f"虚拟用户总数: {stats.total_virtual_users}")
print(f"真实用户总数: {stats.total_real_users}")
print(f"当前权重: {stats.virtual_user_weight}")
print(f"活跃虚拟用户: {stats.active_virtual_users}")
```

## 使用示例

### 完整的冷启动流程

```python
from src.services.virtual_user_service import VirtualUserService
from src.models.virtual_user import VirtualUserGenerationConfig

# 1. 创建服务实例
service = VirtualUserService()

# 2. 初始化虚拟用户库（生成100个虚拟用户）
config = VirtualUserGenerationConfig(total_count=100)
virtual_users = service.initialize_virtual_users(config)

# 3. 验证MBTI类型覆盖
stats = service.get_statistics()
print(f"MBTI类型分布: {stats.mbti_distribution}")

# 4. 获取虚拟用户进行匹配
active_virtual_users = service.get_active_virtual_users()
for vu in active_virtual_users:
    if vu.match_weight > 0:
        # 将虚拟用户加入匹配池
        pass

# 5. 随着真实用户增长，动态调整权重
service.update_real_user_count(500)   # 权重保持1.0
service.update_real_user_count(5000)  # 权重降至约0.56
service.update_real_user_count(10000) # 权重降至0.0
```

### 虚拟用户对话模拟

```python
# 获取虚拟用户
virtual_user = service.get_virtual_user(user_id)

# 模拟收到消息后的回复行为
response_data = service.simulate_response(
    virtual_user_id=virtual_user.user_id,
    message="你对人工智能感兴趣吗？",
    context={"scene": "兴趣社群"}
)

# 根据回复数据生成实际回复
# - 延迟response_data['response_delay']秒后回复
# - 生成长度约为response_data['expected_length']的消息
# - 风格符合response_data['response_hint']的描述
```

## MBTI类型与人格特征映射

系统为每种MBTI类型预设了相应的大五人格特征：

| MBTI | 外向性 | 开放性 | 尽责性 | 宜人性 | 神经质 | 回复风格 |
|------|-------|-------|-------|-------|-------|---------|
| INTJ | 0.2 | 0.8 | 0.8 | 0.4 | 0.3 | 简洁理性，注重逻辑和效率 |
| ENFP | 0.9 | 0.9 | 0.4 | 0.8 | 0.4 | 热情开放，充满创意和想象 |
| ISTJ | 0.2 | 0.3 | 0.9 | 0.6 | 0.3 | 务实可靠，注重细节和规则 |
| ESFP | 0.9 | 0.7 | 0.4 | 0.8 | 0.3 | 活泼外向，享受社交和娱乐 |
| ... | ... | ... | ... | ... | ... | ... |

*注：实际生成时会在基础值上添加±0.1的随机波动，增加多样性*

## 技术实现

### 虚拟用户生成算法

1. **均匀分布**：确保每种MBTI类型都有足够的代表
2. **随机化**：学校、专业、年级随机选择
3. **人格映射**：根据MBTI类型设置大五人格基础值
4. **多样化处理**：添加随机波动避免千篇一律
5. **画像生成**：自动生成完整的用户画像

### 权重调整机制

```python
def _adjust_virtual_user_weights(self):
    if self._real_user_count < 1000:
        new_weight = 1.0
    elif self._real_user_count < 10000:
        new_weight = 1.0 - (self._real_user_count - 1000) / 9000
    else:
        new_weight = 0.0
    
    for virtual_user in self._virtual_users.values():
        virtual_user.match_weight = new_weight
```

### 对话行为模拟

```python
def simulate_response(self, virtual_user_id, message, context):
    virtual_user = self.get_virtual_user(virtual_user_id)
    
    # 模拟回复延迟
    response_delay = random.uniform(*virtual_user.response_speed_range)
    
    # 模拟消息长度
    message_length = random.randint(*virtual_user.message_length_range)
    
    # 生成回复提示
    response_hint = self._generate_response_hint(virtual_user, message, context)
    
    return {
        'response_delay': response_delay,
        'expected_length': message_length,
        'response_style': virtual_user.response_style,
        'response_hint': response_hint
    }
```

## 最佳实践

### 1. 初始化时机

- 在平台启动时立即初始化虚拟用户库
- 确保在第一个真实用户注册前完成初始化

### 2. 权重更新频率

- 每次有新用户注册时更新真实用户计数
- 批量更新以减少计算开销
- 定期（如每小时）同步真实用户数量

### 3. 虚拟用户数量

- 建议初始生成100-200个虚拟用户
- 确保每种MBTI类型至少有5-10个代表
- 根据平台规模调整虚拟用户总数

### 4. 透明度原则

- 始终明确标识虚拟用户身份
- 在匹配结果中显示"AI伙伴"标签
- 在用户协议中说明虚拟用户的存在和作用

### 5. 逐步退出

- 不要突然停止所有虚拟用户
- 使用线性递减确保平滑过渡
- 保留虚拟用户作为备选（权重为0但仍可用）

## 监控与维护

### 关键指标

- 虚拟用户总数
- 活跃虚拟用户数
- 真实用户数量
- 当前匹配权重
- MBTI类型分布
- 虚拟用户参与的对话数

### 日志记录

系统会记录以下事件：

- 虚拟用户库初始化
- 真实用户数量更新
- 权重调整
- 虚拟用户匹配
- 虚拟用户对话

### 性能优化

- 使用缓存存储虚拟用户数据
- 批量生成虚拟用户
- 异步更新权重
- 定期清理不活跃的虚拟用户

## 注意事项

1. **隐私保护**：虚拟用户不应收集或存储真实用户的敏感信息
2. **行为真实性**：虚拟用户的对话行为应尽可能自然，避免被识破
3. **伦理考量**：明确告知用户虚拟用户的存在，保持透明度
4. **质量控制**：定期审查虚拟用户的对话质量，避免不当内容
5. **退出策略**：当真实用户足够多时，逐步减少虚拟用户的参与

## 未来改进

- [ ] 基于真实用户反馈优化虚拟用户行为
- [ ] 使用更先进的LLM生成更自然的对话
- [ ] 实现虚拟用户的"学习"能力
- [ ] 支持更细粒度的权重调整策略
- [ ] 添加虚拟用户行为分析和优化工具
