
import json
import os
from pathlib import Path
from typing import List, Set, Dict, Optional
from urllib.parse import urlparse
from datetime import datetime, timedelta
from scripts.daily_ai.models import BaseItem

class Deduplicator:
    def __init__(self, history_file: Optional[Path] = None, retention_days: int = 7):
        """
        初始化去重处理器
        :param history_file: 历史记录文件路径 (JSON格式)
        :param retention_days: 历史记录保留天数
        """
        self.history_file = Path(history_file) if history_file else None
        self.retention_days = retention_days
        
        # 内存中的去重集合 (normalize后的URL和标题)
        self.seen_urls: Set[str] = set()
        self.seen_titles: Set[str] = set()
        
        # 完整的历史记录数据 [{"url": "...", "title": "...", "date": "YYYY-MM-DD"}, ...]
        self.history_data: List[Dict] = []
        
        if self.history_file and self.history_file.exists():
            self._load_history()

    def _load_history(self):
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            valid_count = 0
            
            for item in data:
                # item format: {"url": "...", "title": "...", "date": "YYYY-MM-DD"}
                date_str = item.get('date', '2000-01-01')
                try:
                    item_date = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    continue
                    
                if item_date > cutoff_date:
                    url_norm = item.get('url', '')
                    title_norm = item.get('title', '')
                    
                    if url_norm:
                        self.seen_urls.add(url_norm)
                    if title_norm:
                        self.seen_titles.add(title_norm)
                        
                    self.history_data.append(item)
                    valid_count += 1
            
            print(f"[INFO] 已加载历史去重记录: {valid_count} 条 (保留 {self.retention_days} 天内)")
            
        except Exception as e:
            print(f"[WARNING] 加载历史记录失败: {e}")

    def save_state(self):
        """保存当前去重状态到文件"""
        if not self.history_file:
            return
            
        try:
            # Create directory if not exists
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 同样在保存时清理过期的
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            to_save = []
            
            for item in self.history_data:
                date_str = item.get('date', '2000-01-01')
                try:
                    item_date = datetime.strptime(date_str, '%Y-%m-%d')
                    if item_date > cutoff_date:
                        to_save.append(item)
                except ValueError:
                    pass
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(to_save, f, ensure_ascii=False, indent=2)
            print(f"[INFO] 已更新历史记录至: {self.history_file} (共 {len(to_save)} 条)")
            
        except Exception as e:
            print(f"[ERROR] 保存历史记录失败: {e}")

    def _normalize_url(self, url: str) -> str:
        if not url: return ""
        try:
             parsed = urlparse(url)
             return f"{parsed.netloc}{parsed.path}".rstrip('/').lower()
        except:
             return url.lower()
             
    def process(self, items: List[BaseItem]) -> List[BaseItem]:
         unique_items = []
         today_str = datetime.now().strftime('%Y-%m-%d')
         new_count = 0
         
         for item in items:
             title_lower = item.title.lower().strip()
             url_norm = self._normalize_url(item.url)
             
             if title_lower and title_lower in self.seen_titles:
                 # print(f"  - [Dedupe] 跳过重复标题: {title_lower[:30]}...")
                 continue
                 
             if url_norm and url_norm in self.seen_urls:
                 # print(f"  - [Dedupe] 跳过重复URL: {url_norm}")
                 continue
                 
             # Add to current memory
             self.seen_titles.add(title_lower)
             if url_norm: self.seen_urls.add(url_norm)
             
             # Add to history data
             self.history_data.append({
                 "url": url_norm,
                 "title": title_lower,
                 "date": today_str
             })
             
             unique_items.append(item)
             new_count += 1
             
         if new_count < len(items):
             print(f"[INFO] 去重: {len(items)} -> {new_count} (过滤掉 {len(items) - new_count} 条重复)")
             
         return unique_items
