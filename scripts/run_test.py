#!/usr/bin/env python3
"""
快速测试运行脚本
"""

import os
import sys
from pathlib import Path

def load_env_file():
    """加载.env文件中的环境变量"""
    env_file = Path(".env")
    if env_file.exists():
        print("📄 加载.env文件...")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ 环境变量已加载")
    else:
        print("⚠️ 未找到.env文件，使用系统环境变量")

def main():
    """主函数"""
    print("🧪 快速测试数据收集功能")
    print("=" * 40)
    
    # 加载环境变量
    load_env_file()
    
    # 导入并运行测试
    try:
        from test_data_collection import main as test_main
        test_main()
    except ImportError as e:
        print(f"❌ 导入测试模块失败: {e}")
        print("请确保在正确的目录中运行此脚本")
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")

if __name__ == "__main__":
    main()
