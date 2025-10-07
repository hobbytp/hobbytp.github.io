#!/usr/bin/env python3
"""
测试环境设置脚本
帮助设置测试所需的环境变量
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """设置测试环境"""
    print("🔧 设置测试环境...")
    
    # 检查是否在虚拟环境中
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 检测到虚拟环境")
    else:
        print("⚠️ 建议在虚拟环境中运行测试")
    
    # 检查必要的包
    required_packages = ['requests', 'openai', 'pyyaml']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 需要安装的包: {', '.join(missing_packages)}")
        print("运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_api_keys():
    """检查API密钥"""
    print("\n🔑 检查API密钥...")
    
    api_keys = {
        'GITHUB_TOKEN': 'GitHub Personal Access Token',
        'GEMINI_API_KEY': 'Google Gemini API Key',
        'HUGGINGFACE_API_KEY': 'Hugging Face API Token (可选)'
    }
    
    missing_keys = []
    for key, description in api_keys.items():
        value = os.getenv(key)
        if value:
            print(f"✅ {key}: 已设置")
        else:
            print(f"❌ {key}: 未设置 - {description}")
            missing_keys.append(key)
    
    if missing_keys:
        print(f"\n⚠️ 缺少API密钥: {', '.join(missing_keys)}")
        print("\n请设置这些环境变量:")
        for key in missing_keys:
            print(f"export {key}='your_api_key_here'")
        
        print("\n或者在Windows中:")
        for key in missing_keys:
            print(f"set {key}=your_api_key_here")
        
        return False
    
    return True

def create_test_config():
    """创建测试配置文件"""
    config_content = """# 测试配置文件
# 复制此文件为 .env 并填入您的API密钥

# GitHub Personal Access Token
# 获取地址: https://github.com/settings/tokens
GITHUB_TOKEN=your_github_token_here

# Google Gemini API Key  
# 获取地址: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Hugging Face API Token (可选)
# 获取地址: https://huggingface.co/settings/tokens
HUGGINGFACE_API_KEY=your_hf_token_here
"""
    
    config_file = Path(".env.example")
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"📄 已创建配置文件模板: {config_file}")
    print("请复制为 .env 文件并填入您的API密钥")

def main():
    """主函数"""
    print("🚀 每日AI动态测试环境设置")
    print("=" * 50)
    
    # 设置环境
    if not setup_environment():
        print("❌ 环境设置失败")
        return
    
    # 检查API密钥
    if not check_api_keys():
        print("❌ API密钥检查失败")
        create_test_config()
        return
    
    print("\n✅ 环境设置完成！")
    print("现在可以运行测试脚本:")
    print("python scripts/test_data_collection.py")

if __name__ == "__main__":
    main()
