# 成长追踪与报告系统

## 概述

成长追踪与报告系统为用户提供周报、月报和年报，帮助用户了解自己的社交成长轨迹，包括对话质量趋势、情绪健康评估、社交能力评分等多维度数据分析。

## 功能特性

### 1. 周报生成
- 统计最近7天的社交活动
- 显示对话总数、消息总数
- 计算平均对话质量
- 评估情绪健康状态
- 评估社交能力
- 识别最活跃的一天和场景
- 统计新建立的连接数
- 提供成长亮点和改进建议

### 2. 月报生成
- 统计最近30天的社交活动
- 包含周报的所有基础数据
- 显示对话质量趋势（按周）
- 显示情绪健康趋势（按周）
- 统计热门话题
- 分析场景分布

### 3. 年报生成
- 统计最近365天的社交活动
- 包含月报的所有基础数据
- 生成成就里程碑
- 展示人格演变数据
- 提供年度总结
- 统计累计好友数
- 记录最长对话时长

### 4. 报告下载
- 支持JSON格式下载
- 支持HTML格式下载
- 支持PDF格式下载

### 5. 报告分享
- 生成分享链接
- 支持图片分享
- 支持社交媒体分享
- 可设置隐私级别（公开/好友/私密）
- 自动设置过期时间（30天）

### 6. 数据可视化
- 对话数量统计
- 消息数量统计
- 质量得分曲线
- 情绪得分曲线
- 社交能力得分
- 场景分布图

## 数据模型

### GrowthReport（基础报告模型）
```python
{
    "report_id": "报告ID",
    "user_id": "用户ID",
    "report_type": "报告类型（weekly/monthly/annual）",
    "period_start": "统计开始时间",
    "period_end": "统计结束时间",
    "total_conversations": "对话总数",
    "total_messages": "消息总数",
    "average_conversation_quality": "平均对话质量（0-10）",
    "emotion_health_score": "情绪健康得分（0-10）",
    "social_skill_score": "社交能力得分（0-10）",
    "highlights": ["成长亮点列表"],
    "suggestions": ["改进建议列表"],
    "visualization_data": {"可视化数据"},
    "generated_at": "生成时间"
}
```

### WeeklyReport（周报模型）
继承自GrowthReport，额外包含：
```python
{
    "most_active_day": "最活跃的一天",
    "most_active_scene": "最活跃的场景",
    "new_connections": "新建立的连接数"
}
```

### MonthlyReport（月报模型）
继承自GrowthReport，额外包含：
```python
{
    "conversation_quality_trend": [周度质量趋势],
    "emotion_health_trend": [周度情绪趋势],
    "top_topics": ["热门话题"],
    "scene_distribution": {"场景分布"}
}
```

### AnnualReport（年报模型）
继承自GrowthReport，额外包含：
```python
{
    "milestones": ["成就里程碑"],
    "personality_evolution": {"人格演变数据"},
    "yearly_summary": "年度总结",
    "total_friends": "累计好友数",
    "longest_conversation_minutes": "最长对话时长（分钟）"
}
```

## API接口

### 生成周报
```python
report = report_service.generate_weekly_report(user_id)
```

### 生成月报
```python
report = report_service.generate_monthly_report(user_id)
```

### 生成年报
```python
report = report_service.generate_annual_report(user_id)
```

### 获取报告
```python
report = report_service.get_report(report_id)
```

### 列出用户报告
```python
# 列出所有报告
reports = report_service.list_user_reports(user_id)

# 按类型筛选
weekly_reports = report_service.list_user_reports(user_id, report_type='weekly')
```

### 下载报告
```python
# JSON格式
download_info = report_service.download_report(report_id, format='json')

# HTML格式
download_info = report_service.download_report(report_id, format='html')

# PDF格式
download_info = report_service.download_report(report_id, format='pdf')
```

### 分享报告
```python
share_link = report_service.share_report(
    report_id,
    share_type='link',  # link/image/social
    privacy_level='friends'  # public/friends/private
)
```

### 可视化成长数据
```python
viz_data = report_service.visualize_growth_data(user_id)
```

## 使用示例

### 示例1：生成并查看周报
```python
from src.services.report_service import ReportService

# 创建服务
report_service = ReportService()

# 生成周报
report = report_service.generate_weekly_report("user_001")

# 查看报告内容
print(f"对话总数: {report.total_conversations}")
print(f"平均质量: {report.average_conversation_quality}")
print(f"情绪健康: {report.emotion_health_score}")
print(f"社交能力: {report.social_skill_score}")

# 查看成长亮点
for highlight in report.highlights:
    print(f"✓ {highlight}")

# 查看改进建议
for suggestion in report.suggestions:
    print(f"• {suggestion}")
```

