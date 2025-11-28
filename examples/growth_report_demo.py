"""成长报告功能演示"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta
import uuid

from src.services.report_service import ReportService
from src.models.conversation import Conversation
from src.models.mental_health import EmotionState


def demo_growth_report():
    """演示成长报告功能"""
    print("=" * 60)
    print("成长报告功能演示")
    print("=" * 60)
    
    # 创建报告服务
    report_service = ReportService()
    
    # 模拟用户ID
    user_id = "user_001"
    
    # 模拟一些对话数据
    print("\n1. 准备测试数据...")
    for i in range(10):
        conv = Conversation(
            conversation_id=str(uuid.uuid4()),
            user_a_id=user_id,
            user_b_id=f"user_{i+2:03d}",
            scene="考研自习室" if i % 2 == 0 else "兴趣社群",
            status="ended",
            started_at=datetime.now() - timedelta(days=i),
            ended_at=datetime.now() - timedelta(days=i, hours=-1),
            message_count=20 + i * 5,
            topic_depth_score=6.0 + i * 0.3,
            emotion_sync_score=0.7 + i * 0.02
        )
        report_service.conversations[conv.conversation_id] = conv
    
    # 模拟情绪记录
    for i in range(20):
        emotion = EmotionState(
            user_id=user_id,
            emotion_type="positive" if i % 3 != 0 else "negative",
            intensity=0.6 + (i % 5) * 0.08,
            detected_keywords=["学习", "进步"] if i % 3 != 0 else ["压力", "焦虑"],
            timestamp=datetime.now() - timedelta(days=i // 2)
        )
        if user_id not in report_service.emotion_records:
            report_service.emotion_records[user_id] = []
        report_service.emotion_records[user_id].append(emotion)
    
    print("✓ 测试数据准备完成")
    
    # 生成周报
    print("\n2. 生成周报...")
    weekly_report = report_service.generate_weekly_report(user_id)
    print(f"✓ 周报生成成功")
    print(f"  报告ID: {weekly_report.report_id}")
    print(f"  统计周期: {weekly_report.period_start.strftime('%Y-%m-%d')} 至 {weekly_report.period_end.strftime('%Y-%m-%d')}")
    print(f"  对话总数: {weekly_report.total_conversations}")
    print(f"  消息总数: {weekly_report.total_messages}")
    print(f"  平均对话质量: {weekly_report.average_conversation_quality:.2f}")
    print(f"  情绪健康得分: {weekly_report.emotion_health_score:.2f}")
    print(f"  社交能力得分: {weekly_report.social_skill_score:.2f}")
    print(f"  最活跃的一天: {weekly_report.most_active_day}")
    print(f"  最活跃的场景: {weekly_report.most_active_scene}")
    print(f"  新建立的连接: {weekly_report.new_connections}")
    
    print("\n  成长亮点:")
    for highlight in weekly_report.highlights:
        print(f"    • {highlight}")
    
    print("\n  改进建议:")
    for suggestion in weekly_report.suggestions:
        print(f"    • {suggestion}")
    
    # 生成月报
    print("\n3. 生成月报...")
    monthly_report = report_service.generate_monthly_report(user_id)
    print(f"✓ 月报生成成功")
    print(f"  报告ID: {monthly_report.report_id}")
    print(f"  统计周期: {monthly_report.period_start.strftime('%Y-%m-%d')} 至 {monthly_report.period_end.strftime('%Y-%m-%d')}")
    print(f"  对话总数: {monthly_report.total_conversations}")
    print(f"  对话质量趋势: {[f'{x:.1f}' for x in monthly_report.conversation_quality_trend]}")
    print(f"  情绪健康趋势: {[f'{x:.1f}' for x in monthly_report.emotion_health_trend]}")
    print(f"  热门话题: {monthly_report.top_topics}")
    print(f"  场景分布: {monthly_report.scene_distribution}")
    
    # 生成年报
    print("\n4. 生成年报...")
    annual_report = report_service.generate_annual_report(user_id)
    print(f"✓ 年报生成成功")
    print(f"  报告ID: {annual_report.report_id}")
    print(f"  统计周期: {annual_report.period_start.strftime('%Y-%m-%d')} 至 {annual_report.period_end.strftime('%Y-%m-%d')}")
    print(f"  对话总数: {annual_report.total_conversations}")
    print(f"  累计好友数: {annual_report.total_friends}")
    print(f"  最长对话时长: {annual_report.longest_conversation_minutes:.2f} 分钟")
    
    print("\n  成就里程碑:")
    for milestone in annual_report.milestones:
        print(f"    {milestone}")
    
    print("\n  年度总结:")
    print(f"    {annual_report.yearly_summary}")
    
    # 列出用户所有报告
    print("\n5. 列出用户所有报告...")
    all_reports = report_service.list_user_reports(user_id)
    print(f"✓ 找到 {len(all_reports)} 份报告")
    for report in all_reports:
        print(f"  - {report.report_type}: {report.report_id} (生成于 {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')})")
    
    # 下载报告
    print("\n6. 下载报告...")
    download_info = report_service.download_report(weekly_report.report_id, format='json')
    print(f"✓ 报告下载成功")
    print(f"  格式: {download_info['format']}")
    print(f"  文件名: {download_info['filename']}")
    print(f"  内容类型: {download_info['content_type']}")
    
    # 下载HTML格式
    html_download = report_service.download_report(weekly_report.report_id, format='html')
    print(f"✓ HTML格式下载成功")
    print(f"  文件名: {html_download['filename']}")
    
    # 分享报告
    print("\n7. 分享报告...")
    share_link = report_service.share_report(
        weekly_report.report_id,
        share_type='link',
        privacy_level='friends'
    )
    print(f"✓ 分享链接创建成功")
    print(f"  分享ID: {share_link.share_id}")
    print(f"  分享链接: {share_link.share_url}")
    print(f"  分享类型: {share_link.share_type}")
    print(f"  隐私级别: {share_link.privacy_level}")
    print(f"  过期时间: {share_link.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 可视化成长数据
    print("\n8. 可视化成长数据...")
    viz_data = report_service.visualize_growth_data(user_id)
    print(f"✓ 可视化数据获取成功")
    print(f"  对话数量: {viz_data.get('conversation_count', 0)}")
    print(f"  消息数量: {viz_data.get('message_count', 0)}")
    print(f"  质量得分: {viz_data.get('quality_score', 0):.2f}")
    print(f"  情绪得分: {viz_data.get('emotion_score', 0):.2f}")
    print(f"  社交能力得分: {viz_data.get('social_skill_score', 0):.2f}")
    print(f"  场景分布: {viz_data.get('scene_distribution', {})}")
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    demo_growth_report()
