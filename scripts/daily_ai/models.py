from typing import List, Optional
from pydantic import BaseModel, Field

class BaseItem(BaseModel):
    title: str
    url: str
    source: str
    description: Optional[str] = ""
    quality_score: float = 5.0
    published_date: Optional[str] = None
    
class ArticleItem(BaseItem):
    """用于新闻、报道和应用"""
    pass

class PaperItem(BaseItem):
    """用于 arXiv / HF Papers 的学术论文"""
    authors: List[str] = Field(default_factory=list)

class GitHubProjectItem(BaseItem):
    """用于 GitHub 趋势项目"""
    stars: int = 0
    stars_per_day: float = 0.0
    language: Optional[str] = None

class ModelItem(BaseItem):
    """用于 HuggingFace 模型"""
    pipeline_tag: Optional[str] = None
    downloads: int = 0
