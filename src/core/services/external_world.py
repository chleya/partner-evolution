"""
外部世界接入模块 - RSS新闻获取
作为Cycle的外部养分
"""
import logging
import feedparser
from datetime import datetime, timezone
from typing import List, Dict, Optional
import time

logger = logging.getLogger(__name__)


class ExternalWorldFetcher:
    """获取外部世界信息作为Cycle养分"""
    
    def __init__(self):
        # 默认RSS源
        self.feed_urls = {
            "tech": [
                "https://news.ycombinator.com/rss",
                "https://www.reddit.com/r/programming/.rss",
            ],
            "ai": [
                "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
            ],
            "github": [
                "https://github.com/chleya/partner-evolution/commits/master.atom",
            ]
        }
        
        self.cache = {}
        self.cache_ttl = 3600  # 1小时缓存
    
    def fetch_feed(self, url: str, max_entries: int = 5) -> List[Dict]:
        """获取单个RSS源"""
        try:
            # 检查缓存
            cache_key = f"{url}_{max_entries}"
            if cache_key in self.cache:
                cached_time, cached_data = self.cache[cache_key]
                if time.time() - cached_time < self.cache_ttl:
                    return cached_data
            
            # 获取feed
            feed = feedparser.parse(url)
            
            entries = []
            for entry in feed.entries[:max_entries]:
                entries.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", "")[:200],
                    "link": entry.get("link", ""),
                    "published": entry.get("published", "")
                })
            
            # 缓存结果
            self.cache[cache_key] = (time.time(), entries)
            
            logger.info(f"Fetched {len(entries)} entries from {url}")
            return entries
            
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return []
    
    def fetch_all(self, max_per_feed: int = 3) -> List[Dict]:
        """获取所有RSS源"""
        all_entries = []
        
        for category, urls in self.feed_urls.items():
            for url in urls:
                entries = self.fetch_feed(url, max_per_feed)
                for entry in entries:
                    entry["category"] = category
                    all_entries.append(entry)
        
        logger.info(f"Total external entries: {len(all_entries)}")
        return all_entries
    
    def get_context_for_cycle(self) -> str:
        """生成供Cycle使用的外部世界上下文"""
        entries = self.fetch_all()
        
        if not entries:
            return ""
        
        context = "\n\n【外部世界最新动态】\n"
        
        for i, entry in enumerate(entries[:10], 1):
            context += f"{i}. {entry.get('title', 'N/A')[:80]}...\n"
            if entry.get('summary'):
                context += f"   {entry.get('summary')[:100]}...\n"
        
        return context
    
    def add_feed(self, category: str, url: str):
        """添加新的RSS源"""
        if category not in self.feed_urls:
            self.feed_urls[category] = []
        if url not in self.feed_urls[category]:
            self.feed_urls[category].append(url)
            logger.info(f"Added RSS feed: {category} -> {url}")


# 全局实例
_fetcher = None

def get_external_fetcher() -> ExternalWorldFetcher:
    """获取外部世界获取器"""
    global _fetcher
    if _fetcher is None:
        _fetcher = ExternalWorldFetcher()
    return _fetcher


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    fetcher = get_external_fetcher()
    context = fetcher.get_context_for_cycle()
    
    print("External World Context:")
    print(context[:500] if context else "No entries fetched")
