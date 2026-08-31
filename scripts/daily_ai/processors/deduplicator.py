
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
        self.first_seen_title: Dict[str, str] = {}
        self.first_seen_url: Dict[str, str] = {}
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
                        prev_date = self.first_seen_url.get(url_norm)
                        if prev_date is None or date_str < prev_date:
                            self.first_seen_url[url_norm] = date_str
                    if title_norm:
                        self.seen_titles.add(title_norm)
                        prev_date = self.first_seen_title.get(title_norm)
                        if prev_date is None or date_str < prev_date:
                            self.first_seen_title[title_norm] = date_str

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

    def _fuzzy_match_in_set(self, norm_title: str, seen_set: Set[str]) -> Optional[str]:
        """在给定集合中查找与标题精确/模糊匹配的条目，返回匹配项（无匹配返回 None）"""
        if not norm_title:
            return None
        for seen in seen_set:
            # 严格相等
            if norm_title == seen:
                return seen
            # 短标题略过模糊比较
            if len(norm_title) > 15 and len(seen) > 15:
                ratio = SequenceMatcher(None, norm_title, seen).ratio()
                if ratio >= self.similarity_threshold:
                    return seen
        return None

    def _first_seen_date(self, title_norm: str, url_norm: str) -> Optional[str]:
        """查询条目的首次出现日期：精确URL > 精确标题 > 模糊标题匹配；未出现过返回 None"""
        if url_norm and url_norm in self.first_seen_url:
            return self.first_seen_url[url_norm]
        if title_norm and title_norm in self.first_seen_title:
            return self.first_seen_title[title_norm]
        if title_norm:
            matched = self._fuzzy_match_in_set(title_norm, self.seen_titles)
            if matched and matched in self.first_seen_title:
                return self.first_seen_title[matched]
        return None


    def process(self, items: List[BaseItem]) -> List[BaseItem]:
        unique_items = []
        today_str = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d')
        new_count = 0
        same_day_kept = 0
        # 本次运行内的去重集合（防止同一次抓取中来自多个渠道的重复条目）
        run_seen_titles: Set[str] = set()
        run_seen_urls: Set[str] = set()

        for item in items:
            title_norm = self._normalize_title(item.title)
            url_norm = self._normalize_url(item.url)

            if not title_norm:
                continue

            # 1) 本次运行内部去重（同一批次内的重复来源，如 RSS 与 Google 报道同一事件）
            if self._fuzzy_match_in_set(title_norm, run_seen_titles) or (url_norm and url_norm in run_seen_urls):
                continue

            # 2) 历史去重：查询条目首次出现日期
            first_seen = self._first_seen_date(title_norm, url_norm)
            if first_seen is not None:
                if first_seen < today_str:
                    # 历史（非今天）已出现过 → 旧闻，丢弃
                    continue
                # 今天已出现过（同日重跑）→ 保留但不重复计数、不重复入库
                unique_items.append(item)
                same_day_kept += 1
                run_seen_titles.add(title_norm)
                if url_norm:
                    run_seen_urls.add(url_norm)
                continue

            # 3) 全新条目：保留并记录首次出现日期
            unique_items.append(item)
            new_count += 1
            run_seen_titles.add(title_norm)
            if url_norm:
                run_seen_urls.add(url_norm)
            self.seen_titles.add(title_norm)
            self.first_seen_title[title_norm] = today_str
            if url_norm:
                self.seen_urls.add(url_norm)
                self.first_seen_url[url_norm] = today_str
            self.history_data.append({
                "url": url_norm,
                "title": title_norm,
                "date": today_str
            })

        total_out = len(unique_items)
        dropped = len(items) - total_out
        if dropped > 0 or same_day_kept > 0:
            print(
                f"[INFO] 语义去重完成: {len(items)} -> {total_out} "
                f"(新增 {new_count} 条, 同日保留 {same_day_kept} 条, 过滤历史/重复 {dropped} 条)"
            )

        return unique_items

