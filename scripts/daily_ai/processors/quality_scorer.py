from typing import List, Union
from scripts.daily_ai.models import BaseItem, GitHubProjectItem, ModelItem, PaperItem

class QualityScorer:
    """评分引擎，用于根据源的不同类型评估条目质量"""
    
    def process(self, items: List[BaseItem]) -> List[BaseItem]:
         for item in items:
              item.quality_score = self._calculate_score(item)
         # 按评分排序，降序
         return sorted(items, key=lambda x: x.quality_score, reverse=True)
         
    def _calculate_score(self, item: BaseItem) -> float:
        score = 5.0
        
        # Based on item type
        if isinstance(item, GitHubProjectItem):
             score += min(3.0, item.stars / 1000)
             score += min(2.0, item.stars_per_day / 50)
        elif isinstance(item, ModelItem):
             score += min(5.0, item.downloads / 10000)
             if hasattr(item, 'pipeline_tag') and 'text-generation' in str(item.pipeline_tag):
                 score += 1.0
        elif isinstance(item, PaperItem):
             authors_count = len(item.authors)
             score += min(2.0, authors_count * 0.5)
             
             content_lower = f"{item.title} {item.description}".lower()
             heavy_keywords = ['large language model', 'llm', 'foundation model', 'gpt', 'llama', 'qwen', 'diffusion']
             if any(kw in content_lower for kw in heavy_keywords):
                 score += 2.0
        else:
             content_lower = f"{item.title} {item.description}".lower()
             heavy_keywords = ['openai', 'google', 'anthropic', 'gpt-5', 'gemini 2', 'claude 3', 'sora']
             if any(kw in content_lower for kw in heavy_keywords):
                 score += 2.5
             if item.source == 'NewsAPI':
                 score -= 1.0
                 
        # 强制界限控制
        return min(10.0, max(1.0, score))
