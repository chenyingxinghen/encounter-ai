"""
内容审查系统演示
Content Moderation System Demo
"""
from src.services.content_moderation_service import ContentModerationService
from src.models.moderation import UserReport, Penalty


def print_separator():
    """打印分隔线"""
    print("\n" + "="*60 + "\n")


def demo_message_moderation():
    """演示消息审查"""
    print("【演示1：消息内容审查】")
    print_separator()
    
    service = ContentModerationService()
    
    # 测试正常消息
    print("1. 审查正常消息:")
    message1 = "你好，很高兴认识你！我们可以一起学习。"
    result1 = service.moderate_message(message1, "user1", "msg1")
    print(f"   消息: {message1}")
    print(f"   审查结果: {'通过' if result1.is_approved else '不通过'}")
    print(f"   处理动作: {result1.action}")
    print(f"   置信度: {result1.confidence_score:.2f}")
    
    print_separator()
    
    # 测试暴力消息
    print("2. 审查暴力消息:")
    message2 = "我要打人，用暴力解决问题"
    result2 = service.moderate_message(message2, "user2", "msg2")
    print(f"   消息: {message2}")
    print(f"   审查结果: {'通过' if result2.is_approved else '不通过'}")
    print(f"   处理动作: {result2.action}")
    print(f"   违规类型: {', '.join(result2.violation_types)}")
    print(f"   触发关键词: {', '.join(result2.flagged_keywords)}")
    print(f"   置信度: {result2.confidence_score:.2f}")
    
    print_separator()
    
    # 测试色情消息
    print("3. 审查色情消息:")
    message3 = "这是色情内容，黄色信息"
    result3 = service.moderate_message(message3, "user3", "msg3")
    print(f"   消息: {message3}")
    print(f"   审查结果: {'通过' if result3.is_approved else '不通过'}")
    print(f"   处理动作: {result3.action}")
    print(f"   违规类型: {', '.join(result3.violation_types)}")
    
    print_separator()
    
    # 测试骚扰消息
    print("4. 审查骚扰消息:")
    message4 = "你这个傻子，我要侮辱你，骚扰你"
    result4 = service.moderate_message(message4, "user4", "msg4")
    print(f"   消息: {message4}")
    print(f"   审查结果: {'通过' if result4.is_approved else '不通过'}")
    print(f"   处理动作: {result4.action}")
    print(f"   违规类型: {', '.join(result4.violation_types)}")
    
    print_separator()
    
    # 测试垃圾消息
    print("5. 审查垃圾消息:")
    message5 = "加微信赚钱，广告推广，兼职刷单"
    result5 = service.moderate_message(message5, "user5", "msg5")
    print(f"   消息: {message5}")
    print(f"   审查结果: {'通过' if result5.is_approved else '不通过'}")
    print(f"   处理动作: {result5.action}")
    print(f"   违规类型: {', '.join(result5.violation_types)}")


def demo_violation_tracking():
    """演示违规追踪"""
    print("【演示2：违规记录追踪】")
    print_separator()
    
    service = ContentModerationService()
    user_id = "user_test"
    
    # 模拟多次违规
    print("模拟用户多次违规:")
    messages = [
        "暴力内容1",
        "暴力内容2",
        "色情内容",
        "骚扰内容",
        "垃圾广告"
    ]
    
    for i, msg in enumerate(messages, 1):
        result = service.moderate_message(msg, user_id, f"msg{i}")
        print(f"   第{i}次: {msg} -> {result.action}")
    
    print_separator()
    
    # 查看违规历史
    violations = service.get_user_violation_history(user_id)
    print(f"用户违规历史 (共{len(violations)}条):")
    for v in violations:
        print(f"   - 类型: {v.violation_type}, 严重程度: {v.severity}, "
              f"状态: {v.status}")
    
    print_separator()
    
    # 查看处罚记录
    penalties = service.get_user_penalties(user_id)
    print(f"用户处罚记录 (共{len(penalties)}条):")
    for p in penalties:
        print(f"   - 类型: {p.penalty_type}, 时长: {p.duration}秒, "
              f"状态: {p.status}")
    
    print_separator()
    
    # 检查是否被处罚
    is_penalized = service.is_user_penalized(user_id)
    print(f"用户当前是否被处罚: {'是' if is_penalized else '否'}")


def demo_user_report():
    """演示用户举报"""
    print("【演示3：用户举报功能】")
    print_separator()
    
    service = ContentModerationService()
    
    # 创建举报
    print("1. 用户A举报用户B:")
    report = service.handle_user_report(
        reporter_id="userA",
        reported_id="userB",
        report_type=UserReport.TYPE_HARASSMENT,
        reason="该用户持续发送骚扰信息，严重影响我的使用体验",
        evidence=["msg101", "msg102", "msg103"]
    )
    
    print(f"   举报ID: {report.report_id}")
    print(f"   举报人: {report.reporter_id}")
    print(f"   被举报人: {report.reported_id}")
    print(f"   举报类型: {report.report_type}")
    print(f"   举报原因: {report.reason}")
    print(f"   证据数量: {len(report.evidence)}")
    print(f"   状态: {report.status}")
    
    print_separator()
    
    # 创建另一个举报
    print("2. 用户C举报用户D:")
    report2 = service.handle_user_report(
        reporter_id="userC",
        reported_id="userD",
        report_type=UserReport.TYPE_INAPPROPRIATE_CONTENT,
        reason="该用户发送不当内容",
        evidence=["msg201"]
    )
    
    print(f"   举报ID: {report2.report_id}")
    print(f"   举报类型: {report2.report_type}")
    print(f"   状态: {report2.status}")


