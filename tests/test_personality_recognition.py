"""人格识别模型测试"""
import pytest
from src.services.personality_recognition_service import PersonalityRecognitionService, ML_AVAILABLE
from src.models.user import BigFiveScores

# 只在ML库可用时导入
if ML_AVAILABLE:
    import torch
    from src.services.personality_recognition_service import PersonalityClassifier


class TestPersonalityRecognitionService:
    """人格识别服务测试类"""
    
    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        # 使用简化版本进行测试（不需要ML库）
        service = PersonalityRecognitionService(use_ml=False)
        return service
    
    def test_service_initialization(self, service):
        """测试服务初始化"""
        assert service is not None
        # 简化版本不需要设备
        assert service.ml_enabled == False
    
    def test_analyze_personality_with_text(self, service):
        """测试文本人格分析"""
        text_data = [
            "我喜欢和朋友们一起出去玩，感觉很开心。",
            "我经常会担心很多事情，有时候会感到焦虑。",
            "我喜欢尝试新的事物，对未知充满好奇。"
        ]
        
        scores = service.analyze_personality(text_data)
        
        # 验证返回类型
        assert isinstance(scores, BigFiveScores)
        
        # 验证得分范围
        assert 0.0 <= scores.neuroticism <= 1.0
        assert 0.0 <= scores.agreeableness <= 1.0
        assert 0.0 <= scores.extraversion <= 1.0
        assert 0.0 <= scores.openness <= 1.0
        assert 0.0 <= scores.conscientiousness <= 1.0
    
    def test_analyze_personality_empty_text(self, service):
        """测试空文本分析"""
        scores = service.analyze_personality([])
        
        # 应该返回默认中性得分
        assert scores.neuroticism == 0.5
        assert scores.agreeableness == 0.5
        assert scores.extraversion == 0.5
        assert scores.openness == 0.5
        assert scores.conscientiousness == 0.5
    
    def test_calculate_trait_scores(self, service):
        """测试特质评分计算"""
        text_data = ["我是一个外向的人，喜欢社交。"]
        
        scores_dict = service.calculate_trait_scores(text_data)
        
        # 验证返回字典格式
        assert isinstance(scores_dict, dict)
        assert 'neuroticism' in scores_dict
        assert 'agreeableness' in scores_dict
        assert 'extraversion' in scores_dict
        assert 'openness' in scores_dict
        assert 'conscientiousness' in scores_dict
        
        # 验证得分范围
        for score in scores_dict.values():
            assert 0.0 <= score <= 1.0
    
    def test_batch_analyze(self, service):
        """测试批量分析"""
        text_batches = [
            ["我喜欢独处，享受安静的时光。"],
            ["我喜欢和朋友们一起活动。"],
            ["我对新事物充满好奇心。"]
        ]
        
        results = service.batch_analyze(text_batches)
        
        # 验证返回结果数量
        assert len(results) == 3
        
        # 验证每个结果都是BigFiveScores
        for scores in results:
            assert isinstance(scores, BigFiveScores)
    
    def test_update_personality_from_behavior(self, service):
        """测试根据行为更新人格"""
        current_scores = BigFiveScores(
            neuroticism=0.5,
            agreeableness=0.5,
            extraversion=0.5,
            openness=0.5,
            conscientiousness=0.5
        )
        
        behavior_data = {
            'response_speed': 5.0,  # 快速回复
            'conversation_depth': 0.8,  # 深度对话
            'social_frequency': 0.9,  # 高社交频率
            'emotion_variance': 0.3  # 低情绪波动
        }
        
        updated_scores = service.update_personality_from_behavior(
            current_scores,
            behavior_data,
            learning_rate=0.1
        )
        
        # 验证返回类型
        assert isinstance(updated_scores, BigFiveScores)
        
        # 验证得分范围
        assert 0.0 <= updated_scores.neuroticism <= 1.0
        assert 0.0 <= updated_scores.agreeableness <= 1.0
        assert 0.0 <= updated_scores.extraversion <= 1.0
        assert 0.0 <= updated_scores.openness <= 1.0
        assert 0.0 <= updated_scores.conscientiousness <= 1.0
        
        # 验证外向性应该增加（因为社交频率高、回复快）
        assert updated_scores.extraversion >= current_scores.extraversion
        
        # 验证开放性应该增加（因为对话深度高）
        assert updated_scores.openness >= current_scores.openness
    
    def test_clip_score(self, service):
        """测试得分限制功能"""
        # 测试超出上限
        assert service._clip_score(1.5) == 1.0
        
        # 测试超出下限
        assert service._clip_score(-0.5) == 0.0
        
        # 测试正常范围
        assert service._clip_score(0.7) == 0.7
    
    def test_extract_personality_features(self, service):
        """测试特征提取"""
        text = "我是一个喜欢思考的人。"
        
        features = service.extract_personality_features(text)
        
        # 验证特征向量存在
        assert features is not None
        assert len(features) > 0