### 示例2：下载和分享报告
```python
# 下载HTML格式
download_info = report_service.download_report(
    report.report_id,
    format='html'
)
print(f"文件名: {download_info['filename']}")

# 分享报告
share_link = report_service.share_report(
    report.report_id,
    share_type='link',
    privacy_level='friends'
)
print(f"分享链接: {share_link.share_url}")
print(f"过期时间: {share_link.expires_at}")
```

### 示例3：查看成长趋势
```python
# 生成月报查看趋势
monthly_report = report_service.generate_monthly_report("user_001")

# 对话质量趋势
print("对话质量趋势（周度）:")
for i, score in enumerate(monthly_report.conversation_quality_trend, 1):
    print(f"第{i}周: {score:.1f}")

# 情绪健康趋势
print("情绪健康趋势（周度）:")
for i, score in enumerate(monthly_report.emotion_health_trend, 1):
    print(f"第{i}周: {score:.1f}")

# 场景分布
print("场景分布:")
for scene, count in monthly_report.scene_distribution.items():
    print(f"{scene}: {count}次")
```

## 评分算法

### 对话质量得分（0-10分）
- 基于对话的话题深度评分
- 考虑对话轮次和持续时间
- 综合情感同步性

### 情绪健康得分（0-10分）
- 基于情绪记录中正面情绪的比例
- 正面情绪比例 × 10
- 如果负面情绪超过50%，分数 × 0.7

### 社交能力得分（0-10分）
- 平均对话质量 × 0.7
- 对话数量因子（最多3分）
- 综合得分上限为10分

## 成长亮点生成规则

系统会根据以下条件自动生成成长亮点：

1. **对话数量亮点**
   - 超过10次：社交活跃度很高
   - 超过5次：保持良好的社交节奏

2. **对话质量亮点**
   - 平均质量≥7.0分：交流效果出色

3. **情绪健康亮点**
   - 情绪得分≥7.5分：心理状态积极向上

4. **社交能力亮点**
   - 社交得分≥7.0分：沟通技巧不断提升

5. **新连接亮点**
   - 新连接>5个：社交圈持续扩大

## 改进建议生成规则

系统会根据以下条件自动生成改进建议：

1. **对话数量建议**
   - 对话<3次：建议增加对话频率

2. **对话质量建议**
   - 平均质量<6.0分：建议尝试更深入的话题

3. **情绪健康建议**
   - 情绪得分<6.0分：建议注意情绪调节

4. **场景多样性建议**
   - 场景<2个：建议探索不同的社交场景

5. **社交能力建议**
   - 社交得分<6.0分：建议多参与对话

## 可视化数据格式

```python
{
    "conversation_count": 10,  # 对话数量
    "message_count": 250,  # 消息数量
    "quality_score": 7.5,  # 质量得分
    "emotion_score": 8.0,  # 情绪得分
    "social_skill_score": 7.2,  # 社交能力得分
    "scene_distribution": {  # 场景分布
        "考研自习室": 5,
        "兴趣社群": 3,
        "心理树洞": 2
    },
    "chart_type": "bar"  # 图表类型
}
```

## 注意事项

1. **数据隐私**
   - 报告包含用户敏感数据，需要严格的权限控制
   - 分享链接应设置合理的过期时间
   - 支持不同的隐私级别设置

2. **性能优化**
   - 报告生成可能涉及大量数据计算
   - 建议使用异步任务处理
   - 可以缓存已生成的报告

3. **数据准确性**
   - 确保统计数据的时间范围准确
   - 处理边界情况（如新用户、无数据等）
   - 提供合理的默认值

4. **用户体验**
   - 报告应该易于理解
   - 提供清晰的可视化展示
   - 成长亮点和建议应该具体且可操作

## 未来扩展

1. **更多报告类型**
   - 季度报告
   - 自定义时间范围报告

2. **更丰富的可视化**
   - 交互式图表
   - 动态数据展示
   - 对比分析

3. **智能分析**
   - AI生成个性化建议
   - 预测未来趋势
   - 识别成长模式

4. **社交功能**
   - 报告评论和点赞
   - 与好友对比
   - 成就徽章系统
