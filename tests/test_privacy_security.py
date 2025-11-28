"""隐私保护与数据安全测试"""
import pytest
from datetime import datetime, timedelta
import json

from src.services.privacy_service import PrivacyService, EncryptionService
from src.models.privacy import (
    ConsentType, ConsentStatus, DataDeletionStatus, PermissionType,
    ConsentRequest, ConsentRevocationRequest, DataDeletionRequestCreate,
    AnonymousModeRequest, PermissionCheckRequest, PermissionGrantRequest
)
from src.utils.exceptions import NotFoundError, ValidationError


class TestPrivacyService:
    """隐私保护服务测试"""
    
    @pytest.fixture
    def privacy_service(self):
        """创建隐私保护服务实例"""
        return PrivacyService()
    
    def test_get_default_privacy_policy(self, privacy_service):
        """测试获取默认隐私政策"""
        policy = privacy_service.get_privacy_policy()
        
        assert policy is not None
        assert policy.policy_id == "default_v1"
        assert policy.version == "1.0"
        assert policy.is_active is True
        assert "数据收集范围" in policy.content
    
    def test_grant_consent(self, privacy_service):
        """测试授予用户授权"""
        request = ConsentRequest(
            user_id="user_001",
            policy_id="default_v1",
            consent_types=[ConsentType.DATA_COLLECTION, ConsentType.DATA_PROCESSING],
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        consents = privacy_service.grant_consent(request)
        
        assert len(consents) == 2
        assert all(c.status == ConsentStatus.GRANTED for c in consents)
        assert all(c.user_id == "user_001" for c in consents)
        assert all(c.granted_at is not None for c in consents)
    
    def test_check_consent(self, privacy_service):
        """测试检查用户授权"""
        # 先授予授权
        request = ConsentRequest(
            user_id="user_002",
            policy_id="default_v1",
            consent_types=[ConsentType.DATA_COLLECTION]
        )
        privacy_service.grant_consent(request)
        
        # 检查授权
        has_consent = privacy_service.check_consent("user_002", ConsentType.DATA_COLLECTION)
        assert has_consent is True
        
        # 检查未授权的类型
        has_consent = privacy_service.check_consent("user_002", ConsentType.MARKETING)
        assert has_consent is False
    
    def test_revoke_consent(self, privacy_service):
        """测试撤销用户授权"""
        # 先授予授权
        grant_request = ConsentRequest(
            user_id="user_003",
            policy_id="default_v1",
            consent_types=[ConsentType.DATA_COLLECTION, ConsentType.DATA_PROCESSING]
        )
        privacy_service.grant_consent(grant_request)
        
        # 撤销授权
        revoke_request = ConsentRevocationRequest(
            user_id="user_003",
            consent_types=[ConsentType.DATA_COLLECTION]
        )
        revoked = privacy_service.revoke_consent(revoke_request)
        
        assert len(revoked) == 1
        assert revoked[0].status == ConsentStatus.REVOKED
        assert revoked[0].revoked_at is not None
        
        # 验证授权已被撤销
        has_consent = privacy_service.check_consent("user_003", ConsentType.DATA_COLLECTION)
        assert has_consent is False
        
        # 验证其他授权仍然有效
        has_consent = privacy_service.check_consent("user_003", ConsentType.DATA_PROCESSING)
        assert has_consent is True
    
    def test_request_data_deletion(self, privacy_service):
        """测试请求删除数据"""
        request = DataDeletionRequestCreate(
            user_id="user_004",
            data_types=["profile", "messages", "conversations"],
            reason="不再使用平台"
        )
        
        deletion_request = privacy_service.request_data_deletion(request)
        
        assert deletion_request.request_id is not None
        assert deletion_request.user_id == "user_004"
        assert deletion_request.status == DataDeletionStatus.PENDING
        assert len(deletion_request.data_types) == 3
        assert deletion_request.requested_at is not None
    
    def test_process_data_deletion(self, privacy_service):
        """测试处理数据删除请求"""
        # 先创建删除请求
        request = DataDeletionRequestCreate(
            user_id="user_005",
            data_types=["consents", "permissions"]
        )
        deletion_request = privacy_service.request_data_deletion(request)
        
        # 先添加一些数据
        consent_request = ConsentRequest(
            user_id="user_005",
            policy_id="default_v1",
            consent_types=[ConsentType.DATA_COLLECTION]
        )
        privacy_service.grant_consent(consent_request)
        
        # 处理删除请求
        result = privacy_service.process_data_deletion(deletion_request.request_id)
        
        assert result.status == DataDeletionStatus.COMPLETED
        assert result.completed_at is not None
        
        # 验证数据已被删除
        assert "user_005" not in privacy_service.consents
    
    def test_enable_anonymous_mode(self, privacy_service):
        """测试启用匿名模式"""
        request = AnonymousModeRequest(
            user_id="user_006",
            enable=True,
            duration_hours=24
        )
        
        profile = privacy_service.enable_anonymous_mode(request)
        
        assert profile is not None
        assert profile.user_id == "user_006"
        assert profile.anonymous_id is not None
        assert profile.display_name.startswith("匿名用户_")
        assert profile.is_active is True
        assert profile.expires_at is not None
    
    def test_disable_anonymous_mode(self, privacy_service):
        """测试禁用匿名模式"""
        # 先启用
        enable_request = AnonymousModeRequest(
            user_id="user_007",
            enable=True
        )
        privacy_service.enable_anonymous_mode(enable_request)
        
        # 再禁用
        disable_request = AnonymousModeRequest(
            user_id="user_007",
            enable=False
        )
        result = privacy_service.enable_anonymous_mode(disable_request)
        
        assert result is None
        
        # 验证匿名模式已禁用
        profile = privacy_service.get_anonymous_profile("user_007")
        assert profile is None
    
    def test_check_permission_default(self, privacy_service):
        """测试检查默认权限"""
        request = PermissionCheckRequest(
            user_id="user_008",
            permission=PermissionType.READ_PROFILE
        )
        
        has_permission = privacy_service.check_permission(request)
        assert has_permission is True
        
        # 检查管理员权限（默认不应有）
        admin_request = PermissionCheckRequest(
            user_id="user_008",
            permission=PermissionType.ADMIN_ACCESS
        )
        has_admin = privacy_service.check_permission(admin_request)
        assert has_admin is False
    
    def test_grant_permission(self, privacy_service):
        """测试授予权限"""
        request = PermissionGrantRequest(
            user_id="user_009",
            permission=PermissionType.DELETE_DATA,
            granted_by="admin_001"
        )
        
        permission = privacy_service.grant_permission(request)
        
        assert permission.user_id == "user_009"
        assert permission.permission == PermissionType.DELETE_DATA
        assert permission.granted is True
        assert permission.granted_by == "admin_001"
        
        # 验证权限已授予
        check_request = PermissionCheckRequest(
            user_id="user_009",
            permission=PermissionType.DELETE_DATA
        )
        has_permission = privacy_service.check_permission(check_request)
        assert has_permission is True
    
    def test_revoke_permission(self, privacy_service):
        """测试撤销权限"""
        # 先授予权限
        grant_request = PermissionGrantRequest(
            user_id="user_010",
            permission=PermissionType.ADMIN_ACCESS,
            granted_by="admin_001"
        )
        privacy_service.grant_permission(grant_request)
        
        # 撤销权限
        success = privacy_service.revoke_permission("user_010", PermissionType.ADMIN_ACCESS)
        assert success is True
        
        # 验证权限已被撤销
        check_request = PermissionCheckRequest(
            user_id="user_010",
            permission=PermissionType.ADMIN_ACCESS
        )
        has_permission = privacy_service.check_permission(check_request)
        assert has_permission is False
    
    def test_audit_logs(self, privacy_service):
        """测试审计日志"""
        # 执行一些操作
        consent_request = ConsentRequest(
            user_id="user_011",
            policy_id="default_v1",
            consent_types=[ConsentType.DATA_COLLECTION],
            ip_address="192.168.1.100"
        )
        privacy_service.grant_consent(consent_request)
        
        # 获取审计日志
        logs = privacy_service.get_audit_logs(user_id="user_011")
        
        assert len(logs) > 0
        assert logs[0].user_id == "user_011"
        assert logs[0].action == "grant_consent"
        assert logs[0].ip_address == "192.168.1.100"
    
    def test_permission_expiration(self, privacy_service):
        """测试权限过期"""
        # 授予一个已过期的权限
        expired_time = datetime.now() - timedelta(hours=1)
        request = PermissionGrantRequest(
            user_id="user_012",
            permission=PermissionType.ADMIN_ACCESS,
            granted_by="admin_001",
            expires_at=expired_time
        )
        privacy_service.grant_permission(request)
        
        # 检查权限（应该因为过期而返回False）
        check_request = PermissionCheckRequest(
            user_id="user_012",
            permission=PermissionType.ADMIN_ACCESS
        )
        has_permission = privacy_service.check_permission(check_request)
        assert has_permission is False


class TestEncryptionService:
    """数据加密服务测试"""
    
    @pytest.fixture
    def encryption_service(self):
        """创建加密服务实例"""
        return EncryptionService()
    
    def test_encrypt_decrypt_string(self, encryption_service):
        """测试加密和解密字符串"""
        original_data = "这是一段敏感信息，需要加密保护"
        
        # 加密
        encrypted = encryption_service.encrypt(original_data)
        
        assert encrypted.data_id is not None
        assert encrypted.encryption_algorithm == "AES-256"
        assert encrypted.encrypted_content != original_data.encode()
        assert len(encrypted.iv) == 16
        
        # 解密
        decrypted = encryption_service.decrypt(encrypted)
        
        assert decrypted == original_data
    
    def test_encrypt_decrypt_dict(self, encryption_service):
        """测试加密和解密字典"""
        original_data = {
            "user_id": "user_001",
            "email": "user@example.com",
            "phone": "13800138000",
            "address": "北京市朝阳区"
        }
        
        # 加密
        encrypted = encryption_service.encrypt_dict(original_data)
        
        assert encrypted.data_id is not None
        assert encrypted.encrypted_content is not None
        
        # 解密
        decrypted = encryption_service.decrypt_dict(encrypted)
        
        assert decrypted == original_data
        assert decrypted["user_id"] == "user_001"
        assert decrypted["email"] == "user@example.com"
    
    def test_encrypt_empty_string(self, encryption_service):
        """测试加密空字符串"""
        original_data = ""
        
        encrypted = encryption_service.encrypt(original_data)
        decrypted = encryption_service.decrypt(encrypted)
        
        assert decrypted == original_data
    
    def test_encrypt_unicode(self, encryption_service):
        """测试加密Unicode字符"""
        original_data = "测试中文字符 🎉 emoji 表情"
        
        encrypted = encryption_service.encrypt(original_data)
        decrypted = encryption_service.decrypt(encrypted)
        
        assert decrypted == original_data
    
    def test_different_encryptions_produce_different_results(self, encryption_service):
        """测试相同数据的不同加密结果不同（因为IV不同）"""
        original_data = "相同的数据"
        
        encrypted1 = encryption_service.encrypt(original_data)
        encrypted2 = encryption_service.encrypt(original_data)
        
        # 加密结果应该不同（因为使用了不同的IV）
        assert encrypted1.encrypted_content != encrypted2.encrypted_content
        assert encrypted1.iv != encrypted2.iv
        
        # 但解密后应该相同
        decrypted1 = encryption_service.decrypt(encrypted1)
        decrypted2 = encryption_service.decrypt(encrypted2)
        
        assert decrypted1 == original_data
        assert decrypted2 == original_data


class TestPrivacyIntegration:
    """隐私保护集成测试"""
    
    @pytest.fixture
    def privacy_service(self):
        """创建隐私保护服务实例"""
        return PrivacyService()
    
    @pytest.fixture
    def encryption_service(self):
        """创建加密服务实例"""
        return EncryptionService()
    
    def test_complete_user_privacy_workflow(self, privacy_service):
        """测试完整的用户隐私工作流"""
        user_id = "user_workflow_001"
        
        # 1. 用户注册时查看隐私政策
        policy = privacy_service.get_privacy_policy()
        assert policy is not None
        
        # 2. 用户授予必要的授权
        consent_request = ConsentRequest(
            user_id=user_id,
            policy_id=policy.policy_id,
            consent_types=[
                ConsentType.DATA_COLLECTION,
                ConsentType.DATA_PROCESSING,
                ConsentType.ANALYTICS
            ]
        )
        consents = privacy_service.grant_consent(consent_request)
        assert len(consents) == 3
        
        # 3. 用户启用匿名模式
        anon_request = AnonymousModeRequest(
            user_id=user_id,
            enable=True,
            duration_hours=48
        )
        anon_profile = privacy_service.enable_anonymous_mode(anon_request)
        assert anon_profile is not None
        
        # 4. 用户撤销部分授权
        revoke_request = ConsentRevocationRequest(
            user_id=user_id,
            consent_types=[ConsentType.ANALYTICS]
        )
        revoked = privacy_service.revoke_consent(revoke_request)
        assert len(revoked) == 1
        
        # 5. 用户请求删除数据
        deletion_request = DataDeletionRequestCreate(
            user_id=user_id,
            data_types=["consents", "anonymous_profiles"],
            reason="测试数据删除"
        )
        deletion = privacy_service.request_data_deletion(deletion_request)
        assert deletion.status == DataDeletionStatus.PENDING
        
        # 6. 处理删除请求
        result = privacy_service.process_data_deletion(deletion.request_id)
        assert result.status == DataDeletionStatus.COMPLETED
        
        # 7. 验证审计日志记录了所有操作
        logs = privacy_service.get_audit_logs(user_id=user_id)
        assert len(logs) >= 4  # 至少有授权、启用匿名、撤销授权、删除数据
    
    def test_encrypted_sensitive_data_storage(self, encryption_service):
        """测试敏感数据加密存储"""
        # 模拟存储敏感用户数据
        sensitive_data = {
            "user_id": "user_sensitive_001",
            "real_name": "张三",
            "id_card": "110101199001011234",
            "phone": "13800138000",
            "email": "zhangsan@example.com",
            "address": "北京市朝阳区某某街道123号"
        }
        
        # 加密存储
        encrypted = encryption_service.encrypt_dict(sensitive_data)
        
        # 模拟从数据库读取加密数据
        # 在实际应用中，这里会从数据库读取
        stored_encrypted = encrypted
        
        # 解密使用
        decrypted = encryption_service.decrypt_dict(stored_encrypted)
        
        assert decrypted == sensitive_data
        assert decrypted["real_name"] == "张三"
        assert decrypted["id_card"] == "110101199001011234"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
