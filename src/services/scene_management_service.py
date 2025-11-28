"""场景管理服务"""
from typing import List, Dict, Optional
from src.models.matching import SceneConfig
from src.models.user import UserProfile
from src.utils.exceptions import ValidationError, NotFoundError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SceneManagementService:
    """场景管理服务类"""
    
    def __init__(self, user_profile_service=None, matching_service=None):
        """
        初始化场景管理服务
        
        Args:
            user_profile_service: 用户画像服务实例
            matching_service: 匹配服务实例
        """
        self._user_profile_service = user_profile_service
        self._matching_service = matching_service
        self._scene_configs: Dict[str, SceneConfig] = self._initialize_scene_configs()
        self.logger = logger
    
    def _initialize_scene_configs(self) -> Dict[str, SceneConfig]:
        """
        初始化所有场景配置
        
        Returns:
            Dict[str, SceneConfig]: 场景配置字典
        """
        configs = {}
        
        # 考研自习室场景
        configs['考研自习室'] = SceneConfig(
            scene_name='考研自习室',
            display_name='考研自习室',
            description='为准备考研的同学提供学习伙伴匹配，优先匹配相同目标院校和专业的用户',
            match_weights={
                'personality': 0.25,
                'interest': 0.35,
                'scene': 0.30,
                'emotion': 0.10
            },
            topic_templates=[
                '你的目标院校是哪里？',
                '你每天的学习时间安排是怎样的？',
                '有什么好的学习方法可以分享吗？',
                '你觉得考研最大的挑战是什么？',
                '你是如何保持学习动力的？'
            ],
            intervention_threshold=15,
            max_interventions_per_hour=3
        )
        
        # 职业咨询室场景
        configs['职业咨询室'] = SceneConfig(
            scene_name='职业咨询室',
            display_name='职业咨询室',
            description='为职业规划和求职提供交流平台，优先匹配相同职业兴趣或有相关经验的用户',
            match_weights={
                'personality': 0.20,
                'interest': 0.40,
                'scene': 0.30,
                'emotion': 0.10
            },
            topic_templates=[
                '你对哪个行业感兴趣？',
                '你有什么职业规划？',
                '你参加过哪些实习或项目？',
                '你理想的工作是什么样的？',
                '你在求职过程中遇到了什么困难？'
            ],
            intervention_threshold=15,
            max_interventions_per_hour=3
        )
        
        # 心理树洞场景
        configs['心理树洞'] = SceneConfig(
            scene_name='心理树洞',
            display_name='心理树洞',
            description='提供情感支持和心理倾诉空间，优先匹配有相似经历或情绪状态的用户',
            match_weights={
                'personality': 0.30,
                'interest': 0.10,
                'scene': 0.20,
                'emotion': 0.40
            },
            topic_templates=[
                '最近有什么让你感到困扰的事情吗？',
                '你通常如何缓解压力？',
                '有什么让你感到开心的事情吗？',
                '你觉得什么样的支持对你最有帮助？',
                '你想聊聊你的感受吗？'
            ],
            intervention_threshold=20,  # 心理树洞场景给更多时间
            max_interventions_per_hour=2  # 减少介入频率
        )
        
        # 兴趣社群场景
        configs['兴趣社群'] = SceneConfig(
            scene_name='兴趣社群',
            display_name='兴趣社群',
            description='基于共同兴趣爱好的社交匹配，优先匹配相同兴趣爱好的用户',
            match_weights={
                'personality': 0.20,
                'interest': 0.50,
                'scene': 0.20,
                'emotion': 0.10
            },
            topic_templates=[
                '你最喜欢的兴趣爱好是什么？',
                '你平时喜欢做什么？',
                '有什么想一起做的活动吗？',
                '你是怎么开始这个爱好的？',
                '你有什么推荐的资源或经验吗？'
            ],
            intervention_threshold=15,
            max_interventions_per_hour=3
        )
        
        return configs
    
    def get_scene_config(self, scene: str) -> SceneConfig:
        """
        获取场景配置
        
        Args:
            scene: 场景名称
            
        Returns:
            SceneConfig: 场景配置
            
        Raises:
            ValidationError: 场景名称无效
        """
        if scene not in self._scene_configs:
            raise ValidationError(f"Invalid scene: {scene}")
        
        return self._scene_configs[scene]
    
    def get_match_weights(self, scene: str) -> Dict[str, float]:
        """
        获取场景的匹配权重
        
        Args:
            scene: 场景名称
            
        Returns:
            Dict[str, float]: 匹配权重字典
            
        Raises:
            ValidationError: 场景名称无效
        """
        scene_config = self.get_scene_config(scene)
        return scene_config.match_weights
    
    def list_available_scenes(self, user_id: str = None) -> List[Dict]:
        """
        列出可用的场景
        
        Args:
            user_id: 用户ID（可选，用于个性化推荐）
            
        Returns:
            List[Dict]: 场景列表
        """
        scenes = []
        
        for scene_name, config in self._scene_configs.items():
            scene_info = {
                'scene_name': config.scene_name,
                'display_name': config.display_name,
                'description': config.description,
                'is_active': False
            }
            
            # 如果提供了用户ID，检查用户是否已关注该场景
            if user_id and self._user_profile_service:
                try:
                    profile = self._user_profile_service.get_profile(user_id)
                    scene_info['is_active'] = scene_name in profile.current_scenes
                    scene_info['priority'] = profile.scene_priorities.get(scene_name, 0.0)
                except NotFoundError:
                    pass
            
            scenes.append(scene_info)
        
        return scenes
    
    def switch_scene(self, user_id: str, scene: str, priority: float = 1.0) -> None:
        """
        切换用户的场景
        
        Args:
            user_id: 用户ID
            scene: 场景名称
            priority: 场景优先级 (0.0-1.0)
            
        Raises:
            ValidationError: 场景名称无效或优先级超出范围
            NotFoundError: 用户不存在
        """
        # 验证场景
        if scene not in self._scene_configs:
            raise ValidationError(f"Invalid scene: {scene}")
        
        # 验证优先级
        if not 0.0 <= priority <= 1.0:
            raise ValidationError(f"Priority must be between 0.0 and 1.0, got {priority}")
        
        if not self._user_profile_service:
            raise ValidationError("User profile service not initialized")
        
        # 获取用户画像
        profile = self._user_profile_service.get_profile(user_id)
        
        # 添加场景到当前场景列表（如果不存在）
        if scene not in profile.current_scenes:
            profile.current_scenes.append(scene)
        
        # 更新场景优先级
        profile.scene_priorities[scene] = priority
        
        # 更新用户画像
        self._user_profile_service.update_profile(user_id, {
            'current_scenes': profile.current_scenes,
            'scene_priorities': profile.scene_priorities
        })
        
        # 如果匹配服务可用，触发匹配度重新计算
        if self._matching_service:
            self._recalculate_matches_for_user(user_id)
        
        self.logger.info(
            f"User {user_id} switched to scene: {scene} with priority: {priority}"
        )
    
    def remove_scene(self, user_id: str, scene: str) -> None:
        """
        移除用户的场景
        
        Args:
            user_id: 用户ID
            scene: 场景名称
            
        Raises:
            NotFoundError: 用户不存在
        """
        if not self._user_profile_service:
            raise ValidationError("User profile service not initialized")
        
        # 获取用户画像
        profile = self._user_profile_service.get_profile(user_id)
        
        # 从当前场景列表中移除
        if scene in profile.current_scenes:
            profile.current_scenes.remove(scene)
        
        # 移除场景优先级
        if scene in profile.scene_priorities:
            del profile.scene_priorities[scene]
        
        # 更新用户画像
        self._user_profile_service.update_profile(user_id, {
            'current_scenes': profile.current_scenes,
            'scene_priorities': profile.scene_priorities
        })
        
        self.logger.info(f"User {user_id} removed scene: {scene}")
    
    def update_scene_priority(self, user_id: str, scene: str, priority: float) -> None:
        """
        更新用户对场景的优先级
        
        Args:
            user_id: 用户ID
            scene: 场景名称
            priority: 新的优先级 (0.0-1.0)
            
        Raises:
            ValidationError: 场景名称无效或优先级超出范围
            NotFoundError: 用户不存在
        """
        # 验证场景
        if scene not in self._scene_configs:
            raise ValidationError(f"Invalid scene: {scene}")
        
        # 验证优先级
        if not 0.0 <= priority <= 1.0:
            raise ValidationError(f"Priority must be between 0.0 and 1.0, got {priority}")
        
        if not self._user_profile_service:
            raise ValidationError("User profile service not initialized")
        
        # 获取用户画像
        profile = self._user_profile_service.get_profile(user_id)
        
        # 更新场景优先级
        profile.scene_priorities[scene] = priority
        
        # 更新用户画像
        self._user_profile_service.update_profile(user_id, {
            'scene_priorities': profile.scene_priorities
        })
        
        # 触发匹配度重新计算
        if self._matching_service:
            self._recalculate_matches_for_user(user_id)
        
        self.logger.info(
            f"Updated scene priority for user {user_id}: {scene} = {priority}"
        )
    
    def _recalculate_matches_for_user(self, user_id: str) -> None:
        """
        为用户重新计算匹配度
        
        Args:
            user_id: 用户ID
        """
        # 这里可以触发异步任务来重新计算匹配度
        # 实际实现中应该使用消息队列
        self.logger.info(f"Triggering match recalculation for user: {user_id}")
        # TODO: 实现异步匹配度重新计算
    
    def get_scene_topic_templates(self, scene: str) -> List[str]:
        """
        获取场景的话题模板
        
        Args:
            scene: 场景名称
            
        Returns:
            List[str]: 话题模板列表
            
        Raises:
            ValidationError: 场景名称无效
        """
        scene_config = self.get_scene_config(scene)
        return scene_config.topic_templates
    
    def get_scene_ai_config(self, scene: str) -> Dict:
        """
        获取场景的AI助手配置
        
        Args:
            scene: 场景名称
            
        Returns:
            Dict: AI助手配置
            
        Raises:
            ValidationError: 场景名称无效
        """
        scene_config = self.get_scene_config(scene)
        return {
            'intervention_threshold': scene_config.intervention_threshold,
            'max_interventions_per_hour': scene_config.max_interventions_per_hour
        }
    
    def validate_scene(self, scene: str) -> bool:
        """
        验证场景是否有效
        
        Args:
            scene: 场景名称
            
        Returns:
            bool: 场景是否有效
        """
        return scene in self._scene_configs
    
    def get_all_scene_names(self) -> List[str]:
        """
        获取所有场景名称
        
        Returns:
            List[str]: 场景名称列表
        """
        return list(self._scene_configs.keys())
