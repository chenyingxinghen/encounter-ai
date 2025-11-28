"""匹配算法优化演示"""
from datetime import datetime, timedelta
from src.models.user import (
    UserRegistrationRequest, MBTITestRequest, BigFiveTestRequest,
    InterestSelectionRequest, SceneSelectionRequest
)
from src.services.user_profile_service import UserProfileService
from src.services.matching_service import MatchingService
from src.services.algorithm_optimization_service import AlgorithmOptimizationService


def main():
    """演示匹配算法优化功能"""
    
    print("=" * 60)
    print("匹配算法优化演示")
    print("=" * 60)
    
    # 初始化服务
    profile_service = UserProfileService()
    matching_service = MatchingService(profile_service)
    optimization_service = AlgorithmOptimizationService(matching_service)
    
    # 创建测试用户
    print("\n1. 创建测试用户...")
    users = []
    for i in range(20):  # 增加用户数量以确保A/B测试有足够样本
        user = profile_service.register_user(
            UserRegistrationRequest(
                username=f"用户{i+1}",
                email=f"user{i+1}@example.com",
                password="password123",
                school="清华大学",
                major="计算机科学",
                grade=2
            )
        )
        
        profile_service.process_mbti_test(
            MBTITestRequest(user_id=user.user_id, answers=[3 + i % 2] * 60)
        )
        
        profile_service.process_big_five_test(
            BigFiveTestRequest(user_id=user.user_id, answers=[3 + i % 2] * 50)
        )
        
        profile_service.update_interests(
            InterestSelectionRequest(
                user_id=user.user_id,
                academic_interests=["考研", "数学"] if i % 2 == 0 else ["考研", "英语"],
                career_interests=["软件工程师"],
                hobby_interests=["阅读", "音乐"]
            )
        )
        
        profile_service.update_scenes(
            SceneSelectionRequest(user_id=user.user_id, scenes=["考研自习室"])
        )
        
        profile_service.generate_initial_profile(user.user_id)
        users.append(user)
    
    print(f"✓ 创建了 {len(users)} 个测试用户")
    
    # 演示1: 反馈数据收集
    print("\n" + "=" * 60)
    print("演示1: 反馈数据收集")
    print("=" * 60)
    
    # 进行匹配
    matches = matching_service.find_matches(
        users[0].user_id,
        "考研自习室",
        limit=5
    )
    
    print(f"\n为用户1找到 {len(matches)} 个匹配对象")
    
    # 收集反馈
    print("\n收集用户反馈...")
    for i, match in enumerate(matches):
        feedback = optimization_service.collect_feedback(
            user_id=users[0].user_id,
            match_id=match.match_id,
            scene="考研自习室",
            satisfaction_score=3.5 + i * 0.3,
            conversation_quality=7.0 + i * 0.5,
            match_accuracy=3.5 + i * 0.2,
            positive_aspects=["人格匹配", "话题相投"] if i % 2 == 0 else ["兴趣相同"],
            negative_aspects=["情绪不同步"] if i == 0 else [],
            suggestions="很好" if i > 2 else "可以改进"
        )
        
        print(f"  反馈 {i+1}: 满意度={feedback.satisfaction_score:.1f}, "
              f"质量={feedback.conversation_quality:.1f}, "
              f"准确度={feedback.match_accuracy:.1f}")
    
    # 演示2: 性能指标计算
    print("\n" + "=" * 60)
    print("演示2: 性能指标计算")
    print("=" * 60)
    
    metrics = optimization_service.calculate_performance_metrics(
        scene="考研自习室",
        period_days=7
    )
    
    print(f"\n场景: {metrics.scene}")
    print(f"统计周期: {metrics.period_start.strftime('%Y-%m-%d')} 至 "
          f"{metrics.period_end.strftime('%Y-%m-%d')}")
    print(f"总匹配数: {metrics.total_matches}")
    print(f"总反馈数: {metrics.total_feedbacks}")
    print(f"平均满意度: {metrics.avg_satisfaction:.2f} / 5.0")
    print(f"平均对话质量: {metrics.avg_conversation_quality:.2f} / 10.0")
    print(f"平均匹配准确度: {metrics.avg_match_accuracy:.2f} / 5.0")
    
    # 演示3: 权重动态调整
    print("\n" + "=" * 60)
    print("演示3: 权重动态调整")
    print("=" * 60)
    
    # 查看当前权重
    current_config = matching_service.get_scene_config("考研自习室")
    print("\n当前权重配置:")
    for key, value in current_config.match_weights.items():
        print(f"  {key}: {value:.2f}")
    
    # 调整权重
    new_weights = {
        'personality': 0.30,
        'interest': 0.40,
        'scene': 0.20,
        'emotion': 0.10
    }
    
    print("\n调整权重...")
    adjustment = optimization_service.adjust_weights(
        scene="考研自习室",
        new_weights=new_weights,
        reason="基于用户反馈，增加兴趣匹配权重"
    )
    
    print(f"✓ 权重调整完成")
    print(f"  调整ID: {adjustment.adjustment_id}")
    print(f"  调整原因: {adjustment.reason}")
    print(f"  调整前性能: {adjustment.performance_before:.2f}")
    
    print("\n新权重配置:")
    for key, value in new_weights.items():
        print(f"  {key}: {value:.2f}")
    
    # 添加更多反馈后评估调整效果
    print("\n收集更多反馈数据...")
    for i in range(5):
        optimization_service.collect_feedback(
            user_id=users[i+1].user_id,
            match_id=f"match_new_{i}",
            scene="考研自习室",
            satisfaction_score=4.0 + i * 0.1,
            conversation_quality=8.0 + i * 0.2,
            match_accuracy=4.0 + i * 0.1
        )
    
    print("\n评估权重调整效果...")
    evaluated = optimization_service.evaluate_weight_adjustment(adjustment.adjustment_id)
    print(f"  调整前性能: {evaluated.performance_before:.2f}")
    print(f"  调整后性能: {evaluated.performance_after:.2f}")
    print(f"  性能变化: {evaluated.performance_after - evaluated.performance_before:+.2f}")
    
    # 演示4: 自动权重调整
    print("\n" + "=" * 60)
    print("演示4: 自动权重调整")
    print("=" * 60)
    
    # 创建大量反馈，包含明显的问题
    print("\n模拟用户反馈（人格匹配问题）...")
    for i in range(15):
        optimization_service.collect_feedback(
            user_id=f"auto_user_{i}",
            match_id=f"auto_match_{i}",
            scene="职业咨询室",
            satisfaction_score=2.5,
            conversation_quality=5.0,
            match_accuracy=2.0,
            negative_aspects=["人格不匹配", "性格差异大"]
        )
    
    print("\n执行自动权重调整...")
    auto_adjustment = optimization_service.auto_adjust_weights("职业咨询室")
    
    if auto_adjustment:
        print(f"✓ 自动调整完成")
        print(f"  调整原因: {auto_adjustment.reason}")
        print(f"  新权重配置:")
        for key, value in auto_adjustment.new_weights.items():
            print(f"    {key}: {value:.2f}")
    else:
        print("  无需调整")
    
    # 演示5: A/B测试
    print("\n" + "=" * 60)
    print("演示5: A/B测试框架")
    print("=" * 60)
    
    # 创建A/B测试
    control_weights = {
        'personality': 0.25,
        'interest': 0.35,
        'scene': 0.30,
        'emotion': 0.10
    }
    
    treatment_weights = {
        'personality': 0.35,
        'interest': 0.30,
        'scene': 0.25,
        'emotion': 0.10
    }
    
    print("\n创建A/B测试...")
    test_config = optimization_service.create_ab_test(
        test_name="人格权重优化测试",
        scene="兴趣社群",
        control_weights=control_weights,
        treatment_weights=treatment_weights,
        traffic_split=0.5,
        min_sample_size=5  # 降低最小样本量以适应演示
    )
    
    print(f"✓ A/B测试创建成功")
    print(f"  测试ID: {test_config.test_id}")
    print(f"  测试名称: {test_config.test_name}")
    print(f"  场景: {test_config.scene}")
    print(f"  流量分配: {test_config.traffic_split * 100:.0f}% 实验组")
    
    # 分配用户到测试组
    print("\n分配用户到测试组...")
    group_counts = {"control": 0, "treatment": 0}
    for user in users:
        group = optimization_service.assign_to_test_group(
            test_config.test_id,
            user.user_id
        )
        group_counts[group] += 1
    
    print(f"  对照组: {group_counts['control']} 人")
    print(f"  实验组: {group_counts['treatment']} 人")
    
    # 收集测试数据
    print("\n收集测试数据...")
    for user in users:
        group = optimization_service.assign_to_test_group(
            test_config.test_id,
            user.user_id
        )
        
        # 模拟实验组表现更好
        if group == "treatment":
            satisfaction = 4.5
            quality = 8.5
        else:
            satisfaction = 3.5
            quality = 7.0
        
        optimization_service.collect_feedback(
            user_id=user.user_id,
            match_id=f"ab_test_match_{user.user_id}",
            scene="兴趣社群",
            satisfaction_score=satisfaction,
            conversation_quality=quality,
            match_accuracy=4.0
        )
    
    # 评估A/B测试
    print("\n评估A/B测试结果...")
    result = optimization_service.evaluate_ab_test(test_config.test_id)
    
    print(f"\n对照组:")
    print(f"  样本量: {result.control_sample_size}")
    print(f"  平均满意度: {result.control_avg_satisfaction:.2f}")
    print(f"  平均质量: {result.control_avg_quality:.2f}")
    
    print(f"\n实验组:")
    print(f"  样本量: {result.treatment_sample_size}")
    print(f"  平均满意度: {result.treatment_avg_satisfaction:.2f}")
    print(f"  平均质量: {result.treatment_avg_quality:.2f}")
    
    print(f"\n统计结果:")
    print(f"  统计显著性: {'是' if result.is_significant else '否'}")
    print(f"  p值: {result.p_value:.4f}")
    print(f"  获胜组: {result.winner}")
    print(f"  建议: {result.recommendation}")
    
    # 完成测试
    print("\n完成A/B测试...")
    optimization_service.complete_ab_test(test_config.test_id, apply_winner=True)
    print("✓ 测试已完成")
    
    # 演示6: 优化报告
    print("\n" + "=" * 60)
    print("演示6: 生成优化报告")
    print("=" * 60)
    
    report = optimization_service.generate_optimization_report("考研自习室")
    
    print(f"\n场景: {report['scene']}")
    
    print("\n性能指标:")
    metrics = report['performance_metrics']
    print(f"  总匹配数: {metrics['total_matches']}")
    print(f"  总反馈数: {metrics['total_feedbacks']}")
    print(f"  平均满意度: {metrics['avg_satisfaction']:.2f}")
    print(f"  平均对话质量: {metrics['avg_conversation_quality']:.2f}")
    
    print(f"\n最近权重调整: {len(report['recent_adjustments'])} 次")
    for adj in report['recent_adjustments'][:3]:
        print(f"  - {adj['reason']}")
    
    print(f"\n活跃A/B测试: {len(report['active_ab_tests'])} 个")
    
    print("\n优化建议:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