def demo_content_review():
    """演示内容审核"""
    print("【演示4：内容审核流程】")
    print_separator()
    
    service = ContentModerationService()
    
    # 创建违规内容
    print("1. 检测到违规内容:")
    message = "暴力内容测试"
    result = service.moderate_message(message, "user_review", "msg_review")
    print(f"   消息: {message}")
    print(f"   处理动作: {result.action}")
    
    print_separator()
    
    if result.action in ["block", "review"]:
        # 人工审核 - 确认违规
        print("2. 人工审核 - 确认违规:")
        service.review_flagged_content("msg_review", "admin1", "confirm")
        violations = service.get_user_violation_history("user_review")
        if violations:
            print(f"   违规状态: {violations[0].status}")
            print(f"   审核人员: {violations[0].reviewed_by}")
        
        print_separator()
    
    # 创建另一个可能的误报
    print("3. 检测到可能的误报:")
    message2 = "暴力美学是一种艺术表现形式"
    result2 = service.moderate_message(message2, "user_review2", "msg_review2")
    print(f"   消息: {message2}")
    print(f"   处理动作: {result2.action}")
    
    if result2.action in ["block", "review"]:
        print_separator()
        print("4. 人工审核 - 驳回违规:")
        service.review_flagged_content("msg_review2", "admin1", "dismiss")
        violations2 = service.get_user_violation_history("user_review2")
        if violations2:
            print(f"   违规状态: {violations2[0].status}")


def demo_penalty_system():
    """演示处罚系统"""
    print("【演示5：自动处罚系统】")
    print_separator()
    
    service = ContentModerationService()
    user_id = "user_penalty_demo"
    
    print("模拟用户逐步违规，触发不同级别的处罚:")
    print_separator()
    
    # 模拟10次违规
    for i in range(1, 11):
        message = f"违规内容 {i}"
        result = service.moderate_message(message, user_id, f"msg{i}")
        
        if result.action == "block":
            penalties = service.get_user_penalties(user_id)
            if penalties:
                latest_penalty = penalties[-1]
                print(f"第{i}次违规:")
                print(f"   违规次数: {service.user_violation_counts[user_id]}")
                print(f"   触发处罚: {latest_penalty.penalty_type}")
                print(f"   处罚时长: {latest_penalty.duration}秒")
                print_separator()


def demo_appeal_system():
    """演示申诉系统"""
    print("【演示6：用户申诉系统】")
    print_separator()
    
    service = ContentModerationService()
    
    # 创建违规
    print("1. 用户发送消息被标记为违规:")
    message = "暴力内容"
    result = service.moderate_message(message, "user_appeal", "msg_appeal")
    print(f"   消息: {message}")
    print(f"   处理动作: {result.action}")
    
    print_separator()
    
    # 用户申诉
    violations = service.get_user_violation_history("user_appeal")
    if violations:
        print("2. 用户提交申诉:")
        violation_id = violations[0].violation_id
        appeal_result = service.handle_appeal(
            "user_appeal",
            violation_id,
            "这是误判，我只是在讨论电影中的暴力美学"
        )
        
        print(f"   申诉提交: {'成功' if appeal_result else '失败'}")
        print(f"   违规状态: {violations[0].status}")


def demo_statistics():
    """演示统计功能"""
    print("【演示7：审查统计数据】")
    print_separator()
    
    service = ContentModerationService()
    
    # 创建一些测试数据
    service.moderate_message("暴力内容1", "user1", "msg1")
    service.moderate_message("暴力内容2", "user2", "msg2")
    service.moderate_message("色情内容", "user3", "msg3")
    service.moderate_message("骚扰内容", "user4", "msg4")
    service.handle_user_report("user5", "user6", UserReport.TYPE_HARASSMENT,
                              "骚扰", ["msg5"])
    service.handle_user_report("user7", "user8", UserReport.TYPE_INAPPROPRIATE_CONTENT,
                              "垃圾信息", ["msg6"])
    
    # 获取统计数据
    stats = service.get_moderation_stats()
    
    print("系统审查统计:")
    print(f"   总违规数: {stats['total_violations']}")
    print(f"   总举报数: {stats['total_reports']}")
    print(f"   总处罚数: {stats['total_penalties']}")
    print(f"   违规用户数: {stats['users_with_violations']}")
    
    print_separator()
    
    print("违规类型分布:")
    for vtype, count in stats['violations_by_type'].items():
        print(f"   {vtype}: {count}")
    
    print_separator()
    
    if stats['penalties_by_type']:
        print("处罚类型分布:")
        for ptype, count in stats['penalties_by_type'].items():
            print(f"   {ptype}: {count}")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("内容审查与监管系统演示")
    print("Content Moderation System Demo")
    print("="*60)
    
    # 运行所有演示
    demo_message_moderation()
    print("\n")
    
    demo_violation_tracking()
    print("\n")
    
    demo_user_report()
    print("\n")
    
    demo_content_review()
    print("\n")
    
    demo_penalty_system()
    print("\n")
    
    demo_appeal_system()
    print("\n")
    
    demo_statistics()
    
    print("\n" + "="*60)
    print("演示完成！")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
