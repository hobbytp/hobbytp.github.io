#!/usr/bin/env python3
"""
基础数据收集测试脚本
完全避免Unicode字符
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """测试导入"""
    print("测试导入模块...")
    try:
        import requests
        print("OK requests 导入成功")
    except ImportError as e:
        print(f"ERROR requests 导入失败: {e}")
        return False
    
    try:
        import openai
        print("OK openai 导入成功")
    except ImportError as e:
        print(f"ERROR openai 导入失败: {e}")
        return False
    
    try:
        import yaml
        print("OK yaml 导入成功")
    except ImportError as e:
        print(f"ERROR yaml 导入失败: {e}")
        return False
    
    return True

def test_environment():
    """测试环境变量"""
    print("\n检查环境变量...")
    
    required_vars = {
        'GITHUB_TOKEN': 'GitHub API Token',
        'GEMINI_API_KEY': 'Gemini API Key',
        'HUGGINGFACE_API_KEY': 'Hugging Face API Key (可选)'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"OK {var}: 已设置")
        else:
            print(f"ERROR {var}: 未设置 - {description}")
            if var != 'HUGGINGFACE_API_KEY':  # HF token是可选的
                missing_vars.append(var)
    
    if missing_vars:
        print(f"\n缺少必需的环境变量: {', '.join(missing_vars)}")
        print("请设置这些环境变量后再运行测试")
        return False
    
    print("环境变量检查完成")
    return True

def test_daily_ai_collector():
    """测试DailyAICollector类"""
    print("\n测试DailyAICollector类...")
    try:
        from daily_ai_collector import DailyAICollector
        collector = DailyAICollector()
        print("OK DailyAICollector 实例化成功")
        
        # 测试时间范围
        yesterday, today = collector.get_date_range()
        print(f"OK 时间范围: {yesterday} 到 {today}")
        
        return True
    except Exception as e:
        print(f"ERROR DailyAICollector 测试失败: {e}")
        return False

def test_github_api():
    """测试GitHub API"""
    print("\n测试GitHub API...")
    try:
        from daily_ai_collector import DailyAICollector
        collector = DailyAICollector()
        
        if not collector.github_token:
            print("WARNING GitHub token未设置，跳过GitHub API测试")
            return True
        
        print("正在搜索GitHub项目...")
        projects = collector.search_github_trending()
        print(f"OK 找到 {len(projects)} 个GitHub项目")
        
        if projects:
            print("前3个项目:")
            for i, project in enumerate(projects[:3], 1):
                print(f"  {i}. {project.get('name', 'N/A')}")
                print(f"     描述: {project.get('description', 'N/A')[:100]}...")
                print(f"     星数: {project.get('stargazers_count', 0)}")
        
        return True
    except Exception as e:
        print(f"ERROR GitHub API测试失败: {e}")
        return False

def test_arxiv_api():
    """测试ArXiv API"""
    print("\n测试ArXiv API...")
    try:
        from daily_ai_collector import DailyAICollector
        collector = DailyAICollector()
        
        print("正在搜索ArXiv论文...")
        papers = collector.search_arxiv_papers()
        print(f"OK 找到 {len(papers)} 篇ArXiv论文")
        
        if papers:
            print("前3篇论文:")
            for i, paper in enumerate(papers[:3], 1):
                print(f"  {i}. {paper.get('title', 'N/A')[:80]}...")
                print(f"     作者: {', '.join(paper.get('authors', [])[:3])}")
        
        return True
    except Exception as e:
        print(f"ERROR ArXiv API测试失败: {e}")
        return False

def test_ai_summary():
    """测试AI摘要生成"""
    print("\n测试AI摘要生成...")
    try:
        from daily_ai_collector import DailyAICollector
        collector = DailyAICollector()
        
        if not os.getenv('GEMINI_API_KEY'):
            print("WARNING Gemini API Key未设置，跳过AI摘要测试")
            return True
        
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
        
        print("正在生成AI摘要...")
        summary = collector.generate_ai_summary(test_data)
        print("OK AI摘要生成成功")
        print("摘要预览:")
        print("-" * 50)
        print(summary[:300] + "..." if len(summary) > 300 else summary)
        print("-" * 50)
        return True
    except Exception as e:
        print(f"ERROR AI摘要生成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("每日AI动态数据收集测试")
    print("=" * 50)
    
    # 运行各项测试
    tests = [
        ("模块导入", test_imports),
        ("环境变量", test_environment),
        ("DailyAICollector类", test_daily_ai_collector),
        ("GitHub API", test_github_api),
        ("ArXiv API", test_arxiv_api),
        ("AI摘要生成", test_ai_summary)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"ERROR {test_name}测试出现异常: {e}")
            results.append((test_name, False))
    
    # 输出测试总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "OK 通过" if result else "ERROR 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("所有测试都通过了！数据收集功能正常工作。")
    else:
        print("部分测试失败，请检查API配置和网络连接。")

if __name__ == "__main__":
    main()
