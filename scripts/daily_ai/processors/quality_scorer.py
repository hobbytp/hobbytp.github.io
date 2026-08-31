import re
from typing import List
from scripts.daily_ai.models import BaseItem, GitHubProjectItem, ModelItem, PaperItem

# 官方与顶级权威信源
TIER1_OFFICIAL_SOURCES = {
    'openai news', 'anthropic news', 'google deepmind blog', 'google ai blog',
    'hugging face blog', 'microsoft ai blog', 'meta ai blog'
}

TIER2_MEDIA_SOURCES = {
    'hacker news', 'hf daily papers', 'techcrunch ai', 'the verge ai', 'venturebeat ai', '机器之心', '量子位'
}

# 深度技术关键词
TECHNICAL_KEYWORDS = [
    'deepseek', 'gpt-5', 'claude 3.7', 'gemini 2', 'qwen', 'llama', 'reasoning',
    'chain-of-thought', 'rlhf', 'agentic', 'multimodal', 'inference', 'quantization',
    'sota', 'open-weights', 'sparse attention', 'mixture-of-experts', 'moe', 'transformer'
]

# 低信息量/噪声关键词（扣分项）
NOISE_KEYWORDS = [
    'hiring', 'salary', 'career', 'layoff', 'complaint', 'lawsuit', 'rumor',
    'deal', 'discount', 'free trial', 'newsletter', 'opinion'
]


class QualityScorer:
    """四维质量评分雷达：信源权威度 + 社区热度/增速 + 技术深度关键词 + 噪声惩罚"""
    
    def process(self, items: List[BaseItem]) -> List[BaseItem]:
        for item in items:
            item.quality_score = self._calculate_score(item)
        # 按评分降序排列
        return sorted(items, key=lambda x: x.quality_score, reverse=True)
          
    def _calculate_score(self, item: BaseItem) -> float:
        score = 5.0
        src_lower = item.source.lower()
        content_lower = f"{item.title} {item.description or ''}".lower()
        
        # 1. 信源权威度加权
        if any(t1 in src_lower for t1 in TIER1_OFFICIAL_SOURCES):
            score += 3.0
        elif any(t2 in src_lower for t2 in TIER2_MEDIA_SOURCES):
            score += 2.0
            
        # 2. 根据不同实体类型的热度指标加权
        if isinstance(item, GitHubProjectItem):
            # Star 总量与每日爆发增速
            score += min(2.5, item.stars / 300)
            score += min(2.5, item.stars_per_day / 25)
        elif isinstance(item, ModelItem):
            # 下载量与任务类型
            score += min(3.0, item.downloads / 2000)
            if hasattr(item, 'pipeline_tag') and any(tag in str(item.pipeline_tag) for tag in ['text-generation', 'image-to-video', 'vision']):
                score += 1.0
        elif isinstance(item, PaperItem):
            # 作者团队与学术突破
            authors_count = len(item.authors)
            score += min(1.5, authors_count * 0.3)
            if 'upvotes' in (item.description or '').lower():
                score += 1.5
                
        # 3. 技术深度与重大突破关键词匹配
        matched_kw_count = sum(1 for kw in TECHNICAL_KEYWORDS if kw in content_lower)
        score += min(2.0, matched_kw_count * 0.7)
        
        # 4. 噪声抑制与扣分项
        matched_noise_count = sum(1 for nkw in NOISE_KEYWORDS if nkw in content_lower)
        score -= min(3.0, matched_noise_count * 1.0)
        
        # 标题过短或描述为空惩罚
        if len(item.title) < 10:
            score -= 1.5
        if not item.description or len(item.description) < 15:
            score -= 1.0
            
        # 强制限制在 [1.0, 10.0] 区间
        return round(min(10.0, max(1.0, score)), 2)

