"""人格识别模型演示脚本"""
import sys
sys.path.append('.')

from src.services.personality_recognition_service import PersonalityRecognitionService
from src.models.user import BigFiveScores


def main():
    """主函数"""
    print("=" * 60)
    print("青春伴行 - 人格识别模型演示")
    print("=" * 60)
    print()
    
    # 初始化服务
    print("正在初始化人格识别服务...")
    try:
        service = PersonalityRecognitionService(device='cpu')
        print("✓ 服务初始化成功")
    except Exception as e:
        print(f"✗ 服务初始化失败: {e}")
        print("\n提示：请确保已安装所需依赖：")
        print("  pip install torch transformers numpy scikit-learn")
        return
    
    print()
    
    # 示例1：分析用户文本
    print("-" * 60)
    print("示例1：基于文本分析人格特质")
    print("-" * 60)
    
    user_texts = [
        "我喜欢和朋友们一起出去玩，感觉很开心。",
        "我经常会担心很多事情，有时候会感到焦虑。",
        "我喜欢尝试新的事物，对未知充满好奇。",
        "我做事情比较有计划，喜欢按部就班。",
        "我很在意别人的感受，愿意帮助他人。"
    ]
    
    print("\n用户文本：")
    for i, text in enumerate(user_texts, 1):
        print(f"  {i}. {text}")
    
    print("\n正在分析...")
    scores = service.analyze_personality(user_texts)
    
    print("\n分析结果（大五人格得分）：")
    print(f"  神经质 (Neuroticism):      {scores.neuroticism:.3f}")
    print(f"  宜人性 (Agreeableness):    {scores.agreeableness:.3f}")
    print(f"  外向性 (Extraversion):     {scores.extraversion:.3f}")
    print(f"  开放性 (Openness):         {scores.openness:.3f}")
    print(f"  尽责性 (Conscientiousness): {scores.conscientiousness:.3f}")
    
    # 示例2：根据行为更新人格
    print()
    print("-" * 60)
    print("示例2：根据行为模式动态调整人格特质")
    print("-" * 60)
    
    behavior_data = {
        'response_speed': 5.0,  # 快速回复（秒）
        'conversation_depth': 0.8,  # 深度对话
        'social_frequency': 0.9,  # 高社交频率
        'emotion_variance': 0.3  # 低情绪波动
    }
    
    print("\n行为数据：")
    print(f"  平均回复速度: {behavior_data['response_speed']} 秒")
    print(f"  对话深度: {behavior_data['conversation_depth']:.2f}")
    print(f"  社交频率: {behavior_data['social_frequency']:.2f}")
    print(f"  情绪波动: {behavior_data['emotion_variance']:.2f}")
    
    print("\n正在根据行为调整人格特质...")
    updated_scores = service.update_personality_from_behavior(
        scores,
        behavior_data,
        learning_rate=0.1
    )
    
    print("\n更新后的人格得分：")
    print(f"  神经质 (Neuroticism):      {updated_scores.neuroticism:.3f} "
          f"(变化: {updated_scores.neuroticism - scores.neuroticism:+.3f})")
    print(f"  宜人性 (Agreeableness):    {updated_scores.agreeableness:.3f} "
          f"(变化: {updated_scores.agreeableness - scores.agreeableness:+.3f})")
    print(f"  外向性 (Extraversion):     {updated_scores.extraversion:.3f} "
          f"(变化: {updated_scores.extraversion - scores.extraversion:+.3f})")
    print(f"  开放性 (Openness):         {updated_scores.openness:.3f} "
          f"(变化: {updated_scores.openness - scores.openness:+.3f})")
    print(f"  尽责性 (Conscientiousness): {updated_scores.conscientiousness:.3f} "
          f"(变化: {updated_scores.conscientiousness - scores.conscientiousness:+.3f})")
    
    # 示例3：批量分析
    print()
    print("-" * 60)
    print("示例3：批量分析多个用户")
    print("-" * 60)
    
    user_batches = [
        ["我喜欢独处，享受安静的时光。"],
        ["我喜欢和朋友们一起活动，很外向。"],
        ["我对新事物充满好奇心，喜欢探索。"]
    ]
    
    print("\n正在批量分析3个用户...")
    results = service.batch_analyze(user_batches)
    
    for i, scores in enumerate(results, 1):
        print(f"\n用户{i}的人格得分：")
        print(f"  外向性: {scores.extraversion:.3f}")
        print(f"  开放性: {scores.openness:.3f}")
    
    print()
    print("=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
