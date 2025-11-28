"""用户画像动态更新服务演示"""
from datetime import datetime
from src.services.profile_update_service import ProfileUpdateService
from src.services.user_profile_service import UserProfileService
from src.services.matching_service import MatchingService
from src.models.user import (
    UserRegistrationRequest,
    BigFiveScores
)
from src.models.conversation import Message


def print_section(title):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_profile_summary(profile):
    """打印画像摘要"""
    print(f"情绪稳定性: {profile.emotion_stability:.2%}")
    print(f"社交能量: {profile.social_energy:.2%}")
    print(f"学业兴趣: {', '.join(profile.academic_interests) if profile.academic_interests else '无'}")
    print(f"职业兴趣: {', '.join(profile.career_interests) if profile.career_interests else '无'}")
    print(f"兴趣爱好: {', '.join(profile.hobby_interests) if profile.hobby_interests else '无'}")
    if profile.big_five:
        print(f"\n大五人格:")
        print(f"  神经质: {profile.big_five.neuroticism:.2%}")
        print(f"  宜人性: {profile.big_five.agreeableness:.2%}")
        print(f"  外向性: {profile.big_five.extraversion:.2%}")
        print(f"  开放性: {profile.big_five.openness:.2%}")
        print(f"  尽责性: {profile.big_five.conscientiousness:.2%}")


