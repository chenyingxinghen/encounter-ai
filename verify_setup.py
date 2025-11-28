"""验证项目基础架构设置"""
import sys
from pathlib import Path


def check_directory_structure():
    """检查目录结构"""
    print("检查目录结构...")
    
    required_dirs = [
        "src",
        "src/api",
        "src/database",
        "src/models",
        "src/services",
        "src/utils",
        "tests",
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} - 不存在")
            all_exist = False
    
    return all_exist


def check_required_files():
    """检查必需文件"""
    print("\n检查必需文件...")
    
    required_files = [
        "src/__init__.py",
        "src/main.py",
        "src/config.py",
        "src/database/__init__.py",
        "src/database/mysql_db.py",
        "src/database/mongodb_db.py",
        "src/database/redis_db.py",
        "src/utils/__init__.py",
        "src/utils/logger.py",
        "src/utils/exceptions.py",
        "src/utils/error_handler.py",
        "requirements.txt",
        ".env.example",
        "pytest.ini",
        "README.md",
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists() and path.is_file():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - 不存在")
            all_exist = False
    
    return all_exist


def check_imports():
    """检查关键模块导入"""
    print("\n检查模块导入...")
    
    try:
        from src.config import settings
        print(f"  ✓ 配置模块导入成功")
        print(f"    - 应用名称: {settings.app_name}")
        print(f"    - 版本: {settings.app_version}")
    except Exception as e:
        print(f"  ✗ 配置模块导入失败: {e}")
        return False
    
    try:
        from src.utils.exceptions import YouthCompanionException
        print(f"  ✓ 异常模块导入成功")
    except Exception as e:
        print(f"  ✗ 异常模块导入失败: {e}")
        return False
    
    try:
        from src.utils.logger import setup_logger
        print(f"  ✓ 日志模块导入成功")
    except Exception as e:
        print(f"  ✗ 日志模块导入失败: {e}")
        return False
    
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("青春伴行平台 - 项目基础架构验证")
    print("=" * 60)
    
    results = []
    
    # 检查目录结构
    results.append(check_directory_structure())
    
    # 检查必需文件
    results.append(check_required_files())
    
    # 检查模块导入
    results.append(check_imports())
    
    # 总结
    print("\n" + "=" * 60)
    if all(results):
        print("✓ 所有检查通过！项目基础架构设置完成。")
        print("\n下一步:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 配置环境变量: 复制 .env.example 为 .env 并修改配置")
        print("3. 启动数据库服务 (MySQL, MongoDB, Redis)")
        print("4. 运行测试: pytest")
        print("5. 启动应用: python src/main.py")
        return 0
    else:
        print("✗ 部分检查失败，请检查上述错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
