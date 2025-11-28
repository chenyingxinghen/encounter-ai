"""隐私保护与数据安全演示"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from src.services.privacy_service import PrivacyService, EncryptionService
from src.models.privacy import (
    ConsentType, PermissionType,
    ConsentRequest, ConsentRevocationRequest, DataDeletionRequestCreate,
    AnonymousModeRequest, PermissionCheckRequest, PermissionGrantRequest
)


def print_section(title: str):
    """打印章节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_privacy_policy():
    """演示隐私政策功能"""
    print_section("1. 隐私政策展示")
    
    privacy_service = PrivacyService()
    
    # 获取隐私政策
    policy = privacy_service.get_privacy_policy()
    print(f"隐私政策ID: {policy.policy_id}")
    print(f"版本: {policy.version}")
    print(f"标题: {policy.title}")
    print(f"生效日期: {policy.effective_date}")
    print(f"\n政策内容摘要:")
    print(policy.content[:200] + "...")


def demo_user_consent():
    """演示用户授权管理"""
    print_section("2. 用户授权管理")
    
    privacy_service = PrivacyService()
    user_id = "demo_user_001"
    
    # 用户授予授权
    print("步骤1: 用户授予授权")
    consent_request = ConsentRequest(
        user_id=user_id,
        policy_id="default_v1",
        consent_types=[
            ConsentType.DATA_COLLECTION,
            ConsentType.DATA_PROCESSING,
            ConsentType.ANALYTICS
        ],
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0"
    )
    consents = privacy_service.grant_consent(consent_request)
    print(f"✓ 已授予 {len(consents)} 项授权")
    for consent in consents:
        print(f"  - {consent.consent_type.value}: {consent.status.value}")
    
    # 检查授权状态
    print("\n步骤2: 检查授权状态")
    has_data_collection = privacy_service.check_consent(user_id, ConsentType.DATA_COLLECTION)
    has_marketing = privacy_service.check_consent(user_id, ConsentType.MARKETING)
    print(f"✓ 数据收集授权: {'已授权' if has_data_collection else '未授权'}")
    print(f"✓ 营销推广授权: {'已授权' if has_marketing else '未授权'}")
    
    # 撤销部分授权
    print("\n步骤3: 撤销部分授权")
    revoke_request = ConsentRevocationRequest(
        user_id=user_id,
        consent_types=[ConsentType.ANALYTICS]
    )
    revoked = privacy_service.revoke_consent(revoke_request)
    print(f"✓ 已撤销 {len(revoked)} 项授权")
    
    # 再次检查
    has_analytics = privacy_service.check_consent(user_id, ConsentType.ANALYTICS)
    print(f"✓ 数据分析授权: {'已授权' if has_analytics else '未授权'}")


def demo_data_encryption():
    """演示数据加密功能"""
    print_section("3. 数据加密（AES-256）")
    
    encryption_service = EncryptionService()
    
    # 加密字符串
    print("步骤1: 加密敏感字符串")
    sensitive_text = "这是用户的敏感信息：身份证号 110101199001011234"
    print(f"原始数据: {sensitive_text}")
    
    encrypted = encryption_service.encrypt(sensitive_text)
    print(f"✓ 加密成功")
    print(f"  - 数据ID: {encrypted.data_id}")
    print(f"  - 加密算法: {encrypted.encryption_algorithm}")
    print(f"  - 加密内容长度: {len(encrypted.encrypted_content)} 字节")
    print(f"  - IV长度: {len(encrypted.iv)} 字节")
    
    # 解密
    print("\n步骤2: 解密数据")
    decrypted = encryption_service.decrypt(encrypted)
    print(f"✓ 解密成功")
    print(f"  - 解密内容: {decrypted}")
    print(f"  - 数据完整性: {'✓ 验证通过' if decrypted == sensitive_text else '✗ 验证失败'}")
    
    # 加密字典
    print("\n步骤3: 加密复杂数据结构")
    user_data = {
        "user_id": "user_001",
        "real_name": "张三",
        "id_card": "110101199001011234",
        "phone": "13800138000",
        "email": "zhangsan@example.com",
        "address": "北京市朝阳区某某街道123号"
    }
    print(f"原始数据: {user_data}")
    
    encrypted_dict = encryption_service.encrypt_dict(user_data)
    print(f"✓ 加密成功")
    
    decrypted_dict = encryption_service.decrypt_dict(encrypted_dict)
    print(f"✓ 解密成功")
    print(f"  - 解密内容: {decrypted_dict}")


