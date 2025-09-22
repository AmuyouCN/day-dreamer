#!/usr/bin/env python
"""
现代化启动脚本

使用 UV 依赖管理 + Aerich 数据库迁移的完整解决方案
提供一键启动体验
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def run_command(cmd, description, check=True):
    """运行命令"""
    print(f"\n📋 {description}")
    print(f"🔧 执行命令: {cmd}")
    print("-" * 50)
    
    result = subprocess.run(cmd, shell=True)
    
    if check and result.returncode != 0:
        print(f"❌ 命令执行失败: {cmd}")
        sys.exit(1)
    
    return result.returncode == 0

def check_uv():
    """检查 uv 是否安装"""
    print("🔍 检查 uv 安装状态...")
    result = subprocess.run("uv --version", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ uv 未安装，请先安装 uv:")
        print("📦 安装命令: pip install uv")
        print("🌐 或访问: https://github.com/astral-sh/uv")
        return False
    print(f"✅ uv 已安装: {result.stdout.strip()}")
    return True

def check_dependencies():
    """检查依赖"""
    print("🔍 检查项目依赖...")
    
    # 检查是否存在虚拟环境
    venv_dir = Path(".venv")
    if not venv_dir.exists():
        print("📦 虚拟环境不存在，正在创建...")
        if not run_command("uv venv", "创建虚拟环境", check=False):
            print("❌ 创建虚拟环境失败")
            return False
    
    # 安装依赖
    if not run_command("uv pip install -e .", "安装项目依赖", check=False):
        print("❌ 安装依赖失败")
        return False
    
    print("✅ 依赖检查完成")
    return True

def setup_database():
    """设置数据库"""
    print("\n🗄️ 设置数据库...")
    
    # 检查是否已经初始化过 aerich
    migrations_dir = Path("migrations")
    if migrations_dir.exists():
        print("📁 发现已存在的迁移目录")
        # 应用迁移
        if run_command("uv run aerich upgrade", "应用数据库迁移", check=False):
            print("✅ 数据库迁移已应用")
        else:
            print("⚠️ 迁移应用失败，可能数据库已是最新状态")
    else:
        print("🚀 首次初始化数据库...")
        # 初始化 aerich
        run_command("uv run aerich init -t app.core.database_config.TORTOISE_CONFIG", "初始化 aerich")
        # 创建初始迁移
        run_command("uv run aerich init-db", "创建初始数据库迁移")
        # 插入初始数据
        run_command("uv run python init_data.py", "插入初始数据")

def main():
    """主函数"""
    print("🚀 接口自动化测试平台现代化启动")
    print("🔥 UV 依赖管理 + Aerich 数据库迁移")
    print("=" * 60)
    
    # 确保在正确的目录
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # 检查 uv
    if not check_uv():
        sys.exit(1)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 设置数据库
    setup_database()
    
    # 启动应用
    print("\n🌟 启动应用服务器...")
    print("📊 访问地址:")
    print("  - API文档: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("  - 健康检查: http://localhost:8000/health")
    print("💡 使用 uv 管理的虚拟环境")
    print("=" * 60)
    
    try:
        # 使用 uv run 启动应用
        subprocess.run([
            "uv", "run", "uvicorn", 
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ])
    except KeyboardInterrupt:
        print("\n👋 应用已关闭")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()