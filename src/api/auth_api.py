"""用户认证API"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import jwt
from src.config import settings
from src.services.user_profile_service import UserProfileService
from src.utils.exceptions import ValidationError, NotFoundError

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()

# 导入共享服务实例
from src.api.dependencies import get_user_profile_service

# 服务实例
user_service = get_user_profile_service()

# JWT配置
SECRET_KEY = settings.secret_key if hasattr(settings, 'secret_key') else "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时


class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str
    user_id: str
    username: str


class TokenData(BaseModel):
    """Token数据"""
    user_id: str
    exp: datetime


def create_access_token(user_id: str) -> str:
    """创建访问令牌"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"user_id": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """验证访问令牌"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭证"
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已过期"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌"
        )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    用户登录接口
    
    验证用户凭证并返回访问令牌
    """
    try:
        # 验证用户凭证（简化版本，实际应该验证密码哈希）
        user = user_service.authenticate_user(request.email, request.password)
        
        # 创建访问令牌
        access_token = create_access_token(user.user_id)
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.user_id,
            username=user.username
        )
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/logout")
async def logout(user_id: str = Depends(verify_token)):
    """
    用户登出接口
    
    使当前令牌失效（实际实现需要令牌黑名单）
    """
    return {
        "message": "登出成功",
        "user_id": user_id
    }


@router.get("/me")
async def get_current_user(user_id: str = Depends(verify_token)):
    """
    获取当前用户信息
    
    通过令牌获取当前登录用户的信息
    """
    try:
        user = user_service.get_user(user_id)
        return user
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
