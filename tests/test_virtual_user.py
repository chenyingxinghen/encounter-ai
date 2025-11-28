"""虚拟用户系统测试"""
import pytest
from src.services.virtual_user_service import VirtualUserService
from src.models.virtual_user import VirtualUserGenerationConfig


class TestVirtualUserService:
    """虚拟用户服务测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.service = VirtualUserService()
    
    def test_initialize_virtual_users_default_config(self):
        """测试使用默认配置初始化虚拟用户库"""
        virtual_users = self.service.initialize_virtual_users()
        
        # 验证生成了100个虚拟用户
        assert len(virtual_users) == 100
        
        # 验证所有用户都被存储
        assert len(self.service._virtual_users) == 100
        assert len(self.service._virtual_profiles) == 100
    
    def test_initialize_virtual_users_custom_config(self):
        """测试使用自定义配置初始化虚拟用户库"""
        config = VirtualUserGenerationConfig(total_count=50)
        virtual_users = self.service.initialize_virtual_users(config)
        
        # 验证生成了50个虚拟用户
        assert len(virtual_users) == 50
    
    def test_mbti_type_coverage(self):
        """测试MBTI类型覆盖所有16种类型"""
        config = VirtualUserGenerationConfig(total_count=100)
        virtual_users = self.service.initialize_virtual_users(config)
        
        # 获取所有MBTI类型
        mbti_types = set(vu.mbti_type for vu in virtual_users)
        
        # 验证覆盖所有16种MBTI类型
        expected_types = {
            'INTJ', 'INTP', 'ENTJ', 'ENTP',
            'INFJ', 'INFP', 'ENFJ', 'ENFP',
            'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ',
            'ISTP', 'ISFP', 'ESTP', 'ESFP'
        }
        assert mbti_types == expected_types
    
    def test_virtual_user_identity_marker(self):
        """测试虚拟用户身份标识"""
        virtual_users = self.service.initialize_virtual_users()
        
        for vu in virtual_users:
            # 验证is_virtual标志
            assert vu.is_virtual is True
            
            # 验证用户名包含"AI伙伴"标识
            assert "AI伙伴" in vu.username
            
            # 验证用户ID包含"virtual"前缀
            assert vu.user_id.startswith("virtual_")
    
    def test_virtual_user_profile_generation(self):
        """测试虚拟用户画像生成"""
        virtual_users = self.service.initialize_virtual_users()
        
        for vu in virtual_users:
            profile = self.service.get_virtual_profile(vu.user_id)
            
            # 验证画像存在
            assert profile is not None
            
            # 验证MBTI类型一致
            assert profile.mbti_type == vu.mbti_type
            
            # 验证大五人格得分在有效范围内
            assert 0.0 <= profile.big_five.neuroticism <= 1.0
            assert 0.0 <= profile.big_five.agreeableness <= 1.0
            assert 0.0 <= profile.big_five.extraversion <= 1.0
            assert 0.0 <= profile.big_five.openness <= 1.0
            assert 0.0 <= profile.big_five.conscientiousness <= 1.0
            
            # 验证兴趣标签不为空
            assert len(profile.academic_interests) > 0
            assert len(profile.hobby_interests) > 0
            assert len(profile.career_interests) > 0
            
            # 验证场景选择不为空
            assert len(profile.current_scenes) > 0
    
    def test_response_behavior_simulation(self):
        """测试虚拟用户对话行为模拟"""
        virtual_users = self.service.initialize_virtual_users()
        sample_user = virtual_users[0]
        
        # 模拟回复
        response_data = self.service.simulate_response(
            sample_user.user_id,
            "你好",
            {"scene": "考研自习室"}
        )
        
        # 验证回复数据结构
        assert 'user_id' in response_data
        assert 'response_delay' in response_data
        assert 'expected_length' in response_data
        assert 'response_style' in response_data
        assert 'response_hint' in response_data
        assert 'mbti_type' in response_data
        
        # 验证回复延迟在合理范围内
        assert sample_user.response_speed_range[0] <= response_data['response_delay'] <= sample_user.response_speed_range[1]
        
        # 验证消息长度在合理范围内
        assert sample_user.message_length_range[0] <= response_data['expected_length'] <= sample_user.message_length_range[1]
    
    def test_response_style_consistency(self):
        """测试虚拟用户行为与MBTI类型一致性"""
        virtual_users = self.service.initialize_virtual_users()
        
        for vu in virtual_users:
            # 外向型(E)应该有更快的回复速度
            if vu.mbti_type[0] == 'E':
                assert vu.response_speed_range[1] <= 30.0
            else:  # 内向型(I)
                assert vu.response_speed_range[0] >= 10.0
    
    def test_virtual_user_weight_initial(self):
        """测试虚拟用户初始权重"""
        virtual_users = self.service.initialize_virtual_users()
        
        # 初始权重应该为1.0
        for vu in virtual_users:
            assert vu.match_weight == 1.0
    
    def test_virtual_user_weight_adjustment_below_1000(self):
        """测试真实用户少于1000时虚拟用户权重保持1.0"""
        self.service.initialize_virtual_users()
        
        # 更新真实用户数量为500
        self.service.update_real_user_count(500)
        
        # 验证权重仍为1.0
        stats = self.service.get_statistics()
        assert stats.virtual_user_weight == 1.0
        assert stats.active_virtual_users == 100
    
    def test_virtual_user_weight_adjustment_1000_to_10000(self):
        """测试真实用户在1000-10000之间时虚拟用户权重逐步递减"""
        self.service.initialize_virtual_users()
        
        # 1000个真实用户
        self.service.update_real_user_count(1000)
        stats = self.service.get_statistics()
        assert stats.virtual_user_weight == 1.0
        
        # 5000个真实用户
        self.service.update_real_user_count(5000)
        stats = self.service.get_statistics()
        expected_weight = 1.0 - (5000 - 1000) / 9000
        assert abs(stats.virtual_user_weight - expected_weight) < 0.01
        
        # 9000个真实用户
        self.service.update_real_user_count(9000)
        stats = self.service.get_statistics()
        expected_weight = 1.0 - (9000 - 1000) / 9000
        assert abs(stats.virtual_user_weight - expected_weight) < 0.01
    
    def test_virtual_user_weight_adjustment_above_10000(self):
        """测试真实用户超过10000时虚拟用户权重为0"""
        self.service.initialize_virtual_users()
        
        # 10000个真实用户
        self.service.update_real_user_count(10000)
        stats = self.service.get_statistics()
        assert stats.virtual_user_weight == 0.0
        assert stats.active_virtual_users == 0
        
        # 15000个真实用户
        self.service.update_real_user_count(15000)
        stats = self.service.get_statistics()
        assert stats.virtual_user_weight == 0.0
    
    def test_is_virtual_user(self):
        """测试虚拟用户识别"""
        virtual_users = self.service.initialize_virtual_users()
        
        # 测试虚拟用户
        virtual_id = virtual_users[0].user_id
        assert self.service.is_virtual_user(virtual_id) is True
        
        # 测试非虚拟用户
        real_id = "real_user_123"
        assert self.service.is_virtual_user(real_id) is False
    
    def test_get_virtual_user(self):
        """测试获取虚拟用户"""
        virtual_users = self.service.initialize_virtual_users()
        
        # 获取存在的虚拟用户
        virtual_id = virtual_users[0].user_id
        user = self.service.get_virtual_user(virtual_id)
        assert user is not None
        assert user.user_id == virtual_id
        
        # 获取不存在的用户
        user = self.service.get_virtual_user("nonexistent")
        assert user is None
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        config = VirtualUserGenerationConfig(total_count=100)
        self.service.initialize_virtual_users(config)
        self.service.update_real_user_count(500)
        
        stats = self.service.get_statistics()
        
        # 验证统计数据
        assert stats.total_virtual_users == 100
        assert stats.total_real_users == 500
        assert stats.virtual_user_weight == 1.0
        assert len(stats.mbti_distribution) == 16
        assert stats.active_virtual_users == 100
        
        # 验证MBTI分布总数
        total_count = sum(stats.mbti_distribution.values())
        assert total_count == 100
    
    def test_get_all_virtual_users(self):
        """测试获取所有虚拟用户"""
        self.service.initialize_virtual_users()
        
        all_users = self.service.get_all_virtual_users()
        assert len(all_users) == 100
    
    def test_get_active_virtual_users(self):
        """测试获取活跃虚拟用户"""
        self.service.initialize_virtual_users()
        
        # 初始状态，所有虚拟用户都活跃
        active_users = self.service.get_active_virtual_users()
        assert len(active_users) == 100
        
        # 更新真实用户数量到10000以上
        self.service.update_real_user_count(10000)
        
        # 所有虚拟用户权重变为0，无活跃用户
        active_users = self.service.get_active_virtual_users()
        assert len(active_users) == 0
    
    def test_mbti_personality_mapping(self):
        """测试MBTI类型与人格特征的映射"""
        virtual_users = self.service.initialize_virtual_users()
        
        # 测试几个典型的MBTI类型
        for vu in virtual_users:
            profile = self.service.get_virtual_profile(vu.user_id)
            
            if vu.mbti_type == 'ENTJ':
                # ENTJ应该是高外向性、高尽责性
                assert profile.big_five.extraversion > 0.6
                assert profile.big_five.conscientiousness > 0.7
            
            elif vu.mbti_type == 'INFP':
                # INFP应该是低外向性、高宜人性
                assert profile.big_five.extraversion < 0.4
                assert profile.big_five.agreeableness > 0.7
    
    def test_virtual_user_diversity(self):
        """测试虚拟用户的多样性"""
        virtual_users = self.service.initialize_virtual_users()
        
        # 收集所有学校、专业
        schools = set(vu.school for vu in virtual_users)
        majors = set(vu.major for vu in virtual_users)
        
        # 验证有多样性
        assert len(schools) > 1
        assert len(majors) > 1
    
    def test_simulate_response_invalid_user(self):
        """测试模拟不存在的虚拟用户回复"""
        self.service.initialize_virtual_users()
        
        with pytest.raises(ValueError, match="Virtual user not found"):
            self.service.simulate_response(
                "nonexistent_user",
                "Hello",
                {}
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
