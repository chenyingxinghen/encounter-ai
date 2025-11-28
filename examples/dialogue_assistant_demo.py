"""AI对话助手服务演示"""
from datetime import datetime, timedelta
from src.services.dialogue_assistant_service import DialogueAssistantService
from src.services.conversation_service import ConversationService
from src.models.conversation import (
    ConversationCreateRequest,
    MessageSendRequest,
    Message
)


def main():
    """演示AI对话助手功能"""
    
    print("=" * 60)
    print("AI对话助手服务演示")
    print("=" * 60)
    
    # 初始化服务
    dialogue_service = DialogueAssistantService()
    conversation_service = ConversationService()
    
    # 1. 创建对话
    print("\n1. 创建对话")
    print("-" * 60)
    
    create_request = ConversationCreateRequest(
        user_a_id="user_001",
        user_b_id="user_002",
        scene="考研自习室"
    )
    conversation = conversation_service.create_conversation(create_request)
    print(f"创建对话: {conversation.conversation_id}")
    print(f"场景: {conversation.scene}")
    print(f"参与者: {conversation.user_a_id}, {conversation.user_b_id}")
    
    # 2. 发送一些消息
    print("\n2. 发送消息")
    print("-" * 60)
    
    messages = [
        ("user_001", "你好，我是准备考研的学生"),
        ("user_002", "你好，我也在准备考研"),
        ("user_001", "你目标院校是哪里？"),
    ]
    
    for sender_id, content in messages:
        msg_request = MessageSendRequest(
            conversation_id=conversation.conversation_id,
            sender_id=sender_id,
            content=content
        )
        msg = conversation_service.send_message(msg_request)
        dialogue_service.update_last_message_time(
            conversation.conversation_id,
            msg.timestamp
        )
        print(f"{sender_id}: {content}")
    
    # 3. 模拟沉默（15秒以上无消息）
    print("\n3. 模拟沉默场景")
    print("-" * 60)
    
    # 将最后消息时间设置为20秒前
    dialogue_service.last_message_time[conversation.conversation_id] = \
        datetime.now() - timedelta(seconds=20)
    
    # 获取最近消息
    recent_messages = conversation_service.messages.get(conversation.conversation_id, [])
    
    # 检测沉默
    is_silent, silence_type = dialogue_service.detect_silence(
        conversation.conversation_id,
        recent_messages
    )
    
    print(f"检测到沉默: {is_silent}")
    if silence_type:
        print(f"沉默类型: {silence_type.type}")
        print(f"置信度: {silence_type.confidence:.2f}")
    
    # 4. 检查是否应该介入
    print("\n4. 检查AI介入条件")
    print("-" * 60)
    
    should = dialogue_service.should_intervene(
        conversation.conversation_id,
        "user_001"
    )
    print(f"应该介入: {should}")
    
    if should:
        # 5. 生成话题建议
        print("\n5. 生成话题建议")
        print("-" * 60)
        
        suggestion = dialogue_service.generate_topic_suggestion(
            conversation.conversation_id,
            conversation.scene,
            recent_messages,
            silence_type
        )
        print(f"AI建议: {suggestion}")
        
        # 6. 记录介入
        print("\n6. 记录AI介入")
        print("-" * 60)
        
        intervention = dialogue_service.record_intervention(
            conversation_id=conversation.conversation_id,
            trigger_type="silence",
            intervention_type="topic_suggestion",
            content=suggestion
        )
        print(f"介入ID: {intervention.intervention_id}")
        print(f"触发类型: {intervention.trigger_type}")
        print(f"介入类型: {intervention.intervention_type}")
        print(f"介入时间: {intervention.timestamp}")
        
        # 更新对话统计
        conversation_service.increment_ai_intervention_count(conversation.conversation_id)
        conversation_service.increment_silence_count(conversation.conversation_id)
        
        # 7. 模拟用户响应
        print("\n7. 用户响应AI建议")
        print("-" * 60)
        
        dialogue_service.update_user_response(
            intervention.intervention_id,
            conversation.conversation_id,
            "accepted"
        )
        print("用户接受了AI建议")
    
    # 8. 测试情绪支持
    print("\n8. 测试情绪支持功能")
    print("-" * 60)
    
    # 创建带有焦虑情绪的消息
    anxious_msg = Message(
        message_id="msg_anxious",
        conversation_id=conversation.conversation_id,
        sender_id="user_002",
        content="我有点紧张，不知道该说什么",
        emotion="anxious",
        emotion_intensity=0.8,
        timestamp=datetime.now()
    )
    
    support = dialogue_service.provide_emotional_support(
        "user_002",
        "anxious",
        [anxious_msg]
    )
    print(f"情绪支持: {support}")
    
    # 9. 测试用户偏好
    print("\n9. 测试用户偏好管理")
    print("-" * 60)
    
    # 用户拒绝AI介入
    preference = dialogue_service.record_user_preference(
        "user_001",
        ai_intervention_enabled=False
    )
    print(f"用户 {preference.user_id} 禁用了AI介入")
    print(f"拒绝次数: {preference.rejection_count}")
    
    # 再次检查是否应该介入
    should_after_disable = dialogue_service.should_intervene(
        conversation.conversation_id,
        "user_001"
    )
    print(f"禁用后是否介入: {should_after_disable}")
    
    # 10. 查看介入历史
    print("\n10. 查看AI介入历史")
    print("-" * 60)
    
    history = dialogue_service.get_intervention_history(conversation.conversation_id)
    print(f"总介入次数: {len(history)}")
    for i, intervention in enumerate(history, 1):
        print(f"\n介入 {i}:")
        print(f"  触发类型: {intervention.trigger_type}")
        print(f"  介入类型: {intervention.intervention_type}")
        print(f"  内容: {intervention.content}")
        print(f"  用户响应: {intervention.user_response}")
        print(f"  时间: {intervention.timestamp}")
    
    # 11. 测试介入频率控制
    print("\n11. 测试介入频率控制（冷却期）")
    print("-" * 60)
    
    # 启用AI介入
    dialogue_service.record_user_preference("user_001", True)
    
    # 尝试立即再次介入
    should_immediate = dialogue_service.should_intervene(
        conversation.conversation_id,
        "user_001"
    )
    print(f"立即再次介入: {should_immediate}")
    print(f"原因: 20分钟冷却期内不允许重复介入")
    
    # 12. 测试不同场景的话题建议
    print("\n12. 测试不同场景的话题建议")
    print("-" * 60)
    
    scenes = ["考研自习室", "职业咨询室", "心理树洞", "兴趣社群"]
    for scene in scenes:
        suggestion = dialogue_service.generate_topic_suggestion(
            conversation.conversation_id,
            scene,
            [],
            None
        )
        print(f"{scene}: {suggestion}")
    
    # 13. 获取沉默时长
    print("\n13. 获取当前沉默时长")
    print("-" * 60)
    
    duration = dialogue_service.get_silence_duration(conversation.conversation_id)
    print(f"当前沉默时长: {duration:.1f} 秒")
    
    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
