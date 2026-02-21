from abc import ABC, abstractmethod
from typing import List, Any
from scripts.daily_ai.models import BaseItem

class BaseFetcher(ABC):
    """
    数据抓取器基类
    """
    def __init__(self):
        self.name = self.__class__.__name__
        
    @abstractmethod
    def fetch(self) -> List[Any]:
        """抓取并返回领域实体对象的列表（如 ArticleItem, GitHubProjectItem）"""
        pass
        
    def _is_recent(self, date_str: str) -> bool:
        """检查日期是否为最近 24 小时（基础实现，各子类可按需覆盖）"""
        # (暂缺实现，在 processor 里会通过专门的时间过滤去做去重)
        return True
