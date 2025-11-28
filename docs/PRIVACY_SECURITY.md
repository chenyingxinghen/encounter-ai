# 隐私保护与数据安全

## 概述

隐私保护与数据安全模块实现了青春伴行平台的核心安全功能，确保用户数据得到充分保护，符合隐私法规要求。

## 核心功能

### 1. 隐私政策展示

系统提供清晰的隐私政策，明确告知用户数据收集范围和用途。

**功能特性：**
- 版本化的隐私政策管理
- 自动展示最新有效政策
- 包含数据收集、使用、保护等完整信息

**使用示例：**
```python
from src.services.privacy_service import PrivacyService

privacy_service = PrivacyService()

# 获取最新隐私政策
policy = privacy_service.get_privacy_policy()
print(f"政策标题: {policy.title}")
print(f"版本: {policy.version}")
print(f"内容: {policy.content}")
```

### 2. 用户授权管理

实现细粒度的用户授权管理，用户可以选择性地授予或撤销不同类型的数据使用授权。

**授权类型：**
- `DATA_COLLECTION`: 数据收集
- `DATA_PROCESSING`: 数据处理
- `DATA_SHARING`: 数据共享
- `MARKETING`: 营销推广
- `ANALYTICS`: 数据分析

**使用示例：**
```python
from src.models.privacy import ConsentRequest, ConsentType, ConsentRevocationRequest

# 授予授权
consent_request = ConsentRequest(
    user_id="user_001",
    policy_id="default_v1",
    consent_types=[
        ConsentType.DATA_COLLECTION,
        ConsentType.DATA_PROCESSING
    ],
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0"
)
consents = privacy_service.grant_consent(consent_request)

# 检查授权
has_consent = privacy_service.check_consent("user_001", ConsentType.DATA_COLLECTION)

# 撤销授权
revoke_request = ConsentRevocationRequest(
    user_id="user_001",
    consent_types=[ConsentType.DATA_PROCESSING]
)
privacy_service.revoke_consent(revoke_request)
```

### 3. 数据加密（AES-256）

使用AES-256加密算法保护敏感数据的存储和传输。

**加密特性：**
- AES-256-CBC模式
- 随机初始化向量（IV）
- PKCS7填充
- 支持字符串和字典加密

**使用示例：**
```python
from src.services.privacy_service import EncryptionService

encryption_service = EncryptionService()

# 加密字符串
sensitive_text = "用户的敏感信息"
encrypted = encryption_service.encrypt(sensitive_text)

# 解密
decrypted = encryption_service.decrypt(encrypted)

# 加密字典
user_data = {
    "user_id": "user_001",
    "real_name": "张三",
    "phone": "13800138000"
}
encrypted_dict = encryption_service.encrypt_dict(user_data)
decrypted_dict = encryption_service.decrypt_dict(encrypted_dict)
```

### 4. 数据删除功能

用户可以请求删除个人数据，系统在24小时内完成处理。

**删除流程：**
1. 用户提交删除请求
2. 系统创建删除任务（状态：PENDING）
3. 系统处理删除（状态：IN_PROGRESS）
4. 删除完成（状态：COMPLETED）
5. 通知用户

**使用示例：**
```python
from src.models.privacy import DataDeletionRequestCreate

# 请求删除数据
deletion_request = DataDeletionRequestCreate(
    user_id="user_001",
    data_types=["profile", "messages", "conversations"],
    reason="不再使用平台"
)
deletion = privacy_service.request_data_deletion(deletion_request)

# 处理删除请求
result = privacy_service.process_data_deletion(deletion.request_id)
print(f"删除状态: {result.status}")
print(f"完成时间: {result.completed_at}")
```

### 5. 匿名模式

用户可以启用匿名模式，隐藏真实身份信息。

**匿名化策略：**
- 生成匿名ID和显示名称
- 将具体学校泛化为地区
- 将具体专业泛化为类别
- 将具体年级泛化为范围
- 保留必要的匹配信息（MBTI、兴趣等）

**使用示例：**
```python
from src.models.privacy import AnonymousModeRequest

# 启用匿名模式
anon_request = AnonymousModeRequest(
    user_id="user_001",
    enable=True,
    duration_hours=24  # 持续24小时
)
anon_profile = privacy_service.enable_anonymous_mode(anon_request)

print(f"匿名ID: {anon_profile.anonymous_id}")
print(f"显示名称: {anon_profile.display_name}")
print(f"学校地区: {anon_profile.school_region}")

# 获取匿名画像
profile = privacy_service.get_anonymous_profile("user_001")

# 禁用匿名模式
disable_request = AnonymousModeRequest(
    user_id="user_001",
    enable=False
)
privacy_service.enable_anonymous_mode(disable_request)
```

### 6. 权限管理系统

实现细粒度的权限控制，确保用户只能访问授权的资源。

**权限类型：**
- `READ_PROFILE`: 读取画像
- `WRITE_PROFILE`: 修改画像
- `READ_MESSAGES`: 读取消息
- `SEND_MESSAGES`: 发送消息
- `VIEW_MATCHES`: 查看匹配
- `REQUEST_MATCHES`: 请求匹配
- `VIEW_REPORTS`: 查看报告
- `DELETE_DATA`: 删除数据
- `ADMIN_ACCESS`: 管理员访问