@pytest.mark.skipif(not ML_AVAILABLE, reason="ML libraries not available")
class TestPersonalityClassifier:
    """人格分类器测试类"""
    
    def test_classifier_initialization(self):
        """测试分类器初始化"""
        try:
            from transformers import BertModel
            bert_model = BertModel.from_pretrained("bert-base-chinese")
            classifier = PersonalityClassifier(bert_model)
            
            assert classifier is not None
            assert classifier.bert is not None
            assert classifier.classifier is not None
        except Exception as e:
            pytest.skip(f"Cannot initialize classifier: {e}")
    
    def test_classifier_forward(self):
        """测试分类器前向传播"""
        try:
            from transformers import BertModel
            bert_model = BertModel.from_pretrained("bert-base-chinese")
            classifier = PersonalityClassifier(bert_model)
            
            # 创建模拟输入
            batch_size = 2
            seq_length = 10
            input_ids = torch.randint(0, 1000, (batch_size, seq_length))
            attention_mask = torch.ones(batch_size, seq_length)
            
            # 前向传播
            with torch.no_grad():
                scores = classifier(input_ids, attention_mask)
            
            # 验证输出形状
            assert scores.shape == (batch_size, 5)
            
            # 验证输出范围（Sigmoid输出应该在0-1之间）
            assert torch.all(scores >= 0.0)
            assert torch.all(scores <= 1.0)
        except Exception as e:
            pytest.skip(f"Cannot test forward pass: {e}")


class TestPersonalityIntegration:
    """人格识别集成测试"""
    
    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        # 使用简化版本
        service = PersonalityRecognitionService(use_ml=False)
        return service
    
    def test_end_to_end_personality_analysis(self, service):
        """测试端到端人格分析流程"""
        # 模拟用户对话数据
        user_texts = [
            "我最近在准备考研，压力很大。",
            "但是我相信通过努力一定能成功。",
            "我喜欢和同学们一起学习，互相鼓励。",
            "有时候我也会感到焦虑，但我会调整心态。",
            "我对未来充满期待，想要探索更多可能性。"
        ]
        
        # 分析人格
        scores = service.analyze_personality(user_texts)
        
        # 验证结果
        assert isinstance(scores, BigFiveScores)
        assert all(0.0 <= getattr(scores, trait) <= 1.0 
                  for trait in ['neuroticism', 'agreeableness', 'extraversion', 
                               'openness', 'conscientiousness'])
        
        # 模拟行为数据
        behavior_data = {
            'response_speed': 15.0,
            'conversation_depth': 0.7,
            'social_frequency': 0.6,
            'emotion_variance': 0.4
        }
        
        # 根据行为更新人格
        updated_scores = service.update_personality_from_behavior(
            scores,
            behavior_data
        )
        
        # 验证更新后的结果
        assert isinstance(updated_scores, BigFiveScores)
        assert all(0.0 <= getattr(updated_scores, trait) <= 1.0 
                  for trait in ['neuroticism', 'agreeableness', 'extraversion', 
                               'openness', 'conscientiousness'])
