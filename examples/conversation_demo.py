"""对话系统演示示例"""
from datetime import datetime
from src.services.conversation_service import ConversationService
from src.models.conversation import (
    ConversationCreateRequest,
    MessageSendRequest,
    ConversationHistoryRequest,
    ConversationStatusUpdateRequest
)


def main():
    """演示对话系统的主要功能"""
    print("=" * 60)
    print("对话系统演示")
    print("=" * 60)
    
    # 初始化服务
    service = ConversationService()
    
    # 1. 创建对话
    print("\n1. 创建对话")
    print("-" * 60)
    create_request = ConversationCreateRequest(
        user_a_id="user_001",
        user_b_id="user_002",
        scene="考研自习室"
    )
    conversation = service.create_conversation(create_request)
    print(f"对话ID: {conversation.conversation_id}")
    print(f"参与者: {conversation.user_a_id} 和 {conversation.user_b_id}")
    print(f"场景: {conversation.scene}")
    print(f"状态: {conversation.status}")
    print(f"开始时间: {conversation.started_at}")
    
    # 2. 发送消息
    print("\n2. 发送消息")
    print("-" * 60)
    
    # 用户A发送消息
    msg1_request = MessageSendRequest(
        conversation_id=conversation.conversation_id,
        sender_id="user_001",
        content="你好！你也在准备考研吗？",
        message_type="text"
    )
    msg1 = service.send_message(msg1_request)
    print(f"[{msg1.timestamp.strftime('%H:%M:%S')}] {msg1.sender_id}: {msg1.content}")
    
    # 用户B回复
    msg2_request = MessageSendRequest(
        conversation_id=conversation.conversation_id,
        sender_id="user_002",
        content="是的！我在准备计算机专业的考研，你呢？",
        message_type="text"
    )
    msg2 = service.send_message(msg2_request)
    print(f"[{msg2.timestamp.strftime('%H:%M:%S')}] {msg2.sender_id}: {msg2.content}")
    
    # 用户A继续对话
    msg3_request = MessageSendRequest(
        conversation_id=conversation.conversation_id,
        sender_id="user_001",
        content="我也是计算机专业！目标是清华大学，你的目标院校是哪里？",
        message_type="text"
    )
    msg3 = service.send_message(msg3_request)
    print(f"[{msg3.timestamp.strftime('%H:%M:%S')}] {msg3.sender_id}: {msg3.content}")
    
    # 用户B回复
    msg4_request = MessageSendRequest(
        conversation_id=conversation.conversation_id,
        sender_id="user_002",
        content="我的目标是北京大学。我们可以互相交流学习经验！",
        message_type="text"
    )
    msg4 = service.send_message(msg4_request)
    print(f"[{msg4.timestamp.strftime('%H:%M:%S')}] {msg4.sender_id}: {msg4.content}")
    
    # 3. 查看对话统计
    print("\n3. 对话统计")
    print("-" * 60)
    conversation = service.get_conversation(conversation.conversation_id)
    print(f"消息总数: {conversation.message_count}")
    print(f"沉默次数: {conversation.silence_count}")
    print(f"AI介入次数: {conversation.ai_intervention_count}")
    
    # 4. 获取对话历史
    print("\n4. 对话历史记录")
    print("-" * 60)
    history_request = ConversationHistoryRequest(
        conversation_id=conversation.conversation_id,
        limit=10,
        offset=0
    )
    messages = service.get_conversation_history(history_request)
    print(f"共有 {len(messages)} 条消息（按时间倒序）:")
    for msg in reversed(messages):  # 反转以按时间正序显示
        print(f"  [{msg.timestamp.strftime('%H:%M:%S')}] {msg.sender_id}: {msg.content}")
    
    # 5. 模拟沉默检测
    print("\n5. 沉默检测")
    print("-" * 60)
    service.increment_silence_count(conversation.conversation_id)
    conversation = service.get_conversation(conversation.conversation_id)
    print(f"检测到沉默，沉默次数: {conversation.silence_count}")
    
    # 6. 模拟AI介入
    print("\n6. AI助手介入")
    print("-" * 60)
    service.increment_ai_intervention_count(conversation.conversation_id)
    conversation = service.get_conversation(conversation.conversation_id)
    print(f"AI助手介入，介入次数: {conversation.ai_intervention_count}")
    
    # 7. 更新质量指标
    print("\n7. 更新对话质量指标")
    print("-" * 60)
    conversation = service.update_quality_metrics(
        conversation_id=conversation.conversation_id,
        topic_depth_score=8.5,
        emotion_sync_score=0.92,
        satisfaction_score=4.5
    )
    print(f"话题深度得分: {conversation.topic_depth_score}/10")
    print(f"情感同步性得分: {conversation.emotion_sync_score}")
    print(f"满意度得分: {conversation.satisfaction_score}/5")
    
    # 8. 获取用户的所有对话
    print("\n8. 获取用户的所有对话")
    print("-" * 60)
    
    # 创建另一个对话
    create_request2 = ConversationCreateRequest(
        user_a_id="user_001",
        user_b_id="user_003",
        scene="职业咨询室"
    )
    conversation2 = service.create_conversation(create_request2)
    
    user_conversations = service.get_user_conversations("user_001")
    print(f"用户 user_001 共有 {len(user_conversations)} 个对话:")
    for conv in user_conversations:
        other_user = conv.user_b_id if conv.user_a_id == "user_001" else conv.user_a_id
        print(f"  - 对话ID: {conv.conversation_id[:8]}... | 对方: {other_user} | 场景: {conv.scene} | 状态: {conv.status}")
    
    # 9. 暂停对话
    print("\n9. 暂停对话")
    print("-" * 60)
    pause_request = ConversationStatusUpdateRequest(
        conversation_id=conversation.conversation_id,
        status="paused"
    )
    conversation = service.update_conversation_status(pause_request)
    print(f"对话状态已更新为: {conversation.status}")
    
    # 10. 结束对话
    print("\n10. 结束对话")
    print("-" * 60)
    end_request = ConversationStatusUpdateRequest(
        conversation_id=conversation.conversation_id,
        status="ended"
    )
    conversation = service.update_conversation_status(end_request)
    print(f"对话状态已更新为: {conversation.status}")
    print(f"结束时间: {conversation.ended_at}")
    
    # 11. 按状态过滤对话
    print("\n11. 按状态过滤对话")
    print("-" * 60)
    active_conversations = service.get_user_conversations("user_001", status="active")
    ended_conversations = service.get_user_conversations("user_001", status="ended")
    print(f"活跃对话数: {len(active_conversations)}")
    print(f"已结束对话数: {len(ended_conversations)}")
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
