"""心理健康监测服务演示"""
from datetime import datetime, timedelta

from src.services.mental_health_service import MentalHealthService
from src.models.mental_health import (
    EmotionAnalysisRequest,
    MentalHealthCheckRequest
)


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_emotion_analysis():
    """演示情感分析功能"""
    print_section("1. 情感分析演示")
    
    service = MentalHealthService()
    
    test_texts = [
        ("今天心情很好，学习进展顺利！", "user_001"),
        ("我感觉很焦虑，考试压力太大了", "user_002"),
        ("最近很抑郁，觉得很无助", "user_003"),
        ("我不想活了，太痛苦了", "user_004"),
    ]
    
    for text, user_id in test_texts:
        request = EmotionAnalysisRequest(text=text, user_id=user_id)
        emotion = service.analyze_emotion(request)
        
        print(f"文本: {text}")
        print(f"用户: {user_id}")
        print(f"情绪类型: {emotion.emotion_type}")
        print(f"情绪强度: {emotion.intensity:.2f}")
        print(f"检测关键词: {emotion.detected_keywords}")
        print(f"时间: {emotion.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)


def demo_mental_health_check():
    """演示心理健康检查功能"""
    print_section("2. 心理健康检查演示")
    
    service = MentalHealthService()
    user_id = "user_005"
    
    # 模拟用户发送多条消息
    messages = [
        "今天学习了新知识",
        "感觉有点焦虑",
        "压力好大啊",
        "又是焦虑的一天",
        "感觉很抑郁",
    ]
    
    print(f"模拟用户 {user_id} 发送消息:")
    for i, msg in enumerate(messages, 1):
        request = EmotionAnalysisRequest(text=msg, user_id=user_id)
        emotion = service.analyze_emotion(request)
        print(f"  {i}. {msg} -> {emotion.emotion_type} (强度: {emotion.intensity:.2f})")
        
        # 模拟不同天
        if i > 1:
            emotion.timestamp = datetime.now() - timedelta(days=5-i)
            service.emotion_states[user_id][-1] = emotion
    
    # 检查心理健康状态
    print(f"\n检查用户 {user_id} 的心理健康状态:")
    check_request = MentalHealthCheckRequest(user_id=user_id, check_recent_days=7)
    status = service.check_mental_health(check_request)
    
    print(f"  风险等级: {status.risk_level}")
    print(f"  情绪稳定性得分: {status.emotion_stability_score:.2f}")
    print(f"  持续负面情绪天数: {status.negative_emotion_days}")
    print(f"  最后负面情绪日期: {status.last_negative_emotion_date}")


def demo_resource_push():
    """演示资源推送功能"""
    print_section("3. 心理健康资源推送演示")
    
    service = MentalHealthService()
    user_id = "user_006"
    
    # 分析焦虑情绪
    request = EmotionAnalysisRequest(
        text="我很焦虑，考试压力太大了",
        user_id=user_id
    )
    emotion = service.analyze_emotion(request)
    
    print(f"检测到用户 {user_id} 的情绪: {emotion.emotion_type}")
    print(f"\n推送心理健康资源:")
    
    resources = service.push_mental_health_resources(user_id, emotion.emotion_type)
    
    for i, resource in enumerate(resources, 1):
        print(f"\n资源 {i}:")
        print(f"  类型: {resource.resource_type}")
        print(f"  标题: {resource.title}")
        print(f"  描述: {resource.description}")
        if resource.contact_info:
            print(f"  联系方式: {resource.contact_info}")
        if resource.url:
            print(f"  链接: {resource.url}")
        print(f"  优先级: {resource.priority}")


def demo_risk_alert():
    """演示风险预警功能"""
    print_section("4. 风险预警演示")
    
    service = MentalHealthService()
    user_id = "user_007"
    
    # 检测到自杀风险
    text = "我真的不想活了，活着太痛苦了"
    request = EmotionAnalysisRequest(text=text, user_id=user_id)
    emotion = service.analyze_emotion(request)
    
    print(f"检测到高风险内容:")
    print(f"  用户: {user_id}")
    print(f"  内容: {text}")
    print(f"  情绪类型: {emotion.emotion_type}")
    print(f"  情绪强度: {emotion.intensity:.2f}")
    print(f"  检测关键词: {emotion.detected_keywords}")
    
    # 创建风险预警
    alert = service.create_risk_alert(
        user_id=user_id,
        alert_type="suicide_risk",
        detected_content=text,
        confidence=emotion.intensity
    )
    
    print(f"\n创建风险预警:")
    print(f"  预警ID: {alert.alert_id}")
    print(f"  风险等级: {alert.risk_level}")
    print(f"  预警类型: {alert.alert_type}")
    print(f"  置信度: {alert.confidence:.2f}")
    print(f"  状态: {alert.status}")
    print(f"  已通知工作人员: {alert.notified_staff}")


def demo_anonymous_session():
    """演示匿名倾诉功能"""
    print_section("5. 匿名倾诉会话演示")
    
    service = MentalHealthService()
    user_id = "user_008"
    
    print(f"用户 {user_id} 进入心理树洞场景")
    
    # 创建匿名会话
    session = service.create_anonymous_session(user_id)
    
    print(f"\n创建匿名会话:")
    print(f"  会话ID: {session.session_id}")
    print(f"  真实用户ID: {session.user_id} (系统内部)")
    print(f"  匿名ID: {session.anonymous_id} (对外显示)")
    print(f"  场景: {session.scene}")
    print(f"  状态: {'活跃' if session.is_active else '已结束'}")
    print(f"  创建时间: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 结束会话
    print(f"\n用户结束匿名会话...")
    result = service.end_anonymous_session(session.session_id)
    
    if result:
        updated_session = service.anonymous_sessions[session.session_id]
        print(f"  会话已结束")
        print(f"  结束时间: {updated_session.ended_at.strftime('%Y-%m-%d %H:%M:%S')}")


def demo_professional_referral():
    """演示专业资源转介功能"""
    print_section("6. 专业资源转介演示")
    
    service = MentalHealthService()
    user_id = "user_009"
    
    # 模拟持续负面情绪
    print(f"用户 {user_id} 持续负面情绪7天以上")
    
    # 创建专业转介
    referral = service.create_professional_referral(
        user_id=user_id,
        referral_type="counseling",
        reason="持续负面情绪超过7天",
        urgency="high"
    )
    
    print(f"\n创建专业转介:")
    print(f"  转介ID: {referral.referral_id}")
    print(f"  用户ID: {referral.user_id}")
    print(f"  转介类型: {referral.referral_type}")
    print(f"  原因: {referral.reason}")
    print(f"  紧急程度: {referral.urgency}")
    print(f"  联系方式: {referral.contact_info}")
    print(f"  状态: {referral.status}")
    print(f"  创建时间: {referral.created_at.strftime('%Y-%m-%d %H:%M:%S')}")


def demo_comprehensive_monitoring():
    """演示综合监测功能"""
    print_section("7. 综合监测演示")
    
    service = MentalHealthService()
    
    test_cases = [
        ("user_010", "今天学习了新知识，感觉不错", "正常情况"),
        ("user_011", "我很焦虑，考试压力太大", "焦虑情况"),
        ("user_012", "我不想活了，太痛苦了", "严重风险"),
    ]
    
    for user_id, text, scenario in test_cases:
        print(f"\n场景: {scenario}")
        print(f"用户: {user_id}")
        print(f"文本: {text}")
        
        result = service.monitor_and_respond(user_id, text)
        
        print(f"\n监测结果:")
        print(f"  情绪检测: {'是' if result['emotion_detected'] else '否'}")
        if result['emotion_detected']:
            emotion = result['emotion_state']
            print(f"  情绪类型: {emotion.emotion_type}")
            print(f"  情绪强度: {emotion.intensity:.2f}")
        
        health = result['health_status']
        print(f"  风险等级: {health.risk_level}")
        print(f"  负面情绪天数: {health.negative_emotion_days}")
        
        print(f"  资源推送: {len(result['resources_pushed'])} 个")
        print(f"  创建预警: {'是' if result['alert_created'] else '否'}")
        print(f"  创建转介: {'是' if result['referral_created'] else '否'}")
        
        if result['alert_created']:
            alert = result['alert']
            print(f"    预警类型: {alert.alert_type}")
            print(f"    风险等级: {alert.risk_level}")
        
        if result['referral_created']:
            referral = result['referral']
            print(f"    转介类型: {referral.referral_type}")
            print(f"    紧急程度: {referral.urgency}")
        
        print("-" * 60)


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  心理健康监测与支持服务演示")
    print("="*60)
    
    try:
        demo_emotion_analysis()
        demo_mental_health_check()
        demo_resource_push()
        demo_risk_alert()
        demo_anonymous_session()
        demo_professional_referral()
        demo_comprehensive_monitoring()
        
        print_section("演示完成")
        print("所有功能演示成功！")
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
