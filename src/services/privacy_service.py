"""隐私保护与数据安全服务"""
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os
import json

from src.models.privacy import (
    PrivacyPolicy, UserConsent, DataDeletionRequest, AnonymousProfile,
    UserPermission, EncryptedData, AuditLog,
    ConsentType, ConsentStatus, DataDeletionStatus, PermissionType,
    ConsentRequest, ConsentRevocationRequest, DataDeletionRequestCreate,
    AnonymousModeRequest, PermissionCheckRequest, PermissionGrantRequest
)
from src.utils.exceptions import (
    ValidationError, AuthorizationError, NotFoundError, DatabaseError
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PrivacyService:
    """隐私保护服务"""
    
    def __init__(self):
        """初始化隐私保护服务"""
        self.policies: Dict[str, PrivacyPolicy] = {}
        self.consents: Dict[str, List[UserConsent]] = {}  # user_id -> consents
        self.deletion_requests: Dict[str, DataDeletionRequest] = {}
        self.anonymous_profiles: Dict[str, AnonymousProfile] = {}  # user_id -> profile
        self.permissions: Dict[str, List[UserPermission]] = {}  # user_id -> permissions
        self.audit_logs: List[AuditLog] = []
        
        # 初始化默认隐私政策
        self._initialize_default_policy()
        
        logger.info("隐私保护服务初始化完成")
    
    def _initialize_default_policy(self):
        """初始化默认隐私政策"""
        policy = PrivacyPolicy(
            policy_id="default_v1",
            version="1.0",
            title="青春伴行平台隐私政策",
            content="""
            # 青春伴行平台隐私政策
            
            ## 1. 数据收集范围
            我们收集以下类型的数据：
            - 基本信息：姓名、学校、专业、年级
            - 人格测评数据：MBTI类型、大五人格得分
            - 兴趣标签和场景需求
            - 对话内容和消息记录
            - 行为数据：登录时间、活跃度等
            
            ## 2. 数据使用目的
            - 提供智能匹配服务
            - 优化用户画像
            - 生成成长报告
            - 改进平台功能
            
            ## 3. 数据保护措施
            - 使用HTTPS加密传输
            - 使用AES-256加密存储敏感数据
            - 严格的访问控制和权限管理
            - 定期安全审计
            
            ## 4. 用户权利
            - 查看和修改个人信息
            - 撤销授权
            - 请求删除数据
            - 使用匿名模式
            
            ## 5. 数据保留期限
            - 活跃用户数据：持续保留
            - 非活跃用户数据：6个月后匿名化
            - 删除请求：24小时内处理
            """,
            effective_date=datetime.now()
        )
        self.policies[policy.policy_id] = policy
        logger.info(f"默认隐私政策已初始化: {policy.policy_id}")
    
    def get_privacy_policy(self, policy_id: Optional[str] = None) -> PrivacyPolicy:
        """
        获取隐私政策
        
        Args:
            policy_id: 政策ID，如果为None则返回最新的活跃政策
            
        Returns:
            隐私政策对象
        """
        if policy_id:
            if policy_id not in self.policies:
                raise NotFoundError(f"隐私政策不存在: {policy_id}")
            return self.policies[policy_id]
        
        # 返回最新的活跃政策
        active_policies = [p for p in self.policies.values() if p.is_active]
        if not active_policies:
            raise NotFoundError("没有可用的隐私政策")
        
        return max(active_policies, key=lambda p: p.created_at)
    
    def grant_consent(self, request: ConsentRequest) -> List[UserConsent]:
        """
        授予用户授权
        
        Args:
            request: 授权请求
            
        Returns:
            授权记录列表
        """
        # 验证政策是否存在
        if request.policy_id not in self.policies:
            raise NotFoundError(f"隐私政策不存在: {request.policy_id}")
        
        consents = []
        for consent_type in request.consent_types:
            consent = UserConsent(
                consent_id=str(uuid.uuid4()),
                user_id=request.user_id,
                policy_id=request.policy_id,
                consent_type=consent_type,
                status=ConsentStatus.GRANTED,
                granted_at=datetime.now(),
                ip_address=request.ip_address,
                user_agent=request.user_agent
            )
            consents.append(consent)
        
        # 存储授权记录
        if request.user_id not in self.consents:
            self.consents[request.user_id] = []
        self.consents[request.user_id].extend(consents)
        
        # 记录审计日志
        self._log_audit(
            user_id=request.user_id,
            action="grant_consent",
            resource_type="consent",
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            details={"consent_types": [ct.value for ct in request.consent_types]}
        )
        
        logger.info(f"用户 {request.user_id} 授予了 {len(consents)} 项授权")
        return consents
    
    def revoke_consent(self, request: ConsentRevocationRequest) -> List[UserConsent]:
        """
        撤销用户授权
        
        Args:
            request: 撤销授权请求
            
        Returns:
            被撤销的授权记录列表
        """
        if request.user_id not in self.consents:
            return []
        
        revoked_consents = []
        for consent in self.consents[request.user_id]:
            if consent.consent_type in request.consent_types and consent.status == ConsentStatus.GRANTED:
                consent.status = ConsentStatus.REVOKED
                consent.revoked_at = datetime.now()
                revoked_consents.append(consent)
        
        # 记录审计日志
        self._log_audit(
            user_id=request.user_id,
            action="revoke_consent",
            resource_type="consent",
            details={"consent_types": [ct.value for ct in request.consent_types]}
        )
        
        logger.info(f"用户 {request.user_id} 撤销了 {len(revoked_consents)} 项授权")
        return revoked_consents
    
    def check_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        """
        检查用户是否已授权
        
        Args:
            user_id: 用户ID
            consent_type: 授权类型
            
        Returns:
            是否已授权
        """
        if user_id not in self.consents:
            return False
        
        for consent in self.consents[user_id]:
            if consent.consent_type == consent_type and consent.status == ConsentStatus.GRANTED:
                return True
        
        return False
    
    def request_data_deletion(self, request: DataDeletionRequestCreate) -> DataDeletionRequest:
        """
        请求删除数据
        
        Args:
            request: 数据删除请求
            
        Returns:
            数据删除请求对象
        """
        deletion_request = DataDeletionRequest(
            request_id=str(uuid.uuid4()),
            user_id=request.user_id,
            status=DataDeletionStatus.PENDING,
            data_types=request.data_types,
            reason=request.reason
        )
        
        self.deletion_requests[deletion_request.request_id] = deletion_request
        
        # 记录审计日志
        self._log_audit(
            user_id=request.user_id,
            action="request_data_deletion",
            resource_type="deletion_request",
            resource_id=deletion_request.request_id,
            details={"data_types": request.data_types}
        )
        
        logger.info(f"用户 {request.user_id} 请求删除数据: {deletion_request.request_id}")
        return deletion_request
    
    def process_data_deletion(self, request_id: str) -> DataDeletionRequest:
        """
        处理数据删除请求
        
        Args:
            request_id: 请求ID
            
        Returns:
            更新后的数据删除请求对象
        """
        if request_id not in self.deletion_requests:
            raise NotFoundError(f"数据删除请求不存在: {request_id}")
        
        deletion_request = self.deletion_requests[request_id]
        
        # 更新状态为处理中
        deletion_request.status = DataDeletionStatus.IN_PROGRESS
        
        try:
            # 执行数据删除操作
            self._delete_user_data(deletion_request.user_id, deletion_request.data_types)
            
            # 更新状态为已完成
            deletion_request.status = DataDeletionStatus.COMPLETED
            deletion_request.completed_at = datetime.now()
            
            # 记录审计日志
            self._log_audit(
                user_id=deletion_request.user_id,
                action="complete_data_deletion",
                resource_type="deletion_request",
                resource_id=request_id,
                details={"data_types": deletion_request.data_types}
            )
            
            logger.info(f"数据删除请求已完成: {request_id}")
        except Exception as e:
            deletion_request.status = DataDeletionStatus.FAILED
            deletion_request.notes = str(e)
            logger.error(f"数据删除请求失败: {request_id}, 错误: {str(e)}")
            raise DatabaseError(f"数据删除失败: {str(e)}")
        
        return deletion_request
    
    def _delete_user_data(self, user_id: str, data_types: List[str]):
        """
        删除用户数据（内部方法）
        
        Args:
            user_id: 用户ID
            data_types: 要删除的数据类型列表
        """
        # 这里应该实际删除数据库中的数据
        # 为了演示，我们只删除内存中的数据
        
        if "consents" in data_types:
            if user_id in self.consents:
                del self.consents[user_id]
        
        if "anonymous_profiles" in data_types:
            if user_id in self.anonymous_profiles:
                del self.anonymous_profiles[user_id]
        
        if "permissions" in data_types:
            if user_id in self.permissions:
                del self.permissions[user_id]
        
        logger.info(f"已删除用户 {user_id} 的数据类型: {data_types}")
    
    def enable_anonymous_mode(self, request: AnonymousModeRequest) -> Optional[AnonymousProfile]:
        """
        启用/禁用匿名模式
        
        Args:
            request: 匿名模式请求
            
        Returns:
            匿名用户画像对象（如果启用）
        """
        if request.enable:
            # 创建匿名画像
            anonymous_profile = AnonymousProfile(
                anonymous_id=str(uuid.uuid4()),
                user_id=request.user_id,
                display_name=f"匿名用户_{hashlib.md5(request.user_id.encode()).hexdigest()[:8]}",
                school_region="华东地区",  # 示例：将具体学校泛化为地区
                major_category="工科",  # 示例：将具体专业泛化为类别
                grade_range="本科",  # 示例：将具体年级泛化为范围
                expires_at=datetime.now() + timedelta(hours=request.duration_hours) if request.duration_hours else None
            )
            
            self.anonymous_profiles[request.user_id] = anonymous_profile
            
            # 记录审计日志
            self._log_audit(
                user_id=request.user_id,
                action="enable_anonymous_mode",
                resource_type="anonymous_profile",
                resource_id=anonymous_profile.anonymous_id
            )
            
            logger.info(f"用户 {request.user_id} 启用了匿名模式")
            return anonymous_profile
        else:
            # 禁用匿名模式
            if request.user_id in self.anonymous_profiles:
                profile = self.anonymous_profiles[request.user_id]
                profile.is_active = False
                
                # 记录审计日志
                self._log_audit(
                    user_id=request.user_id,
                    action="disable_anonymous_mode",
                    resource_type="anonymous_profile"
                )
                
                logger.info(f"用户 {request.user_id} 禁用了匿名模式")
            
            return None
    
    def get_anonymous_profile(self, user_id: str) -> Optional[AnonymousProfile]:
        """
        获取匿名用户画像
        
        Args:
            user_id: 用户ID
            
        Returns:
            匿名用户画像对象
        """
        profile = self.anonymous_profiles.get(user_id)
        
        # 检查是否过期
        if profile and profile.expires_at and profile.expires_at < datetime.now():
            profile.is_active = False
            logger.info(f"用户 {user_id} 的匿名模式已过期")
        
        return profile if profile and profile.is_active else None
    
    def check_permission(self, request: PermissionCheckRequest) -> bool:
        """
        检查用户权限
        
        Args:
            request: 权限检查请求
            
        Returns:
            是否有权限
        """
        if request.user_id not in self.permissions:
            # 默认授予基本权限
            return request.permission in [
                PermissionType.READ_PROFILE,
                PermissionType.READ_MESSAGES,
                PermissionType.SEND_MESSAGES,
                PermissionType.VIEW_MATCHES,
                PermissionType.REQUEST_MATCHES,
                PermissionType.VIEW_REPORTS
            ]
        
        for perm in self.permissions[request.user_id]:
            if perm.permission == request.permission and perm.granted:
                # 检查是否过期
                if perm.expires_at and perm.expires_at < datetime.now():
                    return False
                return True
        
        return False
    
    def grant_permission(self, request: PermissionGrantRequest) -> UserPermission:
        """
        授予用户权限
        
        Args:
            request: 权限授予请求
            
        Returns:
            用户权限对象
        """
        permission = UserPermission(
            user_id=request.user_id,
            permission=request.permission,
            granted=True,
            granted_by=request.granted_by,
            expires_at=request.expires_at
        )
        
        if request.user_id not in self.permissions:
            self.permissions[request.user_id] = []
        self.permissions[request.user_id].append(permission)
        
        # 记录审计日志
        self._log_audit(
            user_id=request.granted_by,
            action="grant_permission",
            resource_type="permission",
            details={
                "target_user": request.user_id,
                "permission": request.permission.value
            }
        )
        
        logger.info(f"用户 {request.user_id} 被授予权限: {request.permission.value}")
        return permission
    
    def revoke_permission(self, user_id: str, permission: PermissionType) -> bool:
        """
        撤销用户权限
        
        Args:
            user_id: 用户ID
            permission: 权限类型
            
        Returns:
            是否成功撤销
        """
        if user_id not in self.permissions:
            return False
        
        for perm in self.permissions[user_id]:
            if perm.permission == permission and perm.granted:
                perm.granted = False
                
                # 记录审计日志
                self._log_audit(
                    user_id=user_id,
                    action="revoke_permission",
                    resource_type="permission",
                    details={"permission": permission.value}
                )
                
                logger.info(f"用户 {user_id} 的权限被撤销: {permission.value}")
                return True
        
        return False
    
    def _log_audit(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        记录审计日志
        
        Args:
            user_id: 用户ID
            action: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            ip_address: IP地址
            user_agent: 用户代理
            details: 详细信息
        """
        log = AuditLog(
            log_id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        self.audit_logs.append(log)
    
    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        获取审计日志
        
        Args:
            user_id: 用户ID（可选）
            action: 操作类型（可选）
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            limit: 返回数量限制
            
        Returns:
            审计日志列表
        """
        logs = self.audit_logs
        
        # 过滤条件
        if user_id:
            logs = [log for log in logs if log.user_id == user_id]
        
        if action:
            logs = [log for log in logs if log.action == action]
        
        if start_time:
            logs = [log for log in logs if log.timestamp >= start_time]
        
        if end_time:
            logs = [log for log in logs if log.timestamp <= end_time]
        
        # 按时间倒序排序
        logs = sorted(logs, key=lambda x: x.timestamp, reverse=True)
        
        return logs[:limit]


class EncryptionService:
    """数据加密服务"""
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        """
        初始化加密服务
        
        Args:
            encryption_key: 加密密钥（32字节），如果为None则生成新密钥
        """
        self.encryption_key = encryption_key or os.urandom(32)  # AES-256需要32字节密钥
        logger.info("数据加密服务初始化完成")
    
    def encrypt(self, data: str) -> EncryptedData:
        """
        加密数据
        
        Args:
            data: 要加密的数据
            
        Returns:
            加密数据对象
        """
        # 生成随机初始化向量
        iv = os.urandom(16)
        
        # 创建加密器
        cipher = Cipher(
            algorithms.AES(self.encryption_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # 填充数据
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data.encode('utf-8')) + padder.finalize()
        
        # 加密
        encrypted_content = encryptor.update(padded_data) + encryptor.finalize()
        
        encrypted_data = EncryptedData(
            data_id=str(uuid.uuid4()),
            encrypted_content=encrypted_content,
            encryption_algorithm="AES-256",
            iv=iv
        )
        
        logger.debug(f"数据已加密: {encrypted_data.data_id}")
        return encrypted_data
    
    def decrypt(self, encrypted_data: EncryptedData) -> str:
        """
        解密数据
        
        Args:
            encrypted_data: 加密数据对象
            
        Returns:
            解密后的数据
        """
        # 创建解密器
        cipher = Cipher(
            algorithms.AES(self.encryption_key),
            modes.CBC(encrypted_data.iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # 解密
        padded_data = decryptor.update(encrypted_data.encrypted_content) + decryptor.finalize()
        
        # 去除填充
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        logger.debug(f"数据已解密: {encrypted_data.data_id}")
        return data.decode('utf-8')
    
    def encrypt_dict(self, data: Dict[str, Any]) -> EncryptedData:
        """
        加密字典数据
        
        Args:
            data: 要加密的字典
            
        Returns:
            加密数据对象
        """
        json_str = json.dumps(data, ensure_ascii=False)
        return self.encrypt(json_str)
    
    def decrypt_dict(self, encrypted_data: EncryptedData) -> Dict[str, Any]:
        """
        解密字典数据
        
        Args:
            encrypted_data: 加密数据对象
            
        Returns:
            解密后的字典
        """
        json_str = self.decrypt(encrypted_data)
        return json.loads(json_str)
