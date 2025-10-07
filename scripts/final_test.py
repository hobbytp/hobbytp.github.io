#!/usr/bin/env python3
"""
最终数据收集测试脚本
完全避免Unicode字符，确保在Windows环境下正常运行
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

# 加载.env文件
def load_env_file():
    """加载.env文件中的环境变量"""
    env_file = Path(".env")
    if env_file.exists():
        print("加载.env文件...")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # 移除引号
                    value = value.strip('"').strip("'")
                    os.environ[key] = value
        print("环境变量已加载")
    else:
        print("未找到.env文件，使用系统环境变量")

# 在导入其他模块之前加载环境变量
load_env_file()

def test_data_collection():
    """测试数据收集"""
    print("开始测试数据收集功能...")
    print("=" * 50)
    
    try:
        from daily_ai_collector import DailyAICollector
        collector = DailyAICollector()
        
        print("1. 测试GitHub API...")
        github_projects = collector.search_github_trending()
        print(f"   GitHub项目数量: {len(github_projects)}")
        
        if github_projects:
            print("   前3个项目:")
            for i, project in enumerate(github_projects[:3], 1):
                name = project.get('name', 'N/A')
                desc = project.get('description', 'N/A')
                stars = project.get('stargazers_count', 0)
                print(f"     {i}. {name}")
                if desc and len(desc) > 60:
                    desc = desc[:60] + "..."
                print(f"        描述: {desc}")
                print(f"        星数: {stars}")
        else:
            print("   没有找到GitHub项目")
        
        print("\n2. 测试Hugging Face API...")
        hf_models = collector.search_huggingface_models()
        print(f"   HF模型数量: {len(hf_models)}")
        
        if hf_models:
            print("   前3个模型:")
            for i, model in enumerate(hf_models[:3], 1):
                model_id = model.get('modelId', 'N/A')
                pipeline = model.get('pipeline_tag', 'N/A')
                downloads = model.get('downloads', 0)
                print(f"     {i}. {model_id}")
                print(f"        标签: {pipeline}")
                print(f"        下载数: {downloads}")
        else:
            print("   没有找到HF模型")
        
        print("\n3. 测试ArXiv API...")
        arxiv_papers = collector.search_arxiv_papers()
        print(f"   ArXiv论文数量: {len(arxiv_papers)}")
        
        if arxiv_papers:
            print("   前3篇论文:")
            for i, paper in enumerate(arxiv_papers[:3], 1):
                title = paper.get('title', 'N/A')
                authors = paper.get('authors', [])
                if len(title) > 60:
                    title = title[:60] + "..."
                print(f"     {i}. {title}")
                if authors:
                    author_str = ', '.join(authors[:3])
                    print(f"        作者: {author_str}")
        else:
            print("   没有找到ArXiv论文")
        
        # 总结
        total_items = len(github_projects) + len(hf_models) + len(arxiv_papers)
        print(f"\n数据收集总结:")
        print(f"   GitHub项目: {len(github_projects)}")
        print(f"   HF模型: {len(hf_models)}")
        print(f"   ArXiv论文: {len(arxiv_papers)}")
        print(f"   总计: {total_items} 项")
        
        if total_items > 0:
            print("\nOK 数据收集成功！找到了真实数据。")
            return True
        else:
            print("\nERROR 没有收集到任何数据，请检查API配置。")
            return False
            
    except Exception as e:
        print(f"ERROR 数据收集测试失败: {e}")
        return False

def test_ai_summary():
    """测试AI摘要生成"""
    print("\n4. 测试AI摘要生成...")
    
    if not os.getenv('GEMINI_API_KEY'):
        print("   WARNING: 未设置Gemini API Key，跳过AI摘要测试")
        return True
    
    try:
        from daily_ai_collector import DailyAICollector
        collector = DailyAICollector()
        
        # 创建测试数据
        test_data = {
            'github_projects': [
                {
                    'name': 'test-ai-project',
                    'description': 'A test AI project for demonstration',
                    'html_url': 'https://github.com/test/test-ai-project',
                    'stargazers_count': 100
                }
            ],
            'hf_models': [
                {
                    'modelId': 'test-model',
                    'pipeline_tag': 'text-generation',
                    'downloads': 50
                }
            ],
            'arxiv_papers': [
                {
                    'title': 'Test AI Paper: A Novel Approach',
                    'authors': ['Test Author'],
                    'summary': 'This is a test paper about AI.',
                    'link': 'https://arxiv.org/abs/test'
                }
            ]
        }
        
        print("   正在生成AI摘要...")
        summary = collector.generate_ai_summary(test_data)
        print("   OK AI摘要生成成功")
        print("   摘要预览:")
        print("   " + "-" * 40)
        if len(summary) > 200:
            print("   " + summary[:200] + "...")
        else:
            print("   " + summary)
        print("   " + "-" * 40)
        return True
        
    except Exception as e:
        print(f"   ERROR AI摘要生成失败: {e}")
        return False

def main():
    """主函数"""
    print("每日AI动态数据收集测试")
    print("=" * 50)
    
    # 检查环境变量
    print("检查环境变量...")
    github_token = os.getenv('GITHUB_TOKEN')
    gemini_key = os.getenv('GEMINI_API_KEY')
    hf_token = os.getenv('HUGGINGFACE_API_KEY')
    
    print(f"   GitHub Token: {'已设置' if github_token else '未设置'}")
    print(f"   Gemini API Key: {'已设置' if gemini_key else '未设置'}")
    print(f"   Hugging Face Token: {'已设置' if hf_token else '未设置'}")
    
    if not github_token and not gemini_key:
        print("\nWARNING: 没有设置必要的API密钥，某些功能可能无法正常工作")
        print("请设置GITHUB_TOKEN和GEMINI_API_KEY环境变量")
    
    # 运行测试
    data_success = test_data_collection()
    ai_success = test_ai_summary()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print("=" * 50)
    print(f"数据收集: {'OK 成功' if data_success else 'ERROR 失败'}")
    print(f"AI摘要生成: {'OK 成功' if ai_success else 'ERROR 失败'}")
    
    if data_success and ai_success:
        print("\n所有测试都通过了！数据收集功能正常工作。")
    elif data_success:
        print("\n数据收集正常，但AI摘要生成有问题。")
    else:
        print("\n数据收集有问题，请检查API配置和网络连接。")

if __name__ == "__main__":
    main()