def main():
    """主函数"""
    print_section("用户画像动态更新服务演示")
    
    # 1. 初始化服务
    print("1. 初始化服务...")
    user_profile_service = UserProfileService()
    matching_service = MatchingService(user_profile_service=user_profile_service)
    profile_update_service = ProfileUpdateService(
        user_profile_service=user_profile_service,
        matching_service=matching_service
    )
    print("✓ 服务初始化完成")
    
    # 2. 创建测试用户
    print_section("创建测试用户")
    
    request = UserRegistrationRequest(
        username="小明",
        email="xiaoming@example.com",
        password="password123",
        school="清华大学",
        major="计算机科学",
        grade=3
    )
    
    user = user_profile_service.register_user(request)
    print(f"✓ 用户创建成功: {user.username} ({user.user_id})")
    
    # 设置初始画像
    user_profile_service.update_profile(user.user_id, {
        'mbti_type': 'INFP',
        'big_five': BigFiveScores(
            neuroticism=0.5,
            agreeableness=0.6,
            extraversion=0.4,
            openness=0.7,
            conscientiousness=0.5
        ),
        'current_scenes': ['考研自习室', '兴趣社群'],
        'academic_interests': ['数学'],
        'hobby_interests': ['阅读']
    })
    
    print("\n初始画像:")
    profile = user_profile_service.get_profile(user.user_id)
    print_profile_summary(profile)
    
    # 3. 模拟对话
    print_section("模拟对话场景")
    
    messages = [
        Message(
            message_id="msg_1",
            conversation_id="conv_123",
            sender_id=user.user_id,
            content="我最近在准备考研，每天学习很充实",
            message_type="text",
            timestamp=datetime.now()
        ),
        Message(
            message_id="msg_2",
            conversation_id="conv_123",
            sender_id="user_2",
            content="加油！我也在考研，目标是北大",
            message_type="text",
            timestamp=datetime.now()
        ),
        Message(
            message_id="msg_3",
            conversation_id="conv_123",
            sender_id=user.user_id,
            content="太好了！我感觉很开心能找到志同道合的伙伴，我们可以一起复习",
            message_type="text",
            timestamp=datetime.now()
        ),
        Message(
            message_id="msg_4",
            conversation_id="conv_123",
            sender_id="user_2",
            content="好的！我平时喜欢看电影和听音乐放松",
            message_type="text",
            timestamp=datetime.now()
        ),
        Message(
            message_id="msg_5",
            conversation_id="conv_123",
            sender_id=user.user_id,
            content="我也喜欢音乐！我们兴趣很相似",
            message_type="text",
            timestamp=datetime.now()
        )
    ]
    
    print("对话内容:")
    for i, msg in enumerate(messages, 1):
        sender = "小明" if msg.sender_id == user.user_id else "对方"
        print(f"{i}. {sender}: {msg.content}")
    
    # 4. 分析对话
    print_section("分析对话内容")
    
    conversation_data = profile_update_service.analyze_conversation(
        conversation_id="conv_123",
        messages=messages
    )
    
    print(f"消息数量: {conversation_data['message_count']}")
    print(f"提取的话题: {', '.join(conversation_data['topics'])}")
    print(f"提取的兴趣: {', '.join(conversation_data['interests'])}")
    
    if user.user_id in conversation_data['emotions']:
        user_emotions = conversation_data['emotions'][user.user_id]
        print(f"\n小明的情绪分析:")
        print(f"  积极情绪: {user_emotions.get('positive', 0)} 次")
        print(f"  消极情绪: {user_emotions.get('negative', 0)} 次")
        print(f"  焦虑情绪: {user_emotions.get('anxious', 0)} 次")
        print(f"  中性情绪: {user_emotions.get('neutral', 0)} 次")
    
    # 5. 更新画像
    print_section("更新用户画像")
    
    update_result = profile_update_service.update_profile_from_conversation(
        user_id=user.user_id,
        conversation_data=conversation_data
    )
    
    print(f"兴趣标签已更新: {'是' if update_result['interests_updated'] else '否'}")
    print(f"情感特征已更新: {'是' if update_result['emotions_updated'] else '否'}")
    print(f"画像变化程度: {update_result['change_magnitude']:.2%}")
    print(f"是否需要通知: {'是' if update_result['should_notify'] else '否'}")
    print(f"匹配度已重新计算: {'是' if update_result['match_recalculated'] else '否'}")
    
    # 6. 显示更新后的画像
    print_section("更新后的画像")
    
    updated_profile = user_profile_service.get_profile(user.user_id)
    print_profile_summary(updated_profile)
    
    # 7. 生成通知
    if update_result['should_notify']:
        print_section("生成画像更新通知")
        
        notification = profile_update_service.generate_profile_update_notification(
            user_id=user.user_id,
            update_result=update_result
        )
        
        if notification:
            print(f"标题: {notification['title']}")
            print(f"内容: {notification['message']}")
            print(f"操作: {notification['action']['label']}")
    
    # 8. 测试行为模式更新
    print_section("根据行为模式更新人格特质")
    
    behavior_data = {
        'emotion_volatility': 0.3,  # 低情绪波动
        'interaction_friendliness': 0.8,  # 高友好度
        'social_activity': 0.7,  # 高社交活跃度
        'topic_diversity': 0.6,  # 中等话题多样性
        'response_timeliness': 0.9  # 高及时性
    }
    
    print("行为数据:")
    for key, value in behavior_data.items():
        print(f"  {key}: {value:.2%}")
    
    print("\n更新前的大五人格:")
    if updated_profile.big_five:
        print(f"  神经质: {updated_profile.big_five.neuroticism:.2%}")
        print(f"  宜人性: {updated_profile.big_five.agreeableness:.2%}")
        print(f"  外向性: {updated_profile.big_five.extraversion:.2%}")
        print(f"  开放性: {updated_profile.big_five.openness:.2%}")
        print(f"  尽责性: {updated_profile.big_five.conscientiousness:.2%}")
    
    updated_scores = profile_update_service.update_personality_from_behavior(
        user_id=user.user_id,
        behavior_data=behavior_data
    )
    
    print("\n更新后的大五人格:")
    print(f"  神经质: {updated_scores.neuroticism:.2%}")
    print(f"  宜人性: {updated_scores.agreeableness:.2%}")
    print(f"  外向性: {updated_scores.extraversion:.2%}")
    print(f"  开放性: {updated_scores.openness:.2%}")
    print(f"  尽责性: {updated_scores.conscientiousness:.2%}")
    
    print_section("演示完成")
    print("✓ 用户画像动态更新功能演示成功！")
    print("\n主要功能:")
    print("  1. 对话内容分析 - 提取话题、情绪、兴趣")
    print("  2. 关键信息提取 - 识别用户兴趣和情感状态")
    print("  3. 兴趣标签自动更新 - 根据对话内容更新兴趣")
    print("  4. 情感特征更新 - 动态调整情绪稳定性和社交能量")
    print("  5. 匹配度重新计算触发 - 画像变化时自动重新匹配")
    print("  6. 画像更新通知 - 变化达到阈值时通知用户")
    print("  7. 行为模式分析 - 根据行为动态调整人格特质")


if __name__ == '__main__':
    main()
