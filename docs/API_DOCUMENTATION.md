# API接口文档

## 概述

青春伴行平台提供完整的RESTful API接口，支持用户注册、认证、匹配、对话、报告和内容审查等功能。

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API版本**: v0.1.0
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON

## 认证

大部分API接口需要JWT认证。在请求头中包含：

```
Authorization: Bearer <access_token>
```

## API端点

### 1. 认证模块 (Authentication)

#### 1.1 用户登录

**端点**: `POST /api/auth/login`

**描述**: 验证用户凭证并返回访问令牌

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "uuid",
  "username": "用户名"
}
```

#### 1.2 用户登出

**端点**: `POST /api/auth/logout`

**描述**: 使当前令牌失效

**认证**: 需要

**响应**:
```json
{
  "message": "登出成功",
  "user_id": "uuid"
}
```

#### 1.3 获取当前用户

**端点**: `GET /api/auth/me`

**描述**: 获取当前登录用户的信息

**认证**: 需要

**响应**: User对象

---

### 2. 用户模块 (Users)

#### 2.1 用户注册

**端点**: `POST /api/users/register`

**描述**: 注册新用户并创建账号

**请求体**:
```json
{
  "username": "张三",
  "email": "zhangsan@example.com",
  "password": "password123",
  "school": "清华大学",
  "major": "计算机科学",
  "grade": 3
}
```

**响应**: User对象 (201 Created)

#### 2.2 提交MBTI测试

**端点**: `POST /api/users/mbti-test`

**描述**: 提交MBTI测试问卷并获取人格类型

**请求体**:
```json
{
  "user_id": "uuid",
  "answers": [3, 4, 2, ...] // 60个答案
}
```

**响应**:
```json
{
  "user_id": "uuid",
  "mbti_type": "INFP",
  "message": "MBTI测试完成"
}
```

#### 2.3 提交大五人格测试

**端点**: `POST /api/users/big-five-test`

**描述**: 提交大五人格评估问卷

**请求体**:
```json
{
  "user_id": "uuid",
  "answers": [3, 4, 2, ...] // 50个答案
}
```

**响应**:
```json
{
  "user_id": "uuid",
  "scores": {
    "neuroticism": 0.6,
    "agreeableness": 0.7,
    "extraversion": 0.5,
    "openness": 0.8,
    "conscientiousness": 0.7
  },
  "message": "大五人格评估完成"
}
```

#### 2.4 更新兴趣标签

**端点**: `POST /api/users/interests`

**描述**: 更新用户的兴趣标签

**请求体**:
```json
{
  "user_id": "uuid",
  "academic_interests": ["考研", "编程"],
  "career_interests": ["软件工程师"],
  "hobby_interests": ["阅读", "音乐"]
}
```

**响应**: UserProfile对象

#### 2.5 更新场景选择

**端点**: `POST /api/users/scenes`

**描述**: 更新用户关注的社交场景

**请求体**:
```json
{
  "user_id": "uuid",
  "scenes": ["考研自习室", "兴趣社群"]
}
```

**响应**: UserProfile对象

#### 2.6 生成初始画像

**端点**: `POST /api/users/profile/generate?user_id={user_id}`

**描述**: 完成所有设置后生成完整的用户画像

**响应**: UserProfile对象

#### 2.7 获取用户画像

**端点**: `GET /api/users/profile/{user_id}`

**描述**: 查询指定用户的画像信息

**响应**: UserProfile对象

#### 2.8 获取用户信息

**端点**: `GET /api/users/{user_id}`

**描述**: 查询指定用户的基本信息

**响应**: User对象

---

### 3. 匹配模块 (Matching)

#### 3.1 查找匹配对象

**端点**: `POST /api/matching/find`

**描述**: 根据用户画像和场景查找合适的匹配对象

**认证**: 需要

**请求体**:
```json
{
  "scene": "考研自习室",
  "limit": 10
}
```

**响应**:
```json
{
  "matches": [
    {
      "match_id": "uuid",
      "user_a_id": "uuid",
      "user_b_id": "uuid",
      "scene": "考研自习室",
      "match_score": 85.5,
      "match_reason": "你们都在准备考研，目标院校相同",
      "personality_score": 80.0,
      "interest_score": 90.0,
      "scene_score": 85.0,
      "emotion_sync_score": 87.0,
      "status": "pending",
      "created_at": "2024-01-01T00:00:00",
      "expires_at": "2024-01-08T00:00:00"
    }
  ],
  "total": 10
}
```

#### 3.2 计算匹配度

**端点**: `GET /api/matching/score/{target_user_id}?scene={scene}`

**描述**: 计算当前用户与目标用户的匹配度

**认证**: 需要

**响应**:
```json
{
  "user_a": "uuid",
  "user_b": "uuid",
  "scene": "考研自习室",
  "match_score": 85.5,
  "match_reason": "你们都在准备考研，目标院校相同"
}
```

#### 3.3 获取匹配历史

**端点**: `GET /api/matching/history?limit={limit}`

**描述**: 查询用户的历史匹配记录

**认证**: 需要

**响应**: Match对象数组

#### 3.4 接受匹配

**端点**: `POST /api/matching/accept/{match_id}`

**描述**: 用户接受一个匹配请求

**认证**: 需要

**响应**:
```json
{
  "message": "匹配已接受",
  "match_id": "uuid",
  "result": {...}
}
```

#### 3.5 拒绝匹配

**端点**: `POST /api/matching/reject/{match_id}`

**描述**: 用户拒绝一个匹配请求

**认证**: 需要

**响应**:
```json
{
  "message": "匹配已拒绝",
  "match_id": "uuid",
  "result": {...}
}
```

---

### 4. 对话模块 (Conversations)

#### 4.1 创建对话

**端点**: `POST /api/conversations/create`

**描述**: 在两个用户之间创建新的对话

**认证**: 需要

**请求体**:
```json
{
  "partner_id": "uuid",
  "scene": "考研自习室"
}
```

**响应**: Conversation对象 (201 Created)

#### 4.2 获取对话详情

**端点**: `GET /api/conversations/{conversation_id}?limit={limit}`

**描述**: 查询对话信息和历史消息

**认证**: 需要

**响应**:
```json
{
  "conversation": {
    "conversation_id": "uuid",
    "user_a_id": "uuid",
    "user_b_id": "uuid",
    "scene": "考研自习室",
    "status": "active",
    "started_at": "2024-01-01T00:00:00",
    "message_count": 50,
    "silence_count": 2,
    "ai_intervention_count": 1
  },
  "messages": [...]
}
```

#### 4.3 获取对话列表

**端点**: `GET /api/conversations/?status_filter={status}&limit={limit}`

**描述**: 查询用户的所有对话

**认证**: 需要

**参数**:
- `status_filter` (可选): active, paused, ended
- `limit` (可选): 默认20

**响应**: Conversation对象数组

#### 4.4 发送消息

**端点**: `POST /api/conversations/{conversation_id}/messages`

**描述**: 在对话中发送新消息

**认证**: 需要

**请求体**:
```json
{
  "content": "你好，很高兴认识你！",
  "message_type": "text"
}
```

**响应**: Message对象 (201 Created)

#### 4.5 获取消息列表

**端点**: `GET /api/conversations/{conversation_id}/messages?limit={limit}&before={timestamp}`

**描述**: 查询对话的历史消息

**认证**: 需要

**响应**: Message对象数组

#### 4.6 暂停对话

**端点**: `POST /api/conversations/{conversation_id}/pause`

**描述**: 暂停当前对话

**认证**: 需要

**响应**:
```json
{
  "message": "对话已暂停",
  "conversation": {...}
}
```

#### 4.7 结束对话

**端点**: `POST /api/conversations/{conversation_id}/end`

**描述**: 结束当前对话

**认证**: 需要

**响应**:
```json
{
  "message": "对话已结束",
  "conversation": {...}
}
```

---

### 5. 报告模块 (Reports)

#### 5.1 生成成长报告

**端点**: `POST /api/reports/generate`

**描述**: 根据指定类型和时间段生成用户成长报告

**认证**: 需要

**请求体**:
```json
{
  "report_type": "weekly",  // weekly, monthly, annual
  "period_start": "2024-01-01T00:00:00",  // 可选
  "period_end": "2024-01-07T23:59:59"     // 可选
}
```

**响应**: GrowthReport对象 (201 Created)

#### 5.2 获取报告列表

**端点**: `GET /api/reports/?report_type={type}&limit={limit}`

**描述**: 查询用户的历史报告

**认证**: 需要

**响应**: GrowthReport对象数组

#### 5.3 获取报告详情

**端点**: `GET /api/reports/{report_id}`

**描述**: 查询指定报告的详细信息

**认证**: 需要

**响应**: GrowthReport对象

#### 5.4 下载报告

**端点**: `GET /api/reports/{report_id}/download?format={format}`

**描述**: 以指定格式下载报告文件

**认证**: 需要

**参数**:
- `format`: pdf 或 json

**响应**: 文件下载

#### 5.5 分享报告

**端点**: `POST /api/reports/{report_id}/share`

**描述**: 生成报告分享链接

**认证**: 需要

**响应**:
```json
{
  "message": "分享链接已生成",
  "report_id": "uuid",
  "share_link": "https://youth-companion.com/reports/share/token",
  "expires_in": "7天"
}
```

#### 5.6 获取最新报告

**端点**: `GET /api/reports/latest/{report_type}`

**描述**: 查询指定类型的最新报告

**认证**: 需要

**响应**: GrowthReport对象

---

### 6. 内容审查模块 (Moderation)

#### 6.1 举报用户

**端点**: `POST /api/moderation/report`

**描述**: 用户举报其他用户的违规行为

**认证**: 需要

**请求体**:
```json
{
  "reported_id": "uuid",
  "report_type": "harassment",  // harassment, inappropriate_content, fake_profile, other
  "reason": "该用户发送骚扰信息",
  "evidence": ["message_id_1", "message_id_2"]
}
```

**响应**: UserReport对象 (201 Created)

#### 6.2 获取我的举报记录

**端点**: `GET /api/moderation/reports?status_filter={status}&limit={limit}`

**描述**: 查询用户提交的举报记录

**认证**: 需要

**响应**: UserReport对象数组

#### 6.3 获取举报详情

**端点**: `GET /api/moderation/reports/{report_id}`

**描述**: 查询指定举报的详细信息

**认证**: 需要

**响应**: UserReport对象

#### 6.4 获取我的违规记录

**端点**: `GET /api/moderation/violations?limit={limit}`

**描述**: 查询用户的违规历史

**认证**: 需要

**响应**: Violation对象数组

#### 6.5 获取违规详情

**端点**: `GET /api/moderation/violations/{violation_id}`

**描述**: 查询指定违规记录的详细信息

**认证**: 需要

**响应**: Violation对象

#### 6.6 提交申诉

**端点**: `POST /api/moderation/appeal`

**描述**: 用户对违规处罚提出申诉

**认证**: 需要

**请求体**:
```json
{
  "violation_id": "uuid",
  "appeal_reason": "这是误判，我没有违规"
}
```

**响应**:
```json
{
  "message": "申诉已提交",
  "violation_id": "uuid",
  "status": "pending_review",
  "result": {...}
}
```

#### 6.7 获取我的处罚记录

**端点**: `GET /api/moderation/penalties?status_filter={status}&limit={limit}`

**描述**: 查询用户的处罚历史

**认证**: 需要

**参数**:
- `status_filter` (可选): active, expired, revoked

**响应**: Penalty对象数组

#### 6.8 获取处罚详情

**端点**: `GET /api/moderation/penalties/{penalty_id}`

**描述**: 查询指定处罚的详细信息

**认证**: 需要

**响应**: Penalty对象

#### 6.9 获取审查状态

**端点**: `GET /api/moderation/status`

**描述**: 查询用户当前的审查状态

**认证**: 需要

**响应**:
```json
{
  "user_id": "uuid",
  "is_muted": false,
  "is_suspended": false,
  "is_banned": false,
  "active_penalties": 0,
  "total_violations": 2,
  "penalties": []
}
```

---

### 7. 系统模块

#### 7.1 根路径

**端点**: `GET /`

**描述**: 获取API基本信息

**响应**:
```json
{
  "app": "青春伴行平台",
  "version": "0.1.0",
  "status": "running"
}
```

#### 7.2 健康检查

**端点**: `GET /health`

**描述**: 检查系统健康状态

**响应**:
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

---

## 错误响应

所有API错误响应遵循统一格式：

```json
{
  "detail": "错误描述信息"
}
```

### HTTP状态码

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证或认证失败
- `403 Forbidden`: 无权访问
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

---

## 交互式文档

系统提供两种交互式API文档：

1. **Swagger UI**: `http://localhost:8000/docs`
   - 提供完整的API测试界面
   - 支持直接在浏览器中测试API

