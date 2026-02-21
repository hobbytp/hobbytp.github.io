import requests
from typing import List, Dict, Any
from datetime import datetime
from scripts.daily_ai.models import ModelItem, PaperItem
from scripts.daily_ai.fetchers.base import BaseFetcher
from scripts.daily_ai.config.env_config import env_config

try:
    from huggingface_hub import HfApi, list_models
    USE_HF_HUB = True
except ImportError:
    USE_HF_HUB = False

class HuggingFaceModelsFetcher(BaseFetcher):
    """获取 Hugging Face 趋势模型 (侧重下载量与更新)"""
    def fetch(self, limit: int = 10, days_back: int = 3) -> List[ModelItem]:
        models = []
        try:
            if USE_HF_HUB:
                api = HfApi(token=env_config.HUGGINGFACE_API_KEY)
                hf_models = list(list_models(
                    sort="trendingScore",
                    direction=-1,
                    limit=limit * 2
                ))
                for item in hf_models:
                    pipeline_tag = getattr(item, 'pipeline_tag', 'unknown') or 'unknown'
                    downloads = getattr(item, 'downloads', 0)
                    
                    if downloads < 500:
                         continue
                         
                    models.append(ModelItem(
                        title=item.modelId,
                        url=f"https://huggingface.co/{item.modelId}",
                        source="HuggingFace",
                        description=f"Task: {pipeline_tag}, Downloads: {downloads}",
                        pipeline_tag=pipeline_tag,
                        downloads=downloads
                    ))
            else:
                # HTTP API Fallback
                headers = {}
                if env_config.HUGGINGFACE_API_KEY:
                    headers['Authorization'] = f'Bearer {env_config.HUGGINGFACE_API_KEY}'
                url = f"https://huggingface.co/api/models?sort=trendingScore&direction=-1&limit={limit*2}"
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    for item in data:
                        downloads = item.get('downloads', 0)
                        if downloads < 500:
                            continue
                        models.append(ModelItem(
                            title=item.get('id', ''),
                            url=f"https://huggingface.co/{item.get('id', '')}",
                            source="HuggingFace",
                            description=f"Task: {item.get('pipeline_tag', 'unknown')}, Downloads: {downloads}",
                            pipeline_tag=item.get('pipeline_tag'),
                            downloads=downloads
                        ))
        except Exception as e:
             print(f"[ERROR] HuggingFace Models 抓取失败: {e}")
             
        return models[:limit]

class HuggingFacePapersFetcher(BaseFetcher):
    """获取 Hugging Face 每日推荐论文"""
    def fetch(self, limit: int = 10) -> List[PaperItem]:
        papers = []
        try:
            date_str = datetime.utcnow().strftime('%Y-%m-%d')
            url = f"https://huggingface.co/api/daily_papers?date={date_str}"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                for item in data:
                    paper_info = item.get('paper', {})
                    authors = [a.get('name', 'Unknown') for a in paper_info.get('authors', [])]
                    papers.append(PaperItem(
                        title=paper_info.get('title', 'Unknown'),
                        url=f"https://huggingface.co/papers/{paper_info.get('id', '')}",
                        source="HuggingFace Papers",
                        description=paper_info.get('summary', '')[:500],
                        authors=authors,
                        published_date=paper_info.get('publishedAt', '')
                    ))
            else:
                 # 回退到前一天
                 yesterday_str = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
                 url = f"https://huggingface.co/api/daily_papers?date={yesterday_str}"
                 response = requests.get(url, timeout=15)
                 if response.status_code == 200:
                     data = response.json()
                     for item in data:
                         paper_info = item.get('paper', {})
                         authors = [a.get('name', 'Unknown') for a in paper_info.get('authors', [])]
                         papers.append(PaperItem(
                             title=paper_info.get('title', 'Unknown'),
                             url=f"https://huggingface.co/papers/{paper_info.get('id', '')}",
                             source="HuggingFace Papers",
                             description=paper_info.get('summary', '')[:500],
                             authors=authors,
                             published_date=paper_info.get('publishedAt', '')
                         ))
                         
        except Exception as e:
            print(f"[ERROR] HuggingFace Papers 抓取失败: {e}")
            
        return papers[:limit]
