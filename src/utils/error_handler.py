"""错误处理中间件"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from src.utils.exceptions import YouthCompanionException
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def youth_companion_exception_handler(
    request: Request, 
    exc: YouthCompanionException
) -> JSONResponse:
    """处理自定义异常"""
    logger.error(f"业务异常: {exc.code} - {exc.message}")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """处理数据验证异常"""
    logger.error(f"数据验证失败: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "数据验证失败",
                "details": exc.errors()
            }
        }
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """处理通用异常"""
    logger.exception(f"未处理的异常: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "服务器内部错误"
            }
        }
    )