**使用示例：**
```python
from src.models.privacy import PermissionCheckRequest, PermissionGrantRequest, PermissionType

# 检查权限
check_request = PermissionCheckRequest(
    user_id="user_001",
    permission=PermissionType.DELETE_DATA
)
has_permission = privacy_service.check_permission(check_request)

# 授予权限
grant_request = PermissionGrantRequest(
    user_id="user_001",
    permission=PermissionType.DELETE_DATA,
    granted_by="admin_001",
    expires_at=datetime.now() + timedelta(days=30)
)
permission = privacy_service.grant_permission(grant_request)

# 撤销权限
privacy_service.revoke_permission("user_001", PermissionType.DELETE_DATA)
```

### 7. 审计日志

记录所有隐私相关操作，用于安全审计和问题追溯。

**记录内容：**
- 用户ID
- 操作类型
- 资源类型和ID
- IP地址
- 用户代理
- 时间戳
- 详细信息

**使用示例：**
```python
# 获取审计日志
logs = privacy_service.get_audit_logs(
    user_id="user_001",
    action="grant_consent",
    start_time=datetime.now() - timedelta(days=7),
    limit=50
)

for log in logs:
    print(f"操作: {log.action}")
    print(f"时间: {log.timestamp}")
    print(f"IP: {log.ip_address}")
    print(f"详情: {log.details}")
```

## 数据模型

### PrivacyPolicy（隐私政策）
```python
class PrivacyPolicy:
    policy_id: str          # 政策ID
    version: str            # 版本号
    title: str              # 标题
    content: str            # 政策内容
    effective_date: datetime # 生效日期
    is_active: bool         # 是否有效
```

### UserConsent（用户授权）
```python
class UserConsent:
    consent_id: str         # 授权记录ID
    user_id: str            # 用户ID
    policy_id: str          # 隐私政策ID
    consent_type: ConsentType # 授权类型
    status: ConsentStatus   # 授权状态
    granted_at: datetime    # 授权时间
    revoked_at: datetime    # 撤销时间
```

### DataDeletionRequest（数据删除请求）
```python
class DataDeletionRequest:
    request_id: str         # 请求ID
    user_id: str            # 用户ID
    status: DataDeletionStatus # 删除状态
    requested_at: datetime  # 请求时间
    completed_at: datetime  # 完成时间
    data_types: List[str]   # 要删除的数据类型
```

### AnonymousProfile（匿名用户画像）
```python
class AnonymousProfile:
    anonymous_id: str       # 匿名ID
    user_id: str            # 真实用户ID
    display_name: str       # 显示名称
    school_region: str      # 学校地区
    major_category: str     # 专业类别
    grade_range: str        # 年级范围
    expires_at: datetime    # 过期时间
```

### UserPermission（用户权限）
```python
class UserPermission:
    user_id: str            # 用户ID
    permission: PermissionType # 权限类型
    granted: bool           # 是否授予
    granted_at: datetime    # 授予时间
    granted_by: str         # 授予者ID
    expires_at: datetime    # 过期时间
```

## 安全最佳实践

### 1. 数据传输安全
- 使用HTTPS加密所有数据传输
- 实施TLS 1.2或更高版本
- 配置强加密套件

### 2. 数据存储安全
- 敏感数据使用AES-256加密
- 密钥独立存储和管理
- 定期轮换加密密钥

### 3. 访问控制
- 实施最小权限原则
- 定期审查用户权限
- 记录所有访问操作

### 4. 审计和监控
- 记录所有隐私相关操作
- 定期审查审计日志
- 设置异常行为告警

### 5. 数据删除
- 24小时内处理删除请求
- 彻底删除所有相关数据
- 保留必要的审计记录

## 合规性

本模块设计符合以下法规要求：

- **GDPR（欧盟通用数据保护条例）**
  - 数据主体权利（访问、修改、删除）
  - 数据处理透明度
  - 数据最小化原则

- **中国个人信息保护法**
  - 明确告知和同意
  - 数据安全保护措施
  - 个人信息删除权

## 错误处理

### 常见错误

1. **NotFoundError**: 隐私政策或请求不存在
2. **ValidationError**: 请求参数验证失败
3. **AuthorizationError**: 权限不足
4. **DatabaseError**: 数据删除失败

### 错误处理示例
```python
from src.utils.exceptions import NotFoundError, AuthorizationError

try:
    policy = privacy_service.get_privacy_policy("invalid_id")
except NotFoundError as e:
    print(f"政策不存在: {e.message}")

try:
    privacy_service.check_permission(request)
except AuthorizationError as e:
    print(f"权限不足: {e.message}")
```

## 性能考虑

### 加密性能
- AES-256加密速度：约100MB/s
- 适合中小型数据加密
- 大文件建议分块加密

### 审计日志
- 使用异步写入避免阻塞
- 定期归档历史日志
- 建立索引提高查询效率

## 测试

运行测试：
```bash
pytest tests/test_privacy_security.py -v
```

运行演示：
```bash
python examples/privacy_security_demo.py
```

## 未来改进

1. **多因素认证（MFA）**
   - 短信验证码
   - 邮箱验证
   - 生物识别

2. **数据脱敏**
   - 自动识别敏感字段
   - 多种脱敏策略
   - 可逆/不可逆脱敏

3. **隐私计算**
   - 联邦学习
   - 差分隐私
   - 同态加密

4. **合规性自动化**
   - 自动生成隐私影响评估
   - 合规性检查工具
   - 数据地图可视化

## 参考资料

- [GDPR官方文档](https://gdpr.eu/)
- [中国个人信息保护法](http://www.npc.gov.cn/)
- [OWASP安全指南](https://owasp.org/)
- [AES加密标准](https://csrc.nist.gov/publications/detail/fips/197/final)
