"""场景管理功能演示"""
from src.models.user import (
    UserRegistrationRequest, MBTITestRequest, BigFiveTestRequest,
    InterestSelectionRequest, SceneSelectionRequest
)
from src.services.user_profile_service import UserProfileService
from src.services.matching_service import MatchingService
from src.services.scene_management_service import SceneManagementService


def main():
    """演示场景管理功能"""
    print("=" * 60)
    print("场景管理功能演示")
    print("=" * 60)
    
    # 初始化服务
    profile_service = UserProfileService()
    matching_service = MatchingService(profile_service)
    scene_service = SceneManagementService(profile_service, matching_service)
    
    # 1. 列出所有可用场景
    print("\n1. 列出所有可用场景:")
    print("-" * 60)
    scenes = scene_service.list_available_scenes()
    for scene in scenes:
        print(f"场景: {scene['display_name']}")
        print(f"  描述: {scene['description']}")
        print()
    
    # 2. 创建测试用户
    print("2. 创建测试用户:")
    print("-" * 60)
    user = profile_service.register_user(
        UserRegistrationRequest(
            username="张三",
            email="zhangsan@example.com",
            password="password123",
            school="清华大学",
            major="计算机科学",
            grade=2
        )
    )
    print(f"用户创建成功: {user.username} ({user.user_id})")
    
    # 完成测评
    profile_service.process_mbti_test(
        MBTITestRequest(user_id=user.user_id, answers=[3] * 60)
    )
    profile_service.process_big_five_test(
        BigFiveTestRequest(user_id=user.user_id, answers=[3] * 50)
    )
    profile_service.update_interests(
        InterestSelectionRequest(
            user_id=user.user_id,
            academic_interests=["考研", "数学", "算法"],
            career_interests=["软件工程师", "数据科学家"],
            hobby_interests=["阅读", "音乐", "跑步"]
        )
    )
    profile_service.update_scenes(
        SceneSelectionRequest(user_id=user.user_id, scenes=["考研自习室"])
    )
    profile_service.generate_initial_profile(user.user_id)
    print("用户画像生成完成")
    
    # 3. 查看场景配置详情
    print("\n3. 查看考研自习室场景配置:")
    print("-" * 60)
    exam_config = scene_service.get_scene_config("考研自习室")
    print(f"场景名称: {exam_config.display_name}")
    print(f"场景描述: {exam_config.description}")
    print(f"匹配权重: {exam_config.match_weights}")
    print(f"AI介入阈值: {exam_config.intervention_threshold}秒")
    print(f"每小时最大介入次数: {exam_config.max_interventions_per_hour}次")
    print(f"话题模板数量: {len(exam_config.topic_templates)}个")
    print("话题模板示例:")
    for i, template in enumerate(exam_config.topic_templates[:3], 1):
        print(f"  {i}. {template}")
    
    # 4. 切换场景
    print("\n4. 切换到职业咨询室场景:")
    print("-" * 60)
    scene_service.switch_scene(user.user_id, "职业咨询室", priority=0.8)
    print("场景切换成功")
    
    profile = profile_service.get_profile(user.user_id)
    print(f"当前关注的场景: {profile.current_scenes}")
    print(f"场景优先级: {profile.scene_priorities}")
    
    # 5. 查看职业咨询室配置
    print("\n5. 查看职业咨询室场景配置:")
    print("-" * 60)
    career_config = scene_service.get_scene_config("职业咨询室")
    print(f"场景名称: {career_config.display_name}")
    print(f"匹配权重: {career_config.match_weights}")
    print("话题模板示例:")
    for i, template in enumerate(career_config.topic_templates[:3], 1):
        print(f"  {i}. {template}")
    
    # 6. 添加更多场景
    print("\n6. 添加心理树洞和兴趣社群场景:")
    print("-" * 60)
    scene_service.switch_scene(user.user_id, "心理树洞", priority=0.6)
    scene_service.switch_scene(user.user_id, "兴趣社群", priority=0.9)
    
    profile = profile_service.get_profile(user.user_id)
    print(f"当前关注的场景: {profile.current_scenes}")
    print(f"场景优先级: {profile.scene_priorities}")
    
    # 7. 更新场景优先级
    print("\n7. 更新考研自习室的优先级:")
    print("-" * 60)
    scene_service.update_scene_priority(user.user_id, "考研自习室", priority=1.0)
    
    profile = profile_service.get_profile(user.user_id)
    print(f"更新后的场景优先级: {profile.scene_priorities}")
    
    # 8. 比较不同场景的匹配权重
    print("\n8. 比较不同场景的匹配权重:")
    print("-" * 60)
    for scene_name in ["考研自习室", "职业咨询室", "心理树洞", "兴趣社群"]:
        weights = scene_service.get_match_weights(scene_name)
        print(f"\n{scene_name}:")
        print(f"  人格权重: {weights['personality']:.2f}")
        print(f"  兴趣权重: {weights['interest']:.2f}")
        print(f"  场景权重: {weights['scene']:.2f}")
        print(f"  情感权重: {weights['emotion']:.2f}")
    
    # 9. 查看心理树洞的特殊配置
    print("\n9. 心理树洞场景的特殊配置:")
    print("-" * 60)
    mental_config = scene_service.get_scene_config("心理树洞")
    print(f"AI介入阈值: {mental_config.intervention_threshold}秒 (更长的等待时间)")
    print(f"每小时最大介入次数: {mental_config.max_interventions_per_hour}次 (更少的介入)")
    print(f"情感权重: {mental_config.match_weights['emotion']:.2f} (最高)")
    
    # 10. 移除场景
    print("\n10. 移除心理树洞场景:")
    print("-" * 60)
    scene_service.remove_scene(user.user_id, "心理树洞")
    
    profile = profile_service.get_profile(user.user_id)
    print(f"移除后的场景: {profile.current_scenes}")
    print(f"场景优先级: {profile.scene_priorities}")
    
    # 11. 验证场景
    print("\n11. 验证场景名称:")
    print("-" * 60)
    test_scenes = ["考研自习室", "无效场景", "职业咨询室", "测试场景"]
    for scene in test_scenes:
        is_valid = scene_service.validate_scene(scene)
        print(f"{scene}: {'✓ 有效' if is_valid else '✗ 无效'}")
    
    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
