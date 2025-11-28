"""API接口测试"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# 创建一个简化的测试应用
app = FastAPI(title="青春伴行平台", version="0.1.0")

# 导入路由
from src.api.user_api import router as user_router
from src.api.auth_api import router as auth_router
from src.api.matching_api import router as matching_router
from src.api.conversation_api import router as conversation_router
from src.api.report_api import router as report_router
from src.api.moderation_api import router as moderation_router

# 注册路由
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(matching_router)
app.include_router(conversation_router)
app.include_router(report_router)
app.include_router(moderation_router)

# 添加基本路由
@app.get("/")
async def root():
    return {"app": "青春伴行平台", "version": "0.1.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}

# 创建测试客户端
client = TestClient(app)


class TestAuthAPI:
    """认证API测试"""
    
    def test_register_and_login(self):
        """测试用户注册和登录流程"""
        # 注册用户
        register_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "school": "测试大学",
            "major": "计算机科学",
            "grade": 3
        }
        
        response = client.post("/api/users/register", json=register_data)
        assert response.status_code == 201
        user_data = response.json()
        assert user_data["username"] == "testuser"
        assert user_data["email"] == "test@example.com"
        
        # 登录
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        login_response = response.json()
        assert "access_token" in login_response
        assert login_response["token_type"] == "bearer"
        
        return login_response["access_token"]
    
    def test_login_with_invalid_credentials(self):
        """测试使用无效凭证登录"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401


class TestUserAPI:
    """用户API测试"""
    
    def test_complete_registration_flow(self):
        """测试完整的注册流程"""
        # 1. 注册用户
        register_data = {
            "username": "flowtest",
            "email": "flowtest@example.com",
            "password": "password123",
            "school": "测试大学",
            "major": "计算机科学",
            "grade": 3
        }
        
        response = client.post("/api/users/register", json=register_data)
        assert response.status_code == 201
        user_data = response.json()
        user_id = user_data["user_id"]
        
        # 2. 提交MBTI测试
        mbti_data = {
            "user_id": user_id,
            "answers": [3] * 60  # 简化的测试答案
        }
        
        response = client.post("/api/users/mbti-test", json=mbti_data)
        assert response.status_code == 200
        mbti_result = response.json()
        assert "mbti_type" in mbti_result
        
        # 3. 提交大五人格测试
        big_five_data = {
            "user_id": user_id,
            "answers": [3] * 50  # 简化的测试答案
        }
        
        response = client.post("/api/users/big-five-test", json=big_five_data)
        assert response.status_code == 200
        big_five_result = response.json()
        assert "scores" in big_five_result
        
        # 4. 选择兴趣标签
        interests_data = {
            "user_id": user_id,
            "academic_interests": ["考研", "编程"],
            "career_interests": ["软件工程师"],
            "hobby_interests": ["阅读", "音乐"]
        }
        
        response = client.post("/api/users/interests", json=interests_data)
        assert response.status_code == 200
        
        # 5. 选择场景
        scenes_data = {
            "user_id": user_id,
            "scenes": ["考研自习室", "兴趣社群"]
        }
        
        response = client.post("/api/users/scenes", json=scenes_data)
        assert response.status_code == 200
        
        # 6. 生成初始画像
        response = client.post(f"/api/users/profile/generate?user_id={user_id}")
        assert response.status_code == 200
        profile = response.json()
        assert profile["user_id"] == user_id
        assert len(profile["profile_vector"]) > 0


class TestMatchingAPI:
    """匹配API测试"""
    
    def test_find_matches_requires_auth(self):
        """测试匹配接口需要认证"""
        match_data = {
            "scene": "考研自习室",
            "limit": 10
        }
        
        response = client.post("/api/matching/find", json=match_data)
        assert response.status_code == 403  # Forbidden without auth


class TestConversationAPI:
    """对话API测试"""
    
    def test_create_conversation_requires_auth(self):
        """测试创建对话需要认证"""
        conversation_data = {
            "partner_id": "test_partner",
            "scene": "考研自习室"
        }
        
        response = client.post("/api/conversations/create", json=conversation_data)
        assert response.status_code == 403  # Forbidden without auth


class TestReportAPI:
    """报告API测试"""
    
    def test_generate_report_requires_auth(self):
        """测试生成报告需要认证"""
        report_data = {
            "report_type": "weekly"
        }
        
        response = client.post("/api/reports/generate", json=report_data)
        assert response.status_code == 403  # Forbidden without auth


class TestModerationAPI:
    """审查API测试"""
    
    def test_report_user_requires_auth(self):
        """测试举报用户需要认证"""
        report_data = {
            "reported_id": "test_user",
            "report_type": "harassment",
            "reason": "测试举报",
            "evidence": []
        }
        
        response = client.post("/api/moderation/report", json=report_data)
        assert response.status_code == 403  # Forbidden without auth


class TestHealthCheck:
    """健康检查测试"""
    
    def test_root_endpoint(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["app"] == "青春伴行平台"
        assert "version" in data
    
    def test_health_check(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestAPIDocumentation:
    """API文档测试"""
    
    def test_openapi_schema(self):
        """测试OpenAPI schema可访问"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "青春伴行平台"
    
    def test_swagger_ui(self):
        """测试Swagger UI可访问"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc(self):
        """测试ReDoc可访问"""
        response = client.get("/redoc")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
