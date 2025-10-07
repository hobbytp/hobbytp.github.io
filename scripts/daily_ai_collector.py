#!/usr/bin/env python3
"""
每日AI动态收集脚本
自动收集AI领域的最新动态，包括新模型、新框架、新应用等
"""

import os
import json
import requests
import datetime
from typing import List, Dict, Any
import openai
from pathlib import Path
import yaml

class DailyAICollector:
    def __init__(self):
        #self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.openai_client = openai.OpenAI(
            api_key=os.getenv('GEMINI_API_KEY'),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        self.github_token = os.getenv('GITHUB_TOKEN')
        self.hf_token = os.getenv('HUGGINGFACE_API_KEY')
        self.content_dir = Path("content/zh/daily_ai")
        self.content_dir.mkdir(exist_ok=True)
        
    def get_date_range(self) -> tuple:
        """获取时间范围（昨天8点到今天8点）"""
        now = datetime.datetime.now()
        today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
        yesterday_8am = today_8am - datetime.timedelta(days=1)
        return yesterday_8am, today_8am
    
    def search_github_trending(self) -> List[Dict]:
        """搜索GitHub热门AI项目"""
        if not self.github_token:
            print("WARNING GitHub token未设置，跳过GitHub搜索")
            return []
            
        headers = {'Authorization': f'Bearer {self.github_token}'}
        url = 'https://api.github.com/search/repositories'
        
        # 搜索过去7天创建的AI相关项目（放宽时间范围）
        yesterday, today = self.get_date_range()
        date_str = (yesterday - datetime.timedelta(days=6)).strftime('%Y-%m-%d')
        
        params = {
            'q': f'AI machine-learning deep-learning created:>{date_str} language:python language:javascript',
            'sort': 'stars',
            'order': 'desc',
            'per_page': 20
        }
        
        try:
            print(f"搜索GitHub项目: {params['q']}")
            response = requests.get(url, headers=headers, params=params)
            print(f"GitHub API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                print(f"找到 {len(items)} 个GitHub项目")
                return items[:10]  # 返回前10个
            else:
                print(f"GitHub API错误: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"GitHub搜索错误: {e}")
            
        return []
    
    def search_huggingface_models(self) -> List[Dict]:
        """搜索Hugging Face新模型"""
        if not self.hf_token:
            print("WARNING Hugging Face token未设置，跳过HF搜索")
            return []
            
        headers = {'Authorization': f'Bearer {self.hf_token}'}
        url = 'https://huggingface.co/api/models'
        
        # 搜索过去7天创建的模型（放宽时间范围）
        yesterday, today = self.get_date_range()
        date_str = (yesterday - datetime.timedelta(days=6)).strftime('%Y-%m-%d')
        
        params = {
            'filter': 'pytorch',
            'sort': 'downloads',
            'direction': -1,
            'limit': 50
        }
        
        try:
            print(f"搜索Hugging Face模型")
            response = requests.get(url, headers=headers, params=params)
            print(f"HF API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                models = response.json()
                print(f"获取到 {len(models)} 个模型")
                
                # 过滤最近创建的模型
                recent_models = []
                for model in models:
                    created_at = model.get('created_at', '')
                    if created_at and created_at >= date_str:
                        recent_models.append(model)
                
                print(f"找到 {len(recent_models)} 个最近创建的模型")
                return recent_models[:5]
            else:
                print(f"HF API错误: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Hugging Face搜索错误: {e}")
            
        return []
    
    def search_arxiv_papers(self) -> List[Dict]:
        """搜索ArXiv最新AI论文"""
        url = 'http://export.arxiv.org/api/query'
        
        # 搜索过去7天的论文（放宽时间范围）
        yesterday, today = self.get_date_range()
        start_date = (yesterday - datetime.timedelta(days=6)).strftime('%Y%m%d')
        end_date = today.strftime('%Y%m%d')
        
        params = {
            'search_query': f'cat:cs.AI OR cat:cs.LG OR cat:cs.CL AND submittedDate:[{start_date}0000 TO {end_date}2359]',
            'start': 0,
            'max_results': 20,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        try:
            print(f"搜索ArXiv论文: {params['search_query']}")
            response = requests.get(url, params=params)
            print(f"ArXiv API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                # 解析XML响应
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                
                papers = []
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                    summary_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
                    link_elem = entry.find('{http://www.w3.org/2005/Atom}id')
                    
                    if title_elem is not None and summary_elem is not None and link_elem is not None:
                        paper = {
                            'title': title_elem.text.strip() if title_elem.text else '无标题',
                            'authors': [author.find('{http://www.w3.org/2005/Atom}name').text 
                                      for author in entry.findall('{http://www.w3.org/2005/Atom}author')
                                      if author.find('{http://www.w3.org/2005/Atom}name') is not None],
                            'summary': summary_elem.text.strip() if summary_elem.text else '无摘要',
                            'link': link_elem.text.strip() if link_elem.text else ''
                        }
                        papers.append(paper)
                
                print(f"找到 {len(papers)} 篇ArXiv论文")
                return papers[:5]
            else:
                print(f"ArXiv API错误: {response.status_code}")
        except Exception as e:
            print(f"ArXiv搜索错误: {e}")
            
        return []
    
    def generate_ai_summary(self, collected_data: Dict) -> str:
        """使用AI生成每日动态摘要"""
        # 先打印收集到的数据统计
        github_count = len(collected_data.get('github_projects', []))
        hf_count = len(collected_data.get('hf_models', []))
        arxiv_count = len(collected_data.get('arxiv_papers', []))
        
        print(f"数据收集统计:")
        print(f"   GitHub项目: {github_count}")
        print(f"   HF模型: {hf_count}")
        print(f"   ArXiv论文: {arxiv_count}")
        
        prompt = f"""
        基于以下收集的AI技术动态数据，生成一份结构化的每日AI动态报告：

        数据：
        {json.dumps(collected_data, ensure_ascii=False, indent=2)}

        请按照以下格式生成内容：
        1. 新模型发布
        2. 新框架工具  
        3. 新应用产品
        4. 新标准规范
        5. 新开源项目
        6. 新论文发布
        7. 科技访谈
        8. 技术报告
        9. 论坛会议
        10. 行业趋势

        每个分类下包含2-3个重要动态，每个动态包含标题、简要描述和链接。
        使用中文，内容要准确、简洁、有价值。
        如果某个分类没有数据，请明确说明"今日无新增动态"。
        """
        
        try:
            print("开始AI生成摘要...")
            response = self.openai_client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            print("AI摘要生成完成")
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI生成摘要错误: {e}")
            return self.generate_fallback_summary(collected_data)
    
    def generate_fallback_summary(self, collected_data: Dict) -> str:
        """生成备用摘要"""
        summary = "# 每日AI动态\n\n"
        
        if collected_data.get('github_projects'):
            summary += "## 新开源项目\n"
            for project in collected_data['github_projects'][:3]:
                summary += f"- **{project['name']}**: {project.get('description', '无描述')}\n"
            summary += "\n"
        
        if collected_data.get('hf_models'):
            summary += "## 新模型发布\n"
            for model in collected_data['hf_models'][:3]:
                summary += f"- **{model['modelId']}**: {model.get('pipeline_tag', '未知类型')}\n"
            summary += "\n"
        
        if collected_data.get('arxiv_papers'):
            summary += "## 新论文发布\n"
            for paper in collected_data['arxiv_papers'][:3]:
                summary += f"- **{paper['title']}**: {paper['summary'][:100]}...\n"
            summary += "\n"
        
        return summary
    
    def create_daily_content(self) -> str:
        """创建每日内容文件"""
        yesterday, today = self.get_date_range()
        date_str = today.strftime('%Y-%m-%d')
        time_range = f"{yesterday.strftime('%Y年%m月%d日 %H:%M')} - {today.strftime('%Y年%m月%d日 %H:%M')}"
        
        print(f"时间范围: {time_range}")
        
        # 收集数据
        print("开始收集数据...")
        collected_data = {
            'github_projects': self.search_github_trending(),
            'hf_models': self.search_huggingface_models(),
            'arxiv_papers': self.search_arxiv_papers()
        }
        
        # 生成AI摘要
        ai_summary = self.generate_ai_summary(collected_data)
        
        # 创建Markdown内容
        content = f"""---
title: "每日AI动态 - {date_str}"
date: {today.isoformat()}+08:00
draft: false
categories: ["daily_ai"]
tags: ["AI动态", "技术更新", "行业趋势"]
description: "{date_str}的AI技术动态汇总"
---

# 每日AI动态 - {date_str}

> 📅 **时间范围**: {time_range} (北京时间)

{ai_summary}

---

> 💡 **提示**: 本内容由GitHub Action自动生成，每日更新。如有遗漏或错误，欢迎通过Issues反馈。
"""
        
        return content
    
    def save_daily_content(self):
        """保存每日内容"""
        content = self.create_daily_content()
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        file_path = self.content_dir / f"{date_str}.md"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"每日AI动态已保存到: {file_path}")
        return file_path

def main():
    """主函数"""
    print("开始收集每日AI动态...")
    
    collector = DailyAICollector()
    file_path = collector.save_daily_content()
    
    print(f"每日AI动态收集完成: {file_path}")

if __name__ == "__main__":
    main()
