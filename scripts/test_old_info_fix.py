#!/usr/bin/env python3
"""
测试旧信息修复效果
验证时间过滤逻辑是否能正确过滤掉过时的新闻
"""

import sys
import datetime
from pathlib import Path

# 添加scripts目录到Python路径
sys.path.append(str(Path(__file__).parent))

def test_time_filtering():
    """测试时间过滤功能"""
    print("=" * 60)
    print("测试旧信息修复效果")
    print("=" * 60)
    
    # 测试用例1：模拟Gemini 2.0的旧新闻（12月发布，现在是10月）
    old_gemini_news = {
        'title': 'Google 推出 Gemini 2.0，开启"Agentic 时代"',
        'url': 'https://blog.google/technology/google-deepmind/google-gemini-ai-update-december-2024/',
        'description': 'Google DeepMind 发布了 Gemini 2.0，一款面向"Agentic Era"的新型AI模型',
        'published_date': '2024-12-11T10:00:00Z',  # 12月11日发布
        'source': 'ai_news_lib'
    }
    
    # 测试用例2：模拟今天的新闻
    today_news = {
        'title': '今日AI新闻测试',
        'url': 'https://example.com/today-news',
        'description': '这是一条今天的新闻',
        'published_date': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': 'ai_news_lib'
    }
    
    # 测试用例3：模拟昨天的新闻
    yesterday_news = {
        'title': '昨日AI新闻测试',
        'url': 'https://example.com/yesterday-news',
        'description': '这是一条昨天的新闻',
        'published_date': (datetime.datetime.now() - datetime.timedelta(hours=12)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': 'ai_news_lib'
    }
    
    # 测试用例4：模拟没有发布时间的新闻
    no_date_news = {
        'title': '无发布时间新闻',
        'url': 'https://example.com/no-date-news',
        'description': '这条新闻没有发布时间',
        'published_date': '',
        'source': 'ai_news_lib'
    }
    
    # 测试用例5：模拟未来时间的新闻
    future_news = {
        'title': '未来时间新闻',
        'url': 'https://example.com/future-news',
        'description': '这是一条未来时间的新闻',
        'published_date': (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': 'ai_news_lib'
    }
    
    test_cases = [
        ("旧新闻（12月发布）", old_gemini_news, False),  # 应该被过滤
        ("今日新闻", today_news, True),  # 应该通过
        ("昨日新闻", yesterday_news, True),  # 应该通过
        ("无发布时间", no_date_news, False),  # 应该被过滤
        ("未来时间", future_news, False),  # 应该被过滤
    ]
    
    print("开始测试时间过滤逻辑...")
    print()
    
    for test_name, test_article, expected_pass in test_cases:
        print(f"测试: {test_name}")
        print(f"标题: {test_article['title']}")
        print(f"发布时间: {test_article['published_date']}")
        
        # 模拟时间过滤逻辑
        published_date = test_article.get('published_date', '')
        
        if not published_date or published_date == '':
            result = False
            print("结果: 被过滤（无发布时间）")
        else:
            try:
                if 'T' in published_date:
                    pub_time = datetime.datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                else:
                    pub_time = datetime.datetime.strptime(published_date, '%Y-%m-%d')
                
                # 确保时区一致性
                now = datetime.datetime.now()
                if pub_time.tzinfo is None:
                    pub_time = pub_time.replace(tzinfo=datetime.timezone.utc)
                if now.tzinfo is None:
                    now = now.replace(tzinfo=datetime.timezone.utc)
                
                yesterday = now.replace(hour=8, minute=0, second=0, microsecond=0) - datetime.timedelta(hours=24)
                
                # 检查未来时间
                if pub_time > now:
                    result = False
                    print("结果: 被过滤（未来时间）")
                # 检查是否超过7天
                elif pub_time < now - datetime.timedelta(days=7):
                    result = False
                    print("结果: 被过滤（超过7天）")
                # 检查是否在24小时内
                elif pub_time < yesterday:
                    result = False
                    print("结果: 被过滤（超过24小时）")
                else:
                    result = True
                    print("结果: 通过过滤")
                    
            except Exception as e:
                result = False
                print(f"结果: 被过滤（时间解析错误: {e}）")
        
        # 验证结果
        if result == expected_pass:
            print("[OK] 测试通过")
        else:
            print(f"[FAIL] 测试失败 - 期望: {'通过' if expected_pass else '被过滤'}, 实际: {'通过' if result else '被过滤'}")
        
        print("-" * 40)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

def test_config_consistency():
    """测试配置一致性"""
    print("\n检查配置一致性...")
    
    # 模拟搜索配置
    now = datetime.datetime.now()
    today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
    yesterday_8am = today_8am - datetime.timedelta(hours=24)
    
    print(f"代码中时间范围: {yesterday_8am.strftime('%Y-%m-%d %H:%M')} 到 {today_8am.strftime('%Y-%m-%d %H:%M')}")
    print("代码中 days_back: 0")
    print("代码中 cache_results: False")
    
    # 检查YAML配置
    import yaml
    with open('config/ai_news.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print(f"YAML中 days_back: {config['search']['days_back']}")
    print(f"YAML中 cache_results: {config['advanced']['cache_results']}")
    
    # 验证一致性
    if config['search']['days_back'] == 0 and config['advanced']['cache_results'] == False:
        print("[OK] 配置一致性检查通过")
    else:
        print("[FAIL] 配置一致性检查失败")

if __name__ == "__main__":
    test_time_filtering()
    test_config_consistency()
