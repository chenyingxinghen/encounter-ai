"""人格识别模型服务"""
from typing import List, Dict, Optional
from src.models.user import BigFiveScores
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 尝试导入ML库，如果不可用则使用简化版本
try:
    import torch
    import torch.nn as nn
    import numpy as np
    from transformers import BertTokenizer, BertModel
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.warning("ML libraries not available. Using simplified personality recognition.")


if ML_AVAILABLE:
    class PersonalityClassifier(nn.Module):
        """基于BERT的人格特质分类器"""
        
        def __init__(self, bert_model: BertModel, hidden_size: int = 768, num_traits: int = 5):
            """
            初始化分类器
            
            Args:
                bert_model: BERT模型
                hidden_size: BERT隐藏层大小
                num_traits: 人格特质数量（大五人格为5）
            """
            super(PersonalityClassifier, self).__init__()
            self.bert = bert_model
            
            # 人工神经网络分类器
            self.classifier = nn.Sequential(
                nn.Linear(hidden_size, 512),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(512, 256),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(256, num_traits),
                nn.Sigmoid()  # 输出0-1之间的分数
            )
        
        def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
            """
            前向传播
            
            Args:
                input_ids: 输入token IDs
                attention_mask: 注意力掩码
                
            Returns:
                torch.Tensor: 人格特质得分
            """
            # 获取BERT输出
            outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
            
            # 使用[CLS] token的输出作为句子表示
            pooled_output = outputs.pooler_output
            
            # 通过分类器
            scores = self.classifier(pooled_output)
            
            return scores


