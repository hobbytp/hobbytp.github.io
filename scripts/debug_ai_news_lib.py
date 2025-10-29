#!/usr/bin/env python3
"""
调试ai_news_collector_lib返回的数据格式
检查为什么所有文章都被跳过了
"""

import os
import sys
import datetime
from pathlib import Path

# 添加scripts目录到Python路径
sys.path.append(str(Path(__file__).parent))

def debug_ai_news_lib_data():
    """调试ai_news_collector_lib返回的数据格式"""
    print("=" * 60)
    print("调试ai_news_collector_lib数据格式")
    print("=" * 60)
    
    try:
        from ai_news_collector_lib import (
            AdvancedAINewsCollector,
            AdvancedSearchConfig,
        )
        print("[OK] ai_news_collector_lib 导入成功")
    except ImportError as e:
        print(f"[ERROR] ai_news_collector_lib 导入失败: {e}")
        return
    
    try:
        # 创建搜索配置
        search_config = AdvancedSearchConfig(
            enable_hackernews=True,
            enable_arxiv=True,
            enable_duckduckgo=True,
            enable_rss_feeds=True,
            enable_newsapi=True,
            enable_tavily=True,
            enable_google_search=True,
            enable_serper=True,
            enable_brave_search=True,
            enable_metasota_search=True,
            max_articles_per_source=2,  # 只获取少量数据进行调试
            days_back=0,
            similarity_threshold=0.85,
            enable_content_extraction=False,
            enable_keyword_extraction=True,
            cache_results=False,
        )
        
        # 创建收集器
        collector = AdvancedAINewsCollector(search_config)
        
        # 定义搜索主题
        topics = [
            "latest AI model releases today",
        ]
        
        print("开始收集数据...")
        
        # 异步收集
        import asyncio
        
        async def collect_async():
            if hasattr(collector, 'collect_multiple_topics'):
                return await collector.collect_multiple_topics(topics)
            else:
                result = await collector.collect_news_advanced(topics[0])
                return {"articles": result.get('articles', []), "unique_articles": len(result.get('articles', []))}
        
        result = asyncio.run(collect_async())
        articles = result.get('articles', [])
        
        print(f"收集到 {len(articles)} 条文章")
        print()
        
        if not articles:
            print("没有收集到任何文章，可能的原因：")
            print("1. API密钥未设置")
            print("2. 网络连接问题")
            print("3. 所有数据源都返回空结果")
            return
        
        # 分析前几篇文章的数据结构
        print("分析文章数据结构：")
        print("-" * 40)
        
        for i, article in enumerate(articles[:3]):  # 只分析前3篇
            print(f"\n文章 {i+1}:")
            print(f"标题: {article.get('title', 'N/A')[:50]}...")
            print(f"URL: {article.get('url', 'N/A')}")
            
            # 检查所有可能的日期字段
            date_fields = ['published_date', 'publishedAt', 'pubDate', 'date', 'created_at', 'createdAt', 'timestamp']
            found_date = False
            
            for field in date_fields:
                if field in article and article[field]:
                    print(f"{field}: {article[field]}")
                    found_date = True
            
            if not found_date:
                print("❌ 没有找到任何日期字段")
                print("可用的字段:", list(article.keys()))
            else:
                print("✅ 找到日期字段")
            
            print("-" * 40)
        
        # 检查时间过滤逻辑
        print("\n测试时间过滤逻辑：")
        print("-" * 40)
        
        yesterday = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)
        today = datetime.datetime.now(datetime.timezone.utc)
        
        for i, article in enumerate(articles[:3]):
            print(f"\n文章 {i+1} 时间过滤测试:")
            title = article.get('title', 'N/A')[:30]
            print(f"标题: {title}...")
            
            # 检查published字段（ai_news_collector_lib使用的字段名）
            published_date = article.get('published', '') or article.get('published_date', '')
            print(f"published: '{article.get('published', '')}'")
            print(f"published_date: '{article.get('published_date', '')}'")
            print(f"最终使用的日期: '{published_date}'")
            
            if not published_date or published_date == '':
                print("❌ 被跳过：无发布时间")
                continue
            
            try:
                # 解析发布时间
                if 'T' in published_date:
                    pub_time = datetime.datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                else:
                    pub_time = datetime.datetime.strptime(published_date, '%Y-%m-%d')
                
                # 确保时区一致性 - 如果pub_time没有时区信息，假设为UTC
                if pub_time.tzinfo is None:
                    pub_time = pub_time.replace(tzinfo=datetime.timezone.utc)
                
                now = datetime.datetime.now(datetime.timezone.utc)
                
                print(f"解析后的时间: {pub_time}")
                print(f"当前时间: {now}")
                print(f"昨天时间: {yesterday}")
                
                # 检查各种条件
                if pub_time > now:
                    print("❌ 被跳过：未来时间")
                elif pub_time < now - datetime.timedelta(days=7):
                    print("❌ 被跳过：超过7天")
                elif pub_time < yesterday:
                    print("❌ 被跳过：超过24小时")
                else:
                    print("✅ 通过过滤")
                    
            except Exception as e:
                print(f"❌ 时间解析错误: {e}")
        
    except Exception as e:
        print(f"调试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ai_news_lib_data()
