"""对话质量监测服务演示"""
from datetime import datetime, timedelta
from src.services.conversation_service import ConversationService
from src.services.conversation_quality_service import ConversationQualityService
from src.models.conversation import (
    ConversationCreateRequest,
    MessageSendRequest
)
from src.models.quality import (
    QualityMonitoringRequest,
    SatisfactionFeedbackRequest
)


def main():
    """演示对话质量监测功能"""
    print("=" * 60)
    print("对话质量监测服务演示")
    print("=" * 60)
    
    # 初始化服务
    conversation_service = ConversationService()
    quality_service = ConversationQualityService(conversation_service)
    
    # 1. 创建对话
    print("\n1. 创建对话")
    create_request = ConversationCreateRequest(
        user_a_id="user_001",
        user_b_id="user_002",
        scene="考研自习室"
    )
    conversation = conversation_service.create_conversation(create_request)
    print(f"   对话ID: {conversation.conversation_id}")
    print(f"   场景: {conversation.scene}")
    
    # 2. 模拟对话消息
    print("\n2. 模拟对话消息")
    messages_data = [
        ("user_001", "你好！我也在准备考研，你考哪个学校？"),
        ("user_002", "你好！我准备考清华大学计算机系，你呢？"),
        ("user_001", "我也是考计算机！不过我目标是北大。你复习到哪里了？"),
        ("user_002", "数据结构刚复习完，现在在看操作系统。感觉内容好多啊。"),
        ("user_001", "是啊，我也觉得操作系统很难。你用的什么教材？"),
        ("user_002", "我用的是王道的操作系统，配合视频课程一起看。"),
        ("user_001", "王道的书确实不错！我也在用。你每天学习多长时间？"),
        ("user_002", "我一般早上8点到图书馆，晚上10点回去，中间休息2小时左右。"),
        ("user_001", "你的学习时间好规律！我也想养成这样的习惯。"),
        ("user_002", "坚持下来就好了。对了，你有没有找研友一起学习？"),
        ("user_001", "还没有呢，一直是自己学。有研友的话确实会更有动力。"),
        ("user_002", "那我们可以互相监督啊！每天打卡分享进度。"),
        ("user_001", "好主意！那我们建个群吧，每天晚上总结一下学习内容。"),
        ("user_002", "可以！我觉得这样能帮助我们保持学习状态。"),
        ("user_001", "嗯嗯，那就这么定了。加油！"),
    ]
    
    for sender_id, content in messages_data:
        send_request = MessageSendRequest(
            conversation_id=conversation.conversation_id,
            sender_id=sender_id,
            content=content
        )
        message = conversation_service.send_message(send_request)
        print(f"   [{sender_id}]: {content[:30]}...")
    
    # 3. 实时监测对话质量
    print("\n3. 实时监测对话质量")
    monitoring_request = QualityMonitoringRequest(
        conversation_id=conversation.conversation_id
    )
    metrics = quality_service.monitor_conversation_quality(monitoring_request)
    
    print(f"   话题深度得分: {metrics.topic_depth_score:.2f}/10")
    print(f"   话题数量: {metrics.topic_count}")
    print(f"   平均话题持续时间: {metrics.average_topic_duration:.2f} 条消息")
    print(f"   回应一致性得分: {metrics.response_consistency_score:.2f}")
    print(f"   平均回应时间: {metrics.average_response_time:.2f} 秒")
    print(f"   情感同步性得分: {metrics.emotion_sync_score:.2f}")
    print(f"   情绪一致率: {metrics.emotion_alignment_rate:.2f}")
    print(f"   整体质量得分: {metrics.overall_quality_score:.2f}/10")
    
    # 4. 检测低质量对话
    print("\n4. 检测低质量对话")
    is_low_quality, suggestions = quality_service.detect_low_quality_conversation(
        conversation.conversation_id
    )
    print(f"   是否低质量对话: {'是' if is_low_quality else '否'}")
    if suggestions:
        print("   改进建议:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"     {i}. {suggestion}")
    
    # 5. 收集满意度反馈
    print("\n5. 收集满意度反馈")
    
    # 用户A的反馈
    feedback_request_a = SatisfactionFeedbackRequest(
        conversation_id=conversation.conversation_id,
        user_id="user_001",
        satisfaction_score=4.5,
        feedback_text="聊得很开心，找到了志同道合的研友！",
        feedback_tags=["话题有趣", "聊得投机", "对方友善"]
    )
    feedback_a = quality_service.collect_satisfaction_feedback(feedback_request_a)
    print(f"   用户A满意度: {feedback_a.satisfaction_score}/5")
    print(f"   用户A反馈: {feedback_a.feedback_text}")
    print(f"   用户A标签: {', '.join(feedback_a.feedback_tags)}")
    
    # 用户B的反馈
    feedback_request_b = SatisfactionFeedbackRequest(
        conversation_id=conversation.conversation_id,
        user_id="user_002",
        satisfaction_score=4.8,
        feedback_text="很高兴认识你，一起加油！",
        feedback_tags=["话题有趣", "学到东西", "对方友善"]
    )
    feedback_b = quality_service.collect_satisfaction_feedback(feedback_request_b)
    print(f"   用户B满意度: {feedback_b.satisfaction_score}/5")
    print(f"   用户B反馈: {feedback_b.feedback_text}")
    print(f"   用户B标签: {', '.join(feedback_b.feedback_tags)}")
    
    # 6. 生成对话质量报告
    print("\n6. 生成对话质量报告")
    
    # 结束对话
    from src.models.conversation import ConversationStatusUpdateRequest
    update_request = ConversationStatusUpdateRequest(
        conversation_id=conversation.conversation_id,
        status="ended"
    )
    conversation_service.update_conversation_status(update_request)
    
    # 生成报告
    report = quality_service.generate_conversation_report(conversation.conversation_id)
    
    print(f"   报告ID: {report.report_id}")
    print(f"   对话时长: {report.duration_seconds:.0f} 秒")
    print(f"   消息总数: {report.message_count}")
    print(f"   用户A满意度: {report.user_a_satisfaction}/5")
    print(f"   用户B满意度: {report.user_b_satisfaction}/5")
    print(f"   是否低质量对话: {'是' if report.is_low_quality else '否'}")
    
    if report.suggestions:
        print("   改进建议:")
        for i, suggestion in enumerate(report.suggestions, 1):
            print(f"     {i}. {suggestion}")
    
    # 7. 演示低质量对话场景
    print("\n7. 演示低质量对话场景")
    
    # 创建一个低质量对话
    low_quality_request = ConversationCreateRequest(
        user_a_id="user_003",
        user_b_id="user_004",
        scene="兴趣社群"
    )
    low_quality_conv = conversation_service.create_conversation(low_quality_request)
    print(f"   对话ID: {low_quality_conv.conversation_id}")
    
    # 发送一些简短、无深度的消息
    short_messages = [
        ("user_003", "嗨"),
        ("user_004", "你好"),
        ("user_003", "在吗"),
        ("user_004", "在"),
        ("user_003", "干嘛呢"),
        ("user_004", "没事"),
        ("user_003", "哦"),
        ("user_004", "嗯"),
        ("user_003", "好吧"),
        ("user_004", "嗯嗯"),
    ]
    
    for sender_id, content in short_messages:
        send_request = MessageSendRequest(
            conversation_id=low_quality_conv.conversation_id,
            sender_id=sender_id,
            content=content
        )
        conversation_service.send_message(send_request)
    
    # 监测质量
    low_quality_monitoring = QualityMonitoringRequest(
        conversation_id=low_quality_conv.conversation_id
    )
    low_quality_metrics = quality_service.monitor_conversation_quality(low_quality_monitoring)
    
    print(f"   整体质量得分: {low_quality_metrics.overall_quality_score:.2f}/10")
    print(f"   话题深度得分: {low_quality_metrics.topic_depth_score:.2f}/10")
    
    # 检测低质量
    is_low, suggestions = quality_service.detect_low_quality_conversation(
        low_quality_conv.conversation_id
    )
    print(f"   是否低质量对话: {'是' if is_low else '否'}")
    if suggestions:
        print("   改进建议:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"     {i}. {suggestion}")
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