class PersonalityRecognitionService:
    """人格识别服务类"""
    
    def __init__(self, model_name: str = "bert-base-chinese", device: Optional[str] = None, use_ml: bool = True):
        """
        初始化人格识别服务
        
        Args:
            model_name: BERT模型名称
            device: 计算设备 ('cpu', 'cuda', 'mps' 或 None自动检测)
            use_ml: 是否使用ML模型（如果False，使用简化版本）
        """
        self.logger = logger
        self.ml_enabled = ML_AVAILABLE and use_ml
        
        if not self.ml_enabled:
            self.logger.info("Using simplified personality recognition (ML libraries not available or disabled)")
            self.device = None
            self.tokenizer = None
            self.model = None
            return
        
        # 设置设备
        if device is None:
            if torch.cuda.is_available():
                self.device = torch.device('cuda')
            elif torch.backends.mps.is_available():
                self.device = torch.device('mps')
            else:
                self.device = torch.device('cpu')
        else:
            self.device = torch.device(device)
        
        self.logger.info(f"Using device: {self.device}")
        
        # 加载BERT tokenizer和模型
        try:
            self.tokenizer = BertTokenizer.from_pretrained(model_name)
            bert_model = BertModel.from_pretrained(model_name)
            
            # 创建人格分类器
            self.model = PersonalityClassifier(bert_model)
            self.model.to(self.device)
            self.model.eval()  # 设置为评估模式
            
            self.logger.info(f"Successfully loaded model: {model_name}")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            self.logger.info("Falling back to simplified personality recognition")
            self.ml_enabled = False
            self.device = None
            self.tokenizer = None
            self.model = None
    
    def analyze_personality(self, text_data: List[str]) -> BigFiveScores:
        """
        分析文本数据并返回大五人格得分
        
        Args:
            text_data: 文本数据列表（用户的对话、评论等）
            
        Returns:
            BigFiveScores: 大五人格得分
        """
        if not text_data:
            # 如果没有文本数据，返回默认中性得分
            return BigFiveScores(
                neuroticism=0.5,
                agreeableness=0.5,
                extraversion=0.5,
                openness=0.5,
                conscientiousness=0.5
            )
        
        # 如果ML不可用，使用简化的基于规则的分析
        if not self.ml_enabled:
            return self._analyze_personality_simple(text_data)
        
        try:
            # 合并文本数据
            combined_text = " ".join(text_data)
            
            # 文本预处理和分词
            encoded = self.tokenizer(
                combined_text,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors='pt'
            )
            
            # 移动到设备
            input_ids = encoded['input_ids'].to(self.device)
            attention_mask = encoded['attention_mask'].to(self.device)
            
            # 推理
            with torch.no_grad():
                scores = self.model(input_ids, attention_mask)
            
            # 转换为numpy数组
            scores_np = scores.cpu().numpy()[0]
            
            # 创建BigFiveScores对象
            big_five_scores = BigFiveScores(
                neuroticism=float(scores_np[0]),
                agreeableness=float(scores_np[1]),
                extraversion=float(scores_np[2]),
                openness=float(scores_np[3]),
                conscientiousness=float(scores_np[4])
            )
            
            self.logger.info(f"Analyzed personality from {len(text_data)} texts")
            return big_five_scores
            
        except Exception as e:
            self.logger.error(f"Error analyzing personality: {e}")
            # 返回默认得分
            return BigFiveScores(
                neuroticism=0.5,
                agreeableness=0.5,
                extraversion=0.5,
                openness=0.5,
                conscientiousness=0.5
            )
    
    def _analyze_personality_simple(self, text_data: List[str]) -> BigFiveScores:
        """
        简化的基于规则的人格分析（当ML库不可用时使用）
        
        Args:
            text_data: 文本数据列表
            
        Returns:
            BigFiveScores: 大五人格得分
        """
        combined_text = " ".join(text_data).lower()
        
        # 基于关键词的简单分析
        # 外向性关键词
        extraversion_keywords = ['朋友', '社交', '聚会', '活动', '外向', '热情', '开朗']
        introversion_keywords = ['独处', '安静', '内向', '独自', '一个人']
        
        # 神经质关键词
        neuroticism_keywords = ['焦虑', '担心', '紧张', '压力', '害怕', '不安']
        stability_keywords = ['平静', '稳定', '放松', '淡定']
        
        # 开放性关键词
        openness_keywords = ['好奇', '探索', '新', '创新', '想象', '艺术']
        
        # 宜人性关键词
        agreeableness_keywords = ['帮助', '友好', '善良', '理解', '同情', '合作']
        
        # 尽责性关键词
        conscientiousness_keywords = ['计划', '组织', '认真', '负责', '努力', '目标']
        
        # 计算得分
        extraversion = 0.5
        for keyword in extraversion_keywords:
            if keyword in combined_text:
                extraversion += 0.05
        for keyword in introversion_keywords:
            if keyword in combined_text:
                extraversion -= 0.05
        
        neuroticism = 0.5
        for keyword in neuroticism_keywords:
            if keyword in combined_text:
                neuroticism += 0.05
        for keyword in stability_keywords:
            if keyword in combined_text:
                neuroticism -= 0.05
        
        openness = 0.5
        for keyword in openness_keywords:
            if keyword in combined_text:
                openness += 0.05
        
        agreeableness = 0.5
        for keyword in agreeableness_keywords:
            if keyword in combined_text:
                agreeableness += 0.05
        
        conscientiousness = 0.5
        for keyword in conscientiousness_keywords:
            if keyword in combined_text:
                conscientiousness += 0.05
        
        # 限制在0-1范围内
        return BigFiveScores(
            neuroticism=self._clip_score(neuroticism),
            agreeableness=self._clip_score(agreeableness),
            extraversion=self._clip_score(extraversion),
            openness=self._clip_score(openness),
            conscientiousness=self._clip_score(conscientiousness)
        )
    
    def calculate_trait_scores(self, text_data: List[str]) -> Dict[str, float]:
        """
        计算人格特质评分（返回字典格式）
        
        Args:
            text_data: 文本数据列表
            
        Returns:
            Dict[str, float]: 人格特质评分字典
        """
        scores = self.analyze_personality(text_data)
        
        return {
            'neuroticism': scores.neuroticism,
            'agreeableness': scores.agreeableness,
            'extraversion': scores.extraversion,
            'openness': scores.openness,
            'conscientiousness': scores.conscientiousness
        }
    
    def batch_analyze(self, text_batches: List[List[str]]) -> List[BigFiveScores]:
        """
        批量分析多个用户的文本数据
        
        Args:
            text_batches: 多个用户的文本数据列表
            
        Returns:
            List[BigFiveScores]: 大五人格得分列表
        """
        results = []
        for text_data in text_batches:
            scores = self.analyze_personality(text_data)
            results.append(scores)
        
        return results
    
    def update_personality_from_behavior(
        self,
        current_scores: BigFiveScores,
        behavior_data: Dict[str, float],
        learning_rate: float = 0.1
    ) -> BigFiveScores:
        """
        根据行为模式动态调整人格特质评分
        
        Args:
            current_scores: 当前人格得分
            behavior_data: 行为数据字典（如response_speed, conversation_depth等）
            learning_rate: 学习率，控制调整幅度
            
        Returns:
            BigFiveScores: 更新后的人格得分
        """
        # 行为模式到人格特质的映射
        # 这是一个简化的映射，实际应该基于心理学研究
        
        # 提取行为特征
        response_speed = behavior_data.get('response_speed', 30.0)
        conversation_depth = behavior_data.get('conversation_depth', 0.5)
        social_frequency = behavior_data.get('social_frequency', 0.5)
        emotion_variance = behavior_data.get('emotion_variance', 0.5)
        
        # 计算调整量
        adjustments = {
            'neuroticism': 0.0,
            'agreeableness': 0.0,
            'extraversion': 0.0,
            'openness': 0.0,
            'conscientiousness': 0.0
        }
        
        # 外向性：社交频率高、回复速度快 -> 外向性高
        if social_frequency > 0.7:
            adjustments['extraversion'] += 0.1
        if response_speed < 10.0:
            adjustments['extraversion'] += 0.05
        
        # 神经质：情绪波动大 -> 神经质高
        if emotion_variance > 0.7:
            adjustments['neuroticism'] += 0.1
        
        # 开放性：对话深度高 -> 开放性高
        if conversation_depth > 0.7:
            adjustments['openness'] += 0.1
        
        # 尽责性：回复稳定、对话深度适中 -> 尽责性高
        if 0.4 <= conversation_depth <= 0.7 and response_speed < 60.0:
            adjustments['conscientiousness'] += 0.1
        
        # 应用调整（使用学习率）
        new_scores = BigFiveScores(
            neuroticism=self._clip_score(
                current_scores.neuroticism + adjustments['neuroticism'] * learning_rate
            ),
            agreeableness=self._clip_score(
                current_scores.agreeableness + adjustments['agreeableness'] * learning_rate
            ),
            extraversion=self._clip_score(
                current_scores.extraversion + adjustments['extraversion'] * learning_rate
            ),
            openness=self._clip_score(
                current_scores.openness + adjustments['openness'] * learning_rate
            ),
            conscientiousness=self._clip_score(
                current_scores.conscientiousness + adjustments['conscientiousness'] * learning_rate
            )
        )
        
        return new_scores
    
    def _clip_score(self, score: float) -> float:
        """
        将得分限制在[0, 1]范围内
        
        Args:
            score: 原始得分
            
        Returns:
            float: 限制后的得分
        """
        return max(0.0, min(1.0, score))
    
    def extract_personality_features(self, text: str):
        """
        从文本中提取人格特征向量
        
        Args:
            text: 输入文本
            
        Returns:
            特征向量（numpy数组或列表）
        """
        if not self.ml_enabled:
            # 简化版本：返回基于文本长度和关键词的简单特征
            return [len(text) / 100.0, text.count('我') / 10.0, text.count('你') / 10.0]
        
        try:
            # 编码文本
            encoded = self.tokenizer(
                text,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors='pt'
            )
            
            # 移动到设备
            input_ids = encoded['input_ids'].to(self.device)
            attention_mask = encoded['attention_mask'].to(self.device)
            
            # 获取BERT嵌入
            with torch.no_grad():
                outputs = self.model.bert(input_ids=input_ids, attention_mask=attention_mask)
                features = outputs.pooler_output
            
            return features.cpu().numpy()[0]
            
        except Exception as e:
            self.logger.error(f"Error extracting features: {e}")
            if ML_AVAILABLE:
                return np.zeros(768)  # 返回零向量
            else:
                return [0.0] * 768
