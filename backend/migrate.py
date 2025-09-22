#!/usr/bin/env python
"""
Aerich 迁移管理脚本

提供数据库迁移的便捷操作
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """运行命令并打印结果"""
    print(f"\n📋 {description}")
    print(f"🔧 执行命令: {cmd}")
    print("-" * 50)
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 成功!")
        if result.stdout.strip():
            print(f"输出:\n{result.stdout}")
    else:
        print("❌ 失败!")
        if result.stderr.strip():
            print(f"错误:\n{result.stderr}")
        sys.exit(1)

def init_aerich():
    """初始化 aerich"""
    run_command("uv run aerich init -t app.core.database_config.TORTOISE_CONFIG", "初始化 aerich 配置")

def init_db():
    """初始化数据库"""
    run_command("uv run aerich init-db", "初始化数据库并创建第一个迁移")

def migrate():
    """生成新的迁移文件"""
    name = input("请输入迁移描述 (可选): ").strip()
    cmd = "uv run aerich migrate"
    if name:
        cmd += f" --name '{name}'"
    run_command(cmd, "生成迁移文件")

def upgrade():
    """应用迁移"""
    run_command("uv run aerich upgrade", "应用数据库迁移")

def downgrade():
    """回滚迁移"""
    run_command("uv run aerich downgrade", "回滚最后一次迁移")

def history():
    """查看迁移历史"""
    run_command("uv run aerich history", "查看迁移历史")

def heads():
    """查看当前HEAD"""
    run_command("uv run aerich heads", "查看当前HEAD")

def main():
    """主函数"""
    print("🚀 Aerich 数据库迁移工具")
    print("=" * 50)
    print("1. 初始化 aerich")
    print("2. 初始化数据库 (首次使用)")
    print("3. 生成迁移文件")
    print("4. 应用迁移")
    print("5. 回滚迁移")
    print("6. 查看迁移历史")
    print("7. 查看当前HEAD")
    print("8. 完整初始化 (初始化aerich + 数据库 + 插入初始数据)")
    print("0. 退出")
    print("=" * 50)
    
    while True:
        try:
            choice = input("\n请选择操作 (0-8): ").strip()
            
            if choice == "0":
                print("👋 再见!")
                break
            elif choice == "1":
                init_aerich()
            elif choice == "2":
                init_db()
            elif choice == "3":
                migrate()
            elif choice == "4":
                upgrade()
            elif choice == "5":
                downgrade()
            elif choice == "6":
                history()
            elif choice == "7":
                heads()
            elif choice == "8":
                print("\n🔄 开始完整初始化...")
                init_aerich()
                init_db()
                print("\n📊 插入初始数据...")
                run_command("uv run python init_data.py", "插入初始数据")
                print("\n🎉 完整初始化完成!")
            else:
                print("❌ 无效选择，请输入 0-8")
        except KeyboardInterrupt:
            print("\n\n👋 操作已取消")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")

if __name__ == "__main__":
    # 确保在正确的目录中
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    main()