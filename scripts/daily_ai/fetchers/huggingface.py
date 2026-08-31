import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
from scripts.daily_ai.models import ModelItem, PaperItem
from scripts.daily_ai.fetchers.base import BaseFetcher
from scripts.daily_ai.config.env_config import env_config

try:
    from huggingface_hub import HfApi, list_models
    USE_HF_HUB = True
except ImportError:
    USE_HF_HUB = False

# 知名大模型机构白名单（享有更高优先级）
KNOWN_MODEL_ORGS = {
    'qwen', 'deepseek-ai', 'mistralai', 'meta-llama', 'google', 'microsoft',
    'baai', 'thudm', 'minimaxai', '01-ai', 'kwai-kolors', 'black-forest-labs',
    'mlx-community', 'internlm', 'openbmb', 'stabilityai', 'tiiuae', 'cohere'
}


class HuggingFaceModelsFetcher(BaseFetcher):
    """获取 Hugging Face 趋势与高价值开源模型"""
    
    def fetch(self, limit: int = 20) -> List[ModelItem]:
        models = []
        try:
            headers = {}
            if env_config.HUGGINGFACE_API_KEY:
                headers['Authorization'] = f'Bearer {env_config.HUGGINGFACE_API_KEY}'
            
            # 使用 HTTP API 获取 trendingScore 倒序的高热度模型
            url = f"https://huggingface.co/api/models?sort=trendingScore&direction=-1&limit=60&full=true"
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                for item in data:
                    model_id = item.get('id', '')
                    if not model_id:
                        continue
                    
                    downloads = item.get('downloads', 0)
                    likes = item.get('likes', 0)
                    pipeline_tag = item.get('pipeline_tag', 'text-generation') or 'general-ai'
                    
                    org = model_id.split('/')[0].lower() if '/' in model_id else ''
                    is_known_org = org in KNOWN_MODEL_ORGS
                    
                    # 质量过滤条件：大厂开源 或者 (下载量>200 或 点赞>10)
                    if not is_known_org and downloads < 200 and likes < 10:
                        continue
                        
                    desc = f"任务类型: {pipeline_tag} | 社区点赞: 👍{likes} | 下载量: 📥{downloads}"
                    
                    models.append(ModelItem(
                        title=model_id,
                        url=f"https://huggingface.co/{model_id}",
                        source="Hugging Face",
                        description=desc,
                        pipeline_tag=pipeline_tag,
                        downloads=downloads
                    ))
            else:
                print(f"[WARNING] Hugging Face Models API 响应状态码: {response.status_code}")
                
        except Exception as e:
            print(f"[ERROR] HuggingFace Models 抓取失败: {e}")
             
        # 优先展示知名机构与高热度模型
        print(f"[INFO] Hugging Face Models: 成功筛选出 {len(models)} 个高价值新模型")
        return models[:limit]


class HuggingFacePapersFetcher(BaseFetcher):
    """获取 Hugging Face 每日社区精选高赞论文 (Daily Papers)"""
    
    def fetch(self, limit: int = 10) -> List[PaperItem]:
        papers = []
        try:
            today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            url = f"https://huggingface.co/api/daily_papers?date={today_str}"
            response = requests.get(url, timeout=15)
            
            data = []
            if response.status_code == 200 and response.json():
                data = response.json()
            else:
                # 尝试前一天（由于时区差异，今日论文可能尚未结算）
                yesterday_str = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
                url = f"https://huggingface.co/api/daily_papers?date={yesterday_str}"
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    data = response.json()

            for item in data:
                paper_info = item.get('paper', {})
                title = paper_info.get('title', '').strip()
                paper_id = paper_info.get('id', '')
                summary = paper_info.get('summary', '').strip()
                upvotes = paper_info.get('upvotes', 0)
                
                if not title or not paper_id:
                    continue

                authors = [a.get('name', 'Unknown') for a in paper_info.get('authors', [])]
                
                desc = f"社区推荐: 👍{upvotes} Upvotes | " + summary[:350]
                papers.append(PaperItem(
                    title=title,
                    url=f"https://huggingface.co/papers/{paper_id}",
                    source="HF Daily Papers",
                    description=desc,
                    authors=authors[:5],
                    published_date=paper_info.get('publishedAt', '')
                ))

            print(f"[INFO] Hugging Face Daily Papers 抓取成功，获取 {len(papers)} 篇精选论文")
        except Exception as e:
            print(f"[ERROR] HuggingFace Papers 抓取失败: {e}")
            
        return papers[:limit]

