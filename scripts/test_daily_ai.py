#!/usr/bin/env python3
"""
测试每日AI动态收集功能
"""

import os
import sys
from pathlib import Path

# 添加scripts目录到Python路径
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from daily_ai_collector import DailyAICollector

def test_collector():
    """测试收集器功能"""
    print("🧪 开始测试每日AI动态收集器...")
    
    # 检查环境变量
    required_env_vars = ['OPENAI_API_KEY', 'GITHUB_TOKEN']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  缺少环境变量: {missing_vars}")
        print("请设置以下环境变量:")
        for var in missing_vars:
            print(f"  export {var}=your_api_key")
        return False
    
    try:
        # 创建收集器实例
        collector = DailyAICollector()
        print("✅ 收集器初始化成功")
        
        # 测试GitHub搜索
        print("🔍 测试GitHub项目搜索...")
        github_projects = collector.search_github_trending()
        print(f"✅ 找到 {len(github_projects)} 个GitHub项目")
        
        # 测试Hugging Face搜索
        print("🔍 测试Hugging Face模型搜索...")
        hf_models = collector.search_huggingface_models()
        print(f"✅ 找到 {len(hf_models)} 个Hugging Face模型")
        
        # 测试ArXiv搜索
        print("🔍 测试ArXiv论文搜索...")
        arxiv_papers = collector.search_arxiv_papers()
        print(f"✅ 找到 {len(arxiv_papers)} 篇ArXiv论文")
        
        # 测试内容生成
        print("📝 测试内容生成...")
        content = collector.create_daily_content()
        print(f"✅ 内容生成成功，长度: {len(content)} 字符")
        
        # 保存测试内容
        test_file = Path("content/zh/daily_ai/test_daily_ai.md")
        test_file.parent.mkdir(exist_ok=True)
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 测试内容已保存到: {test_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始测试每日AI动态收集功能...")
    
    success = test_collector()
    
    if success:
        print("✅ 所有测试通过！")
        print("\n📋 下一步:")
        print("1. 在GitHub仓库中设置以下Secrets:")
        print("   - OPENAI_API_KEY: 你的OpenAI API密钥")
        print("   - GITHUB_TOKEN: GitHub Personal Access Token")
        print("   - HUGGINGFACE_API_KEY: Hugging Face API密钥 (可选)")
        print("2. 推送代码到GitHub")
        print("3. GitHub Action将每天北京时间8点自动运行")
    else:
        print("❌ 测试失败，请检查配置")

if __name__ == "__main__":
    main()