def demo_data_deletion():
    """演示数据删除功能"""
    print_section("4. 数据删除功能")
    
    privacy_service = PrivacyService()
    user_id = "demo_user_002"
    
    # 先创建一些数据
    print("步骤1: 创建用户数据")
    consent_request = ConsentRequest(
        user_id=user_id,
        policy_id="default_v1",
        consent_types=[ConsentType.DATA_COLLECTION]
    )
    privacy_service.grant_consent(consent_request)
    print(f"✓ 已创建用户授权数据")
    
    # 请求删除数据
    print("\n步骤2: 用户请求删除数据")
    deletion_request = DataDeletionRequestCreate(
        user_id=user_id,
        data_types=["consents", "permissions", "anonymous_profiles"],
        reason="不再使用平台服务"
    )
    deletion = privacy_service.request_data_deletion(deletion_request)
    print(f"✓ 删除请求已创建")
    print(f"  - 请求ID: {deletion.request_id}")
    print(f"  - 状态: {deletion.status.value}")
    print(f"  - 请求时间: {deletion.requested_at}")
    print(f"  - 数据类型: {', '.join(deletion.data_types)}")
    
    # 处理删除请求
    print("\n步骤3: 系统处理删除请求")
    result = privacy_service.process_data_deletion(deletion.request_id)
    print(f"✓ 删除请求已处理")
    print(f"  - 状态: {result.status.value}")
    print(f"  - 完成时间: {result.completed_at}")
    print(f"  - 处理时长: {(result.completed_at - result.requested_at).total_seconds():.2f} 秒")


def demo_anonymous_mode():
    """演示匿名模式功能"""
    print_section("5. 匿名模式")
    
    privacy_service = PrivacyService()
    user_id = "demo_user_003"
    
    # 启用匿名模式
    print("步骤1: 启用匿名模式")
    anon_request = AnonymousModeRequest(
        user_id=user_id,
        enable=True,
        duration_hours=24
    )
    anon_profile = privacy_service.enable_anonymous_mode(anon_request)
    print(f"✓ 匿名模式已启用")
    print(f"  - 匿名ID: {anon_profile.anonymous_id}")
    print(f"  - 显示名称: {anon_profile.display_name}")
    print(f"  - 学校地区: {anon_profile.school_region}")
    print(f"  - 专业类别: {anon_profile.major_category}")
    print(f"  - 年级范围: {anon_profile.grade_range}")
    print(f"  - 过期时间: {anon_profile.expires_at}")
    
    # 获取匿名画像
    print("\n步骤2: 获取匿名画像")
    profile = privacy_service.get_anonymous_profile(user_id)
    print(f"✓ 匿名画像状态: {'激活' if profile and profile.is_active else '未激活'}")
    
    # 禁用匿名模式
    print("\n步骤3: 禁用匿名模式")
    disable_request = AnonymousModeRequest(
        user_id=user_id,
        enable=False
    )
    privacy_service.enable_anonymous_mode(disable_request)
    print(f"✓ 匿名模式已禁用")


def demo_permission_management():
    """演示权限管理功能"""
    print_section("6. 权限管理系统")
    
    privacy_service = PrivacyService()
    user_id = "demo_user_004"
    admin_id = "admin_001"
    
    # 检查默认权限
    print("步骤1: 检查默认权限")
    basic_permissions = [
        PermissionType.READ_PROFILE,
        PermissionType.SEND_MESSAGES,
        PermissionType.VIEW_MATCHES,
        PermissionType.ADMIN_ACCESS
    ]
    
    for perm in basic_permissions:
        check_request = PermissionCheckRequest(user_id=user_id, permission=perm)
        has_perm = privacy_service.check_permission(check_request)
        status = "✓" if has_perm else "✗"
        print(f"  {status} {perm.value}: {'有权限' if has_perm else '无权限'}")
    
    # 授予特殊权限
    print("\n步骤2: 授予特殊权限")
    grant_request = PermissionGrantRequest(
        user_id=user_id,
        permission=PermissionType.DELETE_DATA,
        granted_by=admin_id
    )
    permission = privacy_service.grant_permission(grant_request)
    print(f"✓ 已授予权限: {permission.permission.value}")
    print(f"  - 授予者: {permission.granted_by}")
    print(f"  - 授予时间: {permission.granted_at}")
    
    # 验证权限
    print("\n步骤3: 验证权限")
    check_request = PermissionCheckRequest(
        user_id=user_id,
        permission=PermissionType.DELETE_DATA
    )
    has_perm = privacy_service.check_permission(check_request)
    print(f"✓ 删除数据权限: {'有权限' if has_perm else '无权限'}")
    
    # 撤销权限
    print("\n步骤4: 撤销权限")
    success = privacy_service.revoke_permission(user_id, PermissionType.DELETE_DATA)
    print(f"✓ 权限撤销: {'成功' if success else '失败'}")
    
    # 再次验证
    has_perm = privacy_service.check_permission(check_request)
    print(f"✓ 删除数据权限: {'有权限' if has_perm else '无权限'}")


