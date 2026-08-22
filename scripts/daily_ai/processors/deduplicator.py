
import json
import os
import re
from pathlib import Path
from typing import List, Set, Dict, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from scripts.daily_ai.models import BaseItem

BEIJING_TZ = timezone(timedelta(hours=8))



class Deduplicator:
    """去重引擎：支持 URL 规范化清理、历史状态持久化以及标题模糊相似度去重"""

    def __init__(self, history_file: Optional[Path] = None, retention_days: int = 7, title_similarity_threshold: float = 0.78):
        self.history_file = Path(history_file) if history_file else None
        self.retention_days = retention_days
        self.similarity_threshold = title_similarity_threshold
        
        self.seen_urls: Set[str] = set()
        self.seen_titles: Set[str] = set()
        self.history_data: List[Dict] = []
        
        if self.history_file and self.history_file.exists():
            self._load_history()

    def _load_history(self):
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            cutoff_date = datetime.now(BEIJING_TZ).replace(tzinfo=None) - timedelta(days=self.retention_days)
            valid_count = 0

            
            for item in data:
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
        if not self.history_file:
            return
            
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            cutoff_date = datetime.now(BEIJING_TZ).replace(tzinfo=None) - timedelta(days=self.retention_days)

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
            print(f"[INFO] 已更新历史去重库: {self.history_file} (保留 {len(to_save)} 条)")
        except Exception as e:
            print(f"[ERROR] 保存历史记录失败: {e}")

    def _normalize_url(self, url: str) -> str:
        if not url:
            return ""
        try:
            parsed = urlparse(url)
            # 过滤追踪参数
            params = parse_qs(parsed.query)
            clean_params = {k: v for k, v in params.items() if not k.startswith(('utm_', 'ref', 'source', 'fbclid', 'gclid'))}
            clean_query = urlencode(clean_params, doseq=True)
            clean_url = urlunparse((parsed.scheme, parsed.netloc.lower(), parsed.path.rstrip('/'), '', clean_query, ''))
            return clean_url
        except Exception:
            return url.lower()

    def _normalize_title(self, title: str) -> str:
        # 去除特殊标点，保留核心词
        clean = re.sub(r'[^\w\s\u4e00-\u9fa5]', ' ', title.lower())
        return re.sub(r'\s+', ' ', clean).strip()

    def _is_similar_to_seen(self, title: str) -> bool:
        norm = self._normalize_title(title)
        if not norm:
            return False
        for seen in self.seen_titles:
            # 严格相等
            if norm == seen:
                return True
            # 短标题略过模糊比较
            if len(norm) > 15 and len(seen) > 15:
                ratio = SequenceMatcher(None, norm, seen).ratio()
                if ratio >= self.similarity_threshold:
                    return True
        return False

    def process(self, items: List[BaseItem]) -> List[BaseItem]:
        unique_items = []
        today_str = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d')
        new_count = 0

        
        for item in items:
            title_norm = self._normalize_title(item.title)
            url_norm = self._normalize_url(item.url)
            
            if not title_norm:
                continue

            if self._is_similar_to_seen(item.title):
                continue
                
            if url_norm and url_norm in self.seen_urls:
                continue
                
            self.seen_titles.add(title_norm)
            if url_norm:
                self.seen_urls.add(url_norm)
            
            self.history_data.append({
                "url": url_norm,
                "title": title_norm,
                "date": today_str
            })
            
            unique_items.append(item)
            new_count += 1
            
        if new_count < len(items):
            print(f"[INFO] 语义去重完成: {len(items)} -> {new_count} (过滤 {len(items) - new_count} 条同质/历史内容)")
            
        return unique_items

