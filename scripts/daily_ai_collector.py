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
            return []
            
        headers = {'Authorization': f'token {self.github_token}'}
        url = 'https://api.github.com/search/repositories'
        
        # 搜索过去24小时创建的AI相关项目
        yesterday, today = self.get_date_range()
        date_str = yesterday.strftime('%Y-%m-%d')
        
        params = {
            'q': f'AI machine-learning deep-learning created:>{date_str}',
            'sort': 'stars',
            'order': 'desc',
            'per_page': 10
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])
        except Exception as e:
            print(f"GitHub搜索错误: {e}")
            
        return []
    
    def search_huggingface_models(self) -> List[Dict]:
        """搜索Hugging Face新模型"""
        if not self.hf_token:
            return []
            
        headers = {'Authorization': f'Bearer {self.hf_token}'}
        url = 'https://huggingface.co/api/models'
        
        yesterday, today = self.get_date_range()
        date_str = yesterday.strftime('%Y-%m-%d')
        
        params = {
            'filter': 'pytorch',
            'sort': 'downloads',
            'direction': -1,
            'limit': 10
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                models = response.json()
                # 过滤最近创建的模型
                recent_models = [
                    model for model in models 
                    if model.get('created_at', '').startswith(date_str)
                ]
                return recent_models[:5]
        except Exception as e:
            print(f"Hugging Face搜索错误: {e}")
            
        return []
    
    def search_arxiv_papers(self) -> List[Dict]:
        """搜索ArXiv最新AI论文"""
        url = 'http://export.arxiv.org/api/query'
        
        yesterday, today = self.get_date_range()
        date_str = yesterday.strftime('%Y%m%d')
        
        params = {
            'search_query': f'cat:cs.AI OR cat:cs.LG OR cat:cs.CL AND submittedDate:[{date_str}0000 TO {date_str}2359]',
            'start': 0,
            'max_results': 10,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                # 解析XML响应
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                
                papers = []
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    paper = {
                        'title': entry.find('{http://www.w3.org/2005/Atom}title').text,
                        'authors': [author.find('{http://www.w3.org/2005/Atom}name').text 
                                  for author in entry.findall('{http://www.w3.org/2005/Atom}author')],
                        'summary': entry.find('{http://www.w3.org/2005/Atom}summary').text,
                        'link': entry.find('{http://www.w3.org/2005/Atom}id').text
                    }
                    papers.append(paper)
                return papers[:5]
        except Exception as e:
            print(f"ArXiv搜索错误: {e}")
            
        return []
    
    def generate_ai_summary(self, collected_data: Dict) -> str:
        """使用AI生成每日动态摘要"""
        prompt = f"""
        基于以下收集的AI技术动态数据，生成一份结构化的每日AI动态报告：

        数据：
        {json.dumps(collected_data, ensure_ascii=False, indent=2)}

        请按照以下格式生成内容：
        1. 🤖 新模型发布
        2. 🛠️ 新框架工具  
        3. 📱 新应用产品
        4. 📋 新标准规范
        5. 🔬 新开源项目
        6. 📄 新论文发布
        7. 🎤 科技访谈
        8. 📊 技术报告
        9. 🏛️ 论坛会议
        10. 📈 行业趋势

        每个分类下包含2-3个重要动态，每个动态包含标题、简要描述和链接。
        使用中文，内容要准确、简洁、有价值。
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI生成摘要错误: {e}")
            return self.generate_fallback_summary(collected_data)
    
    def generate_fallback_summary(self, collected_data: Dict) -> str:
        """生成备用摘要"""
        summary = "# 每日AI动态\n\n"
        
        if collected_data.get('github_projects'):
            summary += "## 🔬 新开源项目\n"
            for project in collected_data['github_projects'][:3]:
                summary += f"- **{project['name']}**: {project.get('description', '无描述')}\n"
            summary += "\n"
        
        if collected_data.get('hf_models'):
            summary += "## 🤖 新模型发布\n"
            for model in collected_data['hf_models'][:3]:
                summary += f"- **{model['modelId']}**: {model.get('pipeline_tag', '未知类型')}\n"
            summary += "\n"
        
        if collected_data.get('arxiv_papers'):
            summary += "## 📄 新论文发布\n"
            for paper in collected_data['arxiv_papers'][:3]:
                summary += f"- **{paper['title']}**: {paper['summary'][:100]}...\n"
            summary += "\n"
        
        return summary
    
    def create_daily_content(self) -> str:
        """创建每日内容文件"""
        yesterday, today = self.get_date_range()
        date_str = today.strftime('%Y-%m-%d')
        time_range = f"{yesterday.strftime('%Y年%m月%d日 %H:%M')} - {today.strftime('%Y年%m月%d日 %H:%M')}"
        
        # 收集数据
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
        
        print(f"✅ 每日AI动态已保存到: {file_path}")
        return file_path

def main():
    """主函数"""
    print("🚀 开始收集每日AI动态...")
    
    collector = DailyAICollector()
    file_path = collector.save_daily_content()
    
    print(f"✅ 每日AI动态收集完成: {file_path}")

if __name__ == "__main__":
    main()