def demo_audit_logs():
    """演示审计日志功能"""
    print_section("7. 审计日志")
    
    privacy_service = PrivacyService()
    user_id = "demo_user_005"
    
    # 执行一些操作
    print("步骤1: 执行用户操作")
    
    # 授权
    consent_request = ConsentRequest(
        user_id=user_id,
        policy_id="default_v1",
        consent_types=[ConsentType.DATA_COLLECTION],
        ip_address="192.168.1.200"
    )
    privacy_service.grant_consent(consent_request)
    print(f"✓ 操作1: 授予授权")
    
    # 启用匿名模式
    anon_request = AnonymousModeRequest(user_id=user_id, enable=True)
    privacy_service.enable_anonymous_mode(anon_request)
    print(f"✓ 操作2: 启用匿名模式")
    
    # 请求删除数据
    deletion_request = DataDeletionRequestCreate(
        user_id=user_id,
        data_types=["consents"]
    )
    privacy_service.request_data_deletion(deletion_request)
    print(f"✓ 操作3: 请求删除数据")
    
    # 查看审计日志
    print("\n步骤2: 查看审计日志")
    logs = privacy_service.get_audit_logs(user_id=user_id, limit=10)
    print(f"✓ 找到 {len(logs)} 条审计日志\n")
    
    for i, log in enumerate(logs, 1):
        print(f"日志 {i}:")
        print(f"  - 操作: {log.action}")
        print(f"  - 资源类型: {log.resource_type}")
        print(f"  - 时间: {log.timestamp}")
        if log.ip_address:
            print(f"  - IP地址: {log.ip_address}")
        if log.details:
            print(f"  - 详情: {log.details}")
        print()


def demo_complete_workflow():
    """演示完整的隐私保护工作流"""
    print_section("8. 完整工作流演示")
    
    privacy_service = PrivacyService()
    encryption_service = EncryptionService()
    user_id = "demo_user_complete"
    
    print("场景: 新用户注册并使用平台\n")
    
    # 1. 查看隐私政策
    print("第1步: 用户查看隐私政策")
    policy = privacy_service.get_privacy_policy()
    print(f"✓ 隐私政策: {policy.title} (版本 {policy.version})")
    
    # 2. 授予授权
    print("\n第2步: 用户授予必要授权")
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
    print(f"✓ 已授予 {len(consents)} 项授权")
    
    # 3. 加密存储敏感数据
    print("\n第3步: 加密存储用户敏感数据")
    sensitive_data = {
        "user_id": user_id,
        "real_name": "李四",
        "phone": "13900139000",
        "email": "lisi@example.com"
    }
    encrypted = encryption_service.encrypt_dict(sensitive_data)
    print(f"✓ 敏感数据已加密存储 (AES-256)")
    
    # 4. 使用匿名模式
    print("\n第4步: 用户在心理树洞场景使用匿名模式")
    anon_request = AnonymousModeRequest(
        user_id=user_id,
        enable=True,
        duration_hours=2
    )
    anon_profile = privacy_service.enable_anonymous_mode(anon_request)
    print(f"✓ 匿名模式已启用: {anon_profile.display_name}")
    
    # 5. 撤销部分授权
    print("\n第5步: 用户撤销营销推广授权")
    revoke_request = ConsentRevocationRequest(
        user_id=user_id,
        consent_types=[ConsentType.ANALYTICS]
    )
    privacy_service.revoke_consent(revoke_request)
    print(f"✓ 已撤销数据分析授权")
    
    # 6. 请求删除数据
    print("\n第6步: 用户决定离开平台，请求删除所有数据")
    deletion_request = DataDeletionRequestCreate(
        user_id=user_id,
        data_types=["profile", "messages", "consents", "anonymous_profiles"],
        reason="不再使用平台"
    )
    deletion = privacy_service.request_data_deletion(deletion_request)
    print(f"✓ 删除请求已提交: {deletion.request_id}")
    
    # 7. 系统处理删除请求
    print("\n第7步: 系统在24小时内处理删除请求")
    result = privacy_service.process_data_deletion(deletion.request_id)
    print(f"✓ 数据删除已完成")
    print(f"  - 状态: {result.status.value}")
    print(f"  - 完成时间: {result.completed_at}")
    
    # 8. 查看完整审计日志
    print("\n第8步: 查看完整操作审计日志")
    logs = privacy_service.get_audit_logs(user_id=user_id)
    print(f"✓ 记录了 {len(logs)} 条操作日志")
    
    print("\n✓ 完整工作流演示完成！")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  青春伴行平台 - 隐私保护与数据安全演示")
    print("="*60)
    
    try:
        demo_privacy_policy()
        demo_user_consent()
        demo_data_encryption()
        demo_data_deletion()
        demo_anonymous_mode()
        demo_permission_management()
        demo_audit_logs()
        demo_complete_workflow()
        
        print("\n" + "="*60)
        print("  所有演示完成！")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
