# 场景化社交空间实现文档

## 概述

场景化社交空间是青春伴行平台的核心功能之一，为用户提供基于不同社交需求的匹配场景。系统支持四种主要场景，每个场景都有独特的匹配策略和AI助手配置。

## 实现的功能

### 1. 场景配置数据模型

已在 `src/models/matching.py` 中定义 `SceneConfig` 模型，包含：
- 场景名称和显示名称
- 场景描述
- 匹配权重配置（人格、兴趣、场景、情感）
- 话题模板列表
- AI助手配置（介入阈值、最大介入次数）

### 2. 四种场景配置

#### 考研自习室
- **目标**: 为准备考研的同学提供学习伙伴匹配
- **匹配权重**: 
  - 人格: 25%
  - 兴趣: 35% (重点)
  - 场景: 30%
  - 情感: 10%
- **特点**: 优先匹配相同目标院校和专业的用户

#### 职业咨询室
- **目标**: 为职业规划和求职提供交流平台
- **匹配权重**:
  - 人格: 20%
  - 兴趣: 40% (最高)
  - 场景: 30%
  - 情感: 10%
- **特点**: 优先匹配相同职业兴趣或有相关经验的用户

#### 心理树洞
- **目标**: 提供情感支持和心理倾诉空间
- **匹配权重**:
  - 人格: 30%
  - 兴趣: 10%
  - 场景: 20%
  - 情感: 40% (最高)
- **特点**: 
  - 优先匹配有相似经历或情绪状态的用户
  - AI介入阈值更长（20秒）
  - 介入频率更低（每小时2次）

#### 兴趣社群
- **目标**: 基于共同兴趣爱好的社交匹配
- **匹配权重**:
  - 人格: 20%
  - 兴趣: 50% (最高)
  - 场景: 20%
  - 情感: 10%
- **特点**: 优先匹配相同兴趣爱好的用户

### 3. 场景管理服务

新增 `SceneManagementService` 类（`src/services/scene_management_service.py`），提供以下功能：

#### 核心方法

- `get_scene_config(scene)`: 获取场景配置
- `get_match_weights(scene)`: 获取场景匹配权重
- `list_available_scenes(user_id)`: 列出可用场景
- `switch_scene(user_id, scene, priority)`: 切换用户场景
- `remove_scene(user_id, scene)`: 移除用户场景
- `update_scene_priority(user_id, scene, priority)`: 更新场景优先级
- `get_scene_topic_templates(scene)`: 获取场景话题模板
- `get_scene_ai_config(scene)`: 获取场景AI配置
- `validate_scene(scene)`: 验证场景是否有效
- `get_all_scene_names()`: 获取所有场景名称

### 4. 场景切换逻辑

场景切换功能实现了以下特性：

1. **多场景支持**: 用户可以同时关注多个场景
2. **优先级管理**: 每个场景都有独立的优先级（0.0-1.0）
3. **动态更新**: 场景切换会自动更新用户画像
4. **匹配触发**: 场景切换会触发匹配度重新计算（异步）

### 5. 场景特定的匹配权重调整

匹配服务已集成场景权重：

- 不同场景使用不同的权重配置
- 考研场景优先考虑学业兴趣
- 职业场景优先考虑职业兴趣
- 心理场景优先考虑情感同步性
- 兴趣场景优先考虑兴趣爱好

## 使用示例

```python
from src.services.scene_management_service import SceneManagementService
from src.services.user_profile_service import UserProfileService
from src.services.matching_service import MatchingService

# 初始化服务
profile_service = UserProfileService()
matching_service = MatchingService(profile_service)
scene_service = SceneManagementService(profile_service, matching_service)

# 列出所有场景
scenes = scene_service.list_available_scenes()

# 切换场景
scene_service.switch_scene(user_id, "考研自习室", priority=0.8)

# 获取场景配置
config = scene_service.get_scene_config("考研自习室")

# 更新场景优先级
scene_service.update_scene_priority(user_id, "考研自习室", priority=1.0)

# 移除场景
scene_service.remove_scene(user_id, "心理树洞")
```

## 测试覆盖

已创建全面的测试套件（`tests/test_scene_management.py`），包括：

1. **基本功能测试** (15个测试)
   - 场景配置获取
   - 场景列表
   - 场景切换
   - 场景移除
   - 优先级更新
   - 话题模板和AI配置

2. **场景配置测试** (4个测试)
   - 验证每个场景的配置正确性
   - 验证权重分配合理性
   - 验证特殊配置（如心理树洞）

3. **场景切换逻辑测试** (3个测试)
   - 验证场景切换更新用户画像
   - 验证多场景切换
   - 验证场景切换影响匹配

4. **权重调整测试** (3个测试)
   - 验证不同场景使用不同权重
   - 验证考研场景优先学业兴趣
   - 验证职业场景优先职业兴趣

**测试结果**: 所有25个测试全部通过 ✓

## 演示程序

运行 `examples/scene_management_demo.py` 可以查看完整的功能演示，包括：
- 场景列表展示
- 场景配置查看
- 场景切换操作
- 优先级管理
- 权重对比
- 场景验证

## 验证需求

该实现满足以下需求：

- ✓ **需求 3.1**: 考研自习室场景优先匹配相同目标院校和专业的用户
- ✓ **需求 3.2**: 职业咨询室场景优先匹配相同职业兴趣或有相关经验的用户
- ✓ **需求 3.3**: 心理树洞场景优先匹配有相似经历或情绪状态的用户
- ✓ **需求 3.4**: 兴趣社群场景优先匹配相同兴趣爱好的用户
- ✓ **需求 3.5**: 场景切换时动态调整匹配权重并重新计算匹配度

## 下一步

场景化社交空间的核心功能已完成。后续可以：
1. 实现对话系统基础功能（任务6）
2. 实现AI对话助手（任务7）
3. 集成场景特定的话题建议
4. 优化场景切换的匹配度重新计算机制
