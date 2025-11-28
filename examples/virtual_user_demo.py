"""虚拟用户系统演示"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.virtual_user_service import VirtualUserService
from src.models.virtual_user import VirtualUserGenerationConfig


def main():
    """演示虚拟用户系统功能"""
    print("=" * 60)
    print("虚拟用户库与冷启动系统演示")
    print("=" * 60)
    
    # 创建虚拟用户服务
    service = VirtualUserService()
    
    # 1. 初始化虚拟用户库
    print("\n1. 初始化虚拟用户库（生成100个虚拟用户）")
    print("-" * 60)
    config = VirtualUserGenerationConfig(total_count=100)
    virtual_users = service.initialize_virtual_users(config)
    print(f"✓ 成功生成 {len(virtual_users)} 个虚拟用户")
    
    # 2. 展示虚拟用户身份标识
    print("\n2. 虚拟用户身份标识")
    print("-" * 60)
    sample_user = virtual_users[0]
    print(f"用户ID: {sample_user.user_id}")
    print(f"用户名: {sample_user.username}")
    print(f"是否虚拟用户: {'是 (AI伙伴)' if sample_user.is_virtual else '否'}")
    print(f"MBTI类型: {sample_user.mbti_type}")
    print(f"学校: {sample_user.school}")
    print(f"专业: {sample_user.major}")
    print(f"年级: {sample_user.grade}")
    
    # 3. 展示虚拟用户对话行为特征
    print("\n3. 虚拟用户对话行为模拟")
    print("-" * 60)
    print(f"回复风格: {sample_user.response_style}")
    print(f"回复速度范围: {sample_user.response_speed_range[0]:.1f}-{sample_user.response_speed_range[1]:.1f}秒")
    print(f"消息长度范围: {sample_user.message_length_range[0]}-{sample_user.message_length_range[1]}字符")
    
    # 模拟对话回复
    response_data = service.simulate_response(
        sample_user.user_id,
        "你好，最近在准备考研吗？",
        {"scene": "考研自习室"}
    )
    print(f"\n模拟回复数据:")
    print(f"  预计延迟: {response_data['response_delay']:.1f}秒")
    print(f"  预期长度: {response_data['expected_length']}字符")
    print(f"  回复提示: {response_data['response_hint']}")
    
    # 4. 展示虚拟用户画像
    print("\n4. 虚拟用户画像")
    print("-" * 60)
    profile = service.get_virtual_profile(sample_user.user_id)
    if profile:
        print(f"MBTI类型: {profile.mbti_type}")
        print(f"大五人格:")
        print(f"  神经质: {profile.big_five.neuroticism:.2f}")
        print(f"  宜人性: {profile.big_five.agreeableness:.2f}")
        print(f"  外向性: {profile.big_five.extraversion:.2f}")
        print(f"  开放性: {profile.big_five.openness:.2f}")
        print(f"  尽责性: {profile.big_five.conscientiousness:.2f}")
        print(f"学业兴趣: {', '.join(profile.academic_interests)}")
        print(f"兴趣爱好: {', '.join(profile.hobby_interests[:3])}...")
        print(f"职业兴趣: {', '.join(profile.career_interests)}")
        print(f"关注场景: {', '.join(profile.current_scenes)}")
    
    # 5. 展示MBTI类型分布
    print("\n5. MBTI类型分布")
    print("-" * 60)
    stats = service.get_statistics()
    print(f"虚拟用户总数: {stats.total_virtual_users}")
    print(f"真实用户总数: {stats.total_real_users}")
    print(f"当前匹配权重: {stats.virtual_user_weight:.2f}")
    print(f"\nMBTI类型分布:")
    for mbti_type in sorted(stats.mbti_distribution.keys()):
        count = stats.mbti_distribution[mbti_type]
        print(f"  {mbti_type}: {count}个")
    
    # 6. 模拟真实用户数量增长和权重动态调整
    print("\n6. 虚拟用户权重动态调整")
    print("-" * 60)
    
    # 初始状态（0个真实用户）
    print(f"真实用户数: 0 -> 虚拟用户权重: {stats.virtual_user_weight:.2f}")
    
    # 500个真实用户
    service.update_real_user_count(500)
    stats = service.get_statistics()
    print(f"真实用户数: 500 -> 虚拟用户权重: {stats.virtual_user_weight:.2f}")
    
    # 1000个真实用户（开始递减）
    service.update_real_user_count(1000)
    stats = service.get_statistics()
    print(f"真实用户数: 1000 -> 虚拟用户权重: {stats.virtual_user_weight:.2f}")
    
    # 5000个真实用户
    service.update_real_user_count(5000)
    stats = service.get_statistics()
    print(f"真实用户数: 5000 -> 虚拟用户权重: {stats.virtual_user_weight:.2f}")
    
    # 10000个真实用户（停止推送）
    service.update_real_user_count(10000)
    stats = service.get_statistics()
    print(f"真实用户数: 10000 -> 虚拟用户权重: {stats.virtual_user_weight:.2f}")
    print(f"活跃虚拟用户数: {stats.active_virtual_users}")
    
    # 15000个真实用户
    service.update_real_user_count(15000)
    stats = service.get_statistics()
    print(f"真实用户数: 15000 -> 虚拟用户权重: {stats.virtual_user_weight:.2f}")
    
    # 7. 验证虚拟用户识别
    print("\n7. 虚拟用户识别")
    print("-" * 60)
    test_virtual_id = sample_user.user_id
    test_real_id = "real_user_123"
    print(f"ID '{test_virtual_id[:20]}...' 是虚拟用户: {service.is_virtual_user(test_virtual_id)}")
    print(f"ID '{test_real_id}' 是虚拟用户: {service.is_virtual_user(test_real_id)}")
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