2. **ReDoc**: `http://localhost:8000/redoc`
   - 提供更美观的文档展示
   - 适合阅读和参考

---

## 使用示例

### Python示例

```python
import requests

# 1. 注册用户
register_data = {
    "username": "张三",
    "email": "zhangsan@example.com",
    "password": "password123",
    "school": "清华大学",
    "major": "计算机科学",
    "grade": 3
}
response = requests.post("http://localhost:8000/api/users/register", json=register_data)
user = response.json()

# 2. 登录
login_data = {
    "email": "zhangsan@example.com",
    "password": "password123"
}
response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
token = response.json()["access_token"]

# 3. 使用token访问受保护的API
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    "http://localhost:8000/api/matching/find",
    json={"scene": "考研自习室", "limit": 10},
    headers=headers
)
matches = response.json()
```

### JavaScript示例

```javascript
// 1. 注册用户
const registerData = {
  username: "张三",
  email: "zhangsan@example.com",
  password: "password123",
  school: "清华大学",
  major: "计算机科学",
  grade: 3
};

const registerResponse = await fetch("http://localhost:8000/api/users/register", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(registerData)
});
const user = await registerResponse.json();

// 2. 登录
const loginData = {
  email: "zhangsan@example.com",
  password: "password123"
};

const loginResponse = await fetch("http://localhost:8000/api/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(loginData)
});
const { access_token } = await loginResponse.json();

// 3. 使用token访问受保护的API
const matchResponse = await fetch("http://localhost:8000/api/matching/find", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${access_token}`
  },
  body: JSON.stringify({ scene: "考研自习室", limit: 10 })
});
const matches = await matchResponse.json();
```

---

## 注意事项

1. **令牌过期**: JWT令牌默认24小时过期，过期后需要重新登录
2. **请求限制**: 为防止滥用，部分API有频率限制
3. **数据验证**: 所有输入数据都会进行严格验证
4. **HTTPS**: 生产环境必须使用HTTPS加密传输
5. **CORS**: 开发环境允许所有来源，生产环境需要配置白名单

---

## 更新日志

### v0.1.0 (2024-01-01)
- 初始版本发布
- 实现用户注册、认证、匹配、对话、报告和内容审查功能
- 提供完整的RESTful API接口
- 集成Swagger UI和ReDoc文档
