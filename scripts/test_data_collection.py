#!/usr/bin/env python3
"""
数据收集测试脚本
用于本地测试每日AI动态数据收集功能
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from daily_ai_collector import DailyAICollector

def test_environment():
    """测试环境变量"""
    print("🔧 检查环境变量...")
    
    required_vars = {
        'GITHUB_TOKEN': 'GitHub API Token',
        'GEMINI_API_KEY': 'Gemini API Key',
        'HUGGINGFACE_API_KEY': 'Hugging Face API Key (可选)'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 8} (已设置)")
        else:
            print(f"❌ {var}: 未设置 - {description}")
            if var != 'HUGGINGFACE_API_KEY':  # HF token是可选的
                missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ 缺少必需的环境变量: {', '.join(missing_vars)}")
        print("请设置这些环境变量后再运行测试")
        return False
    
    print("✅ 环境变量检查完成")
    return True

def test_github_api():
    """测试GitHub API"""
    print("\n🔍 测试GitHub API...")
    
    collector = DailyAICollector()
    if not collector.github_token:
        print("❌ GitHub token未设置，跳过测试")
        return False
    
    try:
        projects = collector.search_github_trending()
        print(f"✅ GitHub API测试成功，找到 {len(projects)} 个项目")
        
        if projects:
            print("📋 前3个项目:")
            for i, project in enumerate(projects[:3], 1):
                print(f"  {i}. {project.get('name', 'N/A')} - {project.get('description', 'N/A')[:100]}...")
                print(f"     链接: {project.get('html_url', 'N/A')}")
                print(f"     星数: {project.get('stargazers_count', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ GitHub API测试失败: {e}")
        return False

def test_huggingface_api():
    """测试Hugging Face API"""
    print("\n🔍 测试Hugging Face API...")
    
    collector = DailyAICollector()
    if not collector.hf_token:
        print("⚠️ Hugging Face token未设置，跳过测试")
        return True  # HF token是可选的
    
    try:
        models = collector.search_huggingface_models()
        print(f"✅ Hugging Face API测试成功，找到 {len(models)} 个模型")
        
        if models:
            print("📋 前3个模型:")
            for i, model in enumerate(models[:3], 1):
                print(f"  {i}. {model.get('modelId', 'N/A')}")
                print(f"     标签: {model.get('pipeline_tag', 'N/A')}")
                print(f"     下载数: {model.get('downloads', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ Hugging Face API测试失败: {e}")
        return False

def test_arxiv_api():
    """测试ArXiv API"""
    print("\n🔍 测试ArXiv API...")
    
    collector = DailyAICollector()
    try:
        papers = collector.search_arxiv_papers()
        print(f"✅ ArXiv API测试成功，找到 {len(papers)} 篇论文")
        
        if papers:
            print("📋 前3篇论文:")
            for i, paper in enumerate(papers[:3], 1):
                print(f"  {i}. {paper.get('title', 'N/A')[:80]}...")
                print(f"     作者: {', '.join(paper.get('authors', [])[:3])}")
                print(f"     链接: {paper.get('link', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"❌ ArXiv API测试失败: {e}")
        return False

def test_ai_summary():
    """测试AI摘要生成"""
    print("\n🤖 测试AI摘要生成...")
    
    collector = DailyAICollector()
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Gemini API Key未设置，跳过AI摘要测试")
        return False
    
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
    
    try:
        summary = collector.generate_ai_summary(test_data)
        print("✅ AI摘要生成测试成功")
        print("📄 生成的摘要预览:")
        print("-" * 50)
        print(summary[:500] + "..." if len(summary) > 500 else summary)
        print("-" * 50)
        return True
    except Exception as e:
        print(f"❌ AI摘要生成测试失败: {e}")
        return False

def test_full_collection():
    """测试完整的数据收集流程"""
    print("\n🚀 测试完整数据收集流程...")
    
    collector = DailyAICollector()
    
    try:
        # 收集数据
        print("📊 开始收集数据...")
        collected_data = {
            'github_projects': collector.search_github_trending(),
            'hf_models': collector.search_huggingface_models(),
            'arxiv_papers': collector.search_arxiv_papers()
        }
        
        # 统计结果
        github_count = len(collected_data['github_projects'])
        hf_count = len(collected_data['hf_models'])
        arxiv_count = len(collected_data['arxiv_papers'])
        
        print(f"📈 数据收集结果:")
        print(f"   GitHub项目: {github_count}")
        print(f"   HF模型: {hf_count}")
        print(f"   ArXiv论文: {arxiv_count}")
        
        total_items = github_count + hf_count + arxiv_count
        if total_items == 0:
            print("⚠️ 没有收集到任何数据，请检查API配置")
            return False
        
        # 生成AI摘要
        if os.getenv('GEMINI_API_KEY'):
            print("🤖 生成AI摘要...")
            summary = collector.generate_ai_summary(collected_data)
            print("✅ AI摘要生成完成")
        else:
            print("⚠️ 未设置Gemini API Key，跳过AI摘要生成")
            summary = "测试摘要 - 未使用AI生成"
        
        # 保存测试结果
        test_file = Path("test_daily_ai_output.md")
        content = f"""# 测试结果 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 数据收集统计
- GitHub项目: {github_count}
- HF模型: {hf_count}  
- ArXiv论文: {arxiv_count}

## AI生成的摘要
{summary}

## 原始数据
```json
{json.dumps(collected_data, ensure_ascii=False, indent=2)}
```
"""
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 测试结果已保存到: {test_file}")
        return True
        
    except Exception as e:
        print(f"❌ 完整数据收集测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 每日AI动态数据收集测试")
    print("=" * 50)
    
    # 检查环境变量
    if not test_environment():
        print("\n❌ 环境变量检查失败，请先设置必要的API密钥")
        return
    
    # 运行各项测试
    tests = [
        ("GitHub API", test_github_api),
        ("Hugging Face API", test_huggingface_api),
        ("ArXiv API", test_arxiv_api),
        ("AI摘要生成", test_ai_summary),
        ("完整数据收集", test_full_collection)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试出现异常: {e}")
            results.append((test_name, False))
    
    # 输出测试总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("🎉 所有测试都通过了！数据收集功能正常工作。")
    else:
        print("⚠️ 部分测试失败，请检查API配置和网络连接。")

if __name__ == "__main__":
    main()
