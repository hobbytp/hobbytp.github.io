#!/usr/bin/env python3
"""
数据摄取管道 (Data Ingestion Pipeline)
解析 Hugo Markdown 文件，向量化并通过 REST API 存入 Cloudflare Vectorize
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
import frontmatter

from dotenv import load_dotenv
load_dotenv()

class BlogIngester:
    """博客内容摄取器"""
    
    # Cloudflare Workers AI Embedding 模型
    EMBEDDING_MODEL = "@cf/baai/bge-base-en-v1.5"
    
    # 文本切片配置
    CHUNK_SIZE = 500  # 每个chunk约500字符
    CHUNK_OVERLAP = 50  # 重叠50字符
    
    def __init__(self, content_dir: str = "content", base_url: str = "https://hobbytp.github.io", state_file: str = ".ingest_state.json"):
        self.content_dir = Path(content_dir)
        self.base_url = base_url.rstrip('/')
        self.state_file = Path(state_file)
        self.state = self.load_state()
        
        # 从环境变量读取Cloudflare配置
        # 注意：CF_ 前缀已弃用，使用 CLOUDFLARE_ 前缀（Cloudflare官方要求）
        self.account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        self.index_name = os.getenv('CLOUDFLARE_VECTORIZE_INDEX_NAME', 'blog-index')
        
        # 调试信息：显示环境变量是否加载（不显示完整token）
        print("\n🔧 Cloudflare 配置检查:")
        if self.account_id:
            print(f"   ✅ CLOUDFLARE_ACCOUNT_ID: {self.account_id[:8]}...{self.account_id[-4:]}")
        else:
            print("   ❌ CLOUDFLARE_ACCOUNT_ID: 未设置")
        
        if self.api_token:
            token_preview = f"{self.api_token[:8]}...{self.api_token[-4:]}" if len(self.api_token) > 12 else "***"
            print(f"   ✅ CLOUDFLARE_API_TOKEN: {token_preview} (长度: {len(self.api_token)})")
        else:
            print("   ❌ CLOUDFLARE_API_TOKEN: 未设置")
        
        print(f"   📦 Vectorize索引名称: {self.index_name}\n")
        
        if not self.account_id or not self.api_token:
            raise ValueError(
                "请设置环境变量 CLOUDFLARE_ACCOUNT_ID 和 CLOUDFLARE_API_TOKEN\n"
                "注意：CF_ 前缀已弃用，请使用 CLOUDFLARE_ 前缀\n"
                "获取方式：\n"
                "1. CLOUDFLARE_ACCOUNT_ID: Cloudflare Dashboard -> 右侧栏显示\n"
                "2. CLOUDFLARE_API_TOKEN: https://dash.cloudflare.com/profile/api-tokens\n"
                "   需要权限：Account: Cloudflare Workers AI:Edit, Account: Vectorize:Edit\n"
                "参考文档: https://developers.cloudflare.com/workers/wrangler/system-environment-variables/"
            )
        
        # 清理API Token（移除引号、空白字符、换行符）
        self.api_token = self.api_token.strip()
        # 移除可能的引号包裹
        if (self.api_token.startswith('"') and self.api_token.endswith('"')) or \
           (self.api_token.startswith("'") and self.api_token.endswith("'")):
            self.api_token = self.api_token[1:-1].strip()
        # 移除所有空白字符和换行符（token应该是连续的字符串）
        self.api_token = ''.join(self.api_token.split())
        
        # Cloudflare API 端点
        self.ai_api_base = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run"
        # Vectorize v2 REST API 基础路径（v1已弃用，避免 incorrect_api_version 错误）
        self.vectorize_api_base_v2 = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/vectorize/v2/indexes/{self.index_name}"
        
        # 请求头
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # 配置代理（如果设置了代理环境变量）
        self.proxies = None
        http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
        https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')
        if http_proxy or https_proxy:
            self.proxies = {
                'http': http_proxy,
                'https': https_proxy or http_proxy
            }
            print(f"🌐 检测到代理设置: {https_proxy or http_proxy}\n")
            
    def load_state(self) -> Dict[str, str]:
        """加载摄取状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  加载状态文件失败: {e}")
        return {}

    def save_state(self):
        """保存摄取状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  保存状态文件失败: {e}")

    def calculate_file_hash(self, file_path: Path) -> str:
        """计算文件内容的MD5哈希"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print(f"⚠️  计算哈希失败 {file_path}: {e}")
            return ""
    
    def extract_frontmatter(self, file_path: Path) -> Dict:
        """提取Markdown文件的frontmatter"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                return {
                    'title': post.metadata.get('title', ''),
                    'date': post.metadata.get('date', ''),
                    'content': post.content,
                    # 额外保留可能的分类字段，供后续解析覆盖或回退
                    'category': post.metadata.get('category', None),
                    'categories': post.metadata.get('categories', None),
                }
        except Exception as e:
            print(f"❌ 解析frontmatter失败 {file_path}: {e}")
            return {}
    
    def clean_markdown(self, text: str) -> str:
        """清洗Markdown符号，保留纯文本"""
        # 移除图片标记 ![alt](url)
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
        # 移除链接但保留文本 [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # 移除粗体/斜体标记
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^\*]+)\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        # 移除代码块
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`[^`]+`', '', text)
        # 移除标题标记
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        # 移除水平线
        text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
        # 移除多余空白
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        return text
    
    def chunk_text(self, text: str) -> List[str]:
        """将文本切片，约500字符/chunk，重叠50字符"""
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # 计算chunk结束位置
            end = min(start + self.CHUNK_SIZE, text_length)
            
            # 如果不是最后一块，尝试在句号、换行符处断开
            if end < text_length:
                # 向后查找合适的断点（句号、换行符）
                for i in range(end, max(start + self.CHUNK_SIZE - 100, start), -1):
                    if text[i] in '。\n':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # 如果已经到达文档末尾，退出循环
            if end >= text_length:
                break
            
            # 下一个chunk的起始位置（考虑重叠）
            start = end - self.CHUNK_OVERLAP
            # 防止无限循环：如果start没有前进，强制退出
            if start >= end:
                break
        
        return chunks
    
    def generate_url(self, file_path: Path) -> str:
        """根据文件路径生成文章URL"""
        # 获取相对于content目录的路径
        try:
            rel_path = file_path.relative_to(self.content_dir)
        except ValueError:
            # 如果不在content目录下，使用文件名
            rel_path = file_path.name
        
        # 转换为URL路径：content/zh/posts/article.md -> /zh/posts/article/
        url_path = str(rel_path).replace('\\', '/')
        if url_path.endswith('.md'):
            url_path = url_path[:-3]  # 移除.md
        
        # 确保以/开头
        if not url_path.startswith('/'):
            url_path = '/' + url_path
        
        # 如果不是以/结尾，添加/
        if not url_path.endswith('/'):
            url_path += '/'
        
        return urljoin(self.base_url, url_path)

    def extract_lang_and_category(self, file_path: Path, fm: Dict) -> Dict[str, Optional[str]]:
        """从路径和front matter解析语言和分类。
        优先使用front matter中的category，其次从路径 content/<lang>/<category>/... 推断。
        """
        lang: Optional[str] = None
        category_from_path: Optional[str] = None
        # 基于相对路径解析
        try:
            rel = file_path.relative_to(self.content_dir)
            parts = list(rel.parts)
            if len(parts) >= 2:
                lang = parts[0]
                category_from_path = parts[1]
        except ValueError:
            # 尝试基于绝对路径定位 content 段
            parts = list(file_path.parts)
            if 'content' in parts:
                idx = parts.index('content')
                if len(parts) > idx + 2:
                    lang = parts[idx + 1]
                    category_from_path = parts[idx + 2]

        # front matter 优先
        fm_cat: Optional[str] = None
        if fm:
            raw_cat = fm.get('category')
            raw_cats = fm.get('categories')
            if isinstance(raw_cat, str) and raw_cat.strip():
                fm_cat = raw_cat.strip()
            elif isinstance(raw_cats, list) and len(raw_cats) > 0:
                fm_cat = str(raw_cats[0]).strip()
            elif isinstance(raw_cats, str) and raw_cats.strip():
                fm_cat = raw_cats.strip()

        category = fm_cat or category_from_path
        return {"lang": lang, "category": category}
    
    def generate_chunk_id(self, url: str, chunk_index: int) -> str:
        """生成确定性ID: md5(full_url + chunk_index)"""
        content = f"{url}{chunk_index}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """调用Cloudflare Workers AI生成向量"""
        if not texts:
            return []
        
        url = f"{self.ai_api_base}/{self.EMBEDDING_MODEL}"
        
        # 准备请求数据：Cloudflare Workers AI API期望单个文本或文本数组
        if len(texts) == 1:
            payload = {"text": texts[0]}
        else:
            payload = {"text": texts}
        
        try:
            # 支持批量处理
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                proxies=self.proxies,
                timeout=60
            )
            
            # 详细的错误处理
            if response.status_code == 401:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('errors', [{}])[0].get('message', 'Unknown error')
                raise ValueError(
                    f"认证失败 (401): {error_msg}\n"
                    f"请检查：\n"
                    f"1. CLOUDFLARE_API_TOKEN 是否正确\n"
                    f"2. API Token 是否已过期\n"
                    f"3. API Token 是否有 Workers AI 和 Vectorize 权限\n"
                    f"4. 环境变量是否正确加载（检查.env文件）\n"
                    f"响应详情: {error_data}"
                )
            elif response.status_code == 403:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('errors', [{}])[0].get('message', 'Unknown error')
                raise ValueError(
                    f"权限不足 (403): {error_msg}\n"
                    f"请确保 API Token 有以下权限：\n"
                    f"- Account: Cloudflare Workers AI:Edit\n"
                    f"- Account: Vectorize:Edit"
                )
            
            response.raise_for_status()
            
            # Cloudflare Workers AI 可能返回两种结构：
            # 1) 直接在根上包含 data / embedding
            # 2) 将实际结果放在 result 字段中，形如：
            #    {"result": {"data": [[...]], "shape": [N, 768], ...}, "success": true, ...}
            result_outer = response.json()
            result = result_outer.get('result', result_outer)
            
            # 处理返回格式：可能是 {data: [[...]], shape: [...]} 或 {data: [{embedding: [...]}]}
            if 'data' in result:
                if isinstance(result['data'], list) and len(result['data']) > 0:
                    if isinstance(result['data'][0], dict) and 'embedding' in result['data'][0]:
                        # OpenAI兼容格式
                        return [item['embedding'] for item in result['data']]
                    elif isinstance(result['data'][0], list):
                        # 直接是向量数组
                        return result['data']
            
            # 如果格式不符合预期，尝试其他可能的结构
            if 'embedding' in result:
                return [result['embedding']]
            
            raise ValueError(f"无法解析embedding响应格式: {result}")
            
        except requests.exceptions.ProxyError as e:
            raise ConnectionError(
                f"代理连接失败: {e}\n"
                f"请检查代理设置或临时禁用代理环境变量（HTTP_PROXY, HTTPS_PROXY）"
            )
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"网络连接失败: {e}\n"
                f"请检查：\n"
                f"1. 网络连接是否正常\n"
                f"2. 代理设置是否正确（如果使用代理）\n"
                f"3. Cloudflare API 是否可访问"
            )
        except requests.exceptions.RequestException as e:
            print(f"❌ 生成embedding失败: {e}")
            if hasattr(e.response, 'text'):
                print(f"响应内容: {e.response.text}")
            raise
    
    def upload_to_vectorize(self, vectors: List[Dict]) -> bool:
        """批量上传向量到Cloudflare Vectorize (ndjson格式)"""
        if not vectors:
            return True
        
        url = f"{self.vectorize_api_base_v2}/upsert"
        
        # 准备ndjson格式数据
        ndjson_lines = []
        for vec in vectors:
            ndjson_lines.append(json.dumps(vec))
        
        ndjson_data = '\n'.join(ndjson_lines)
        
        try:
            response = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/x-ndjson"
                },
                data=ndjson_data,
                proxies=self.proxies,
                timeout=120
            )
            
            # 详细的错误处理
            if response.status_code == 401:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('errors', [{}])[0].get('message', 'Unknown error')
                raise ValueError(
                    f"认证失败 (401): {error_msg}\n"
                    f"请检查 CLOUDFLARE_API_TOKEN 是否正确且有 Vectorize 权限"
                )
            elif response.status_code == 404:
                raise ValueError(
                    f"索引不存在 (404): {self.index_name}\n"
                    f"请先创建 Vectorize 索引：\n"
                    f"npx wrangler vectorize create {self.index_name} --dimensions=768 --metric=cosine"
                )
            
            response.raise_for_status()
            return True
            
        except requests.exceptions.ProxyError as e:
            raise ConnectionError(
                f"代理连接失败: {e}\n"
                f"请检查代理设置或临时禁用代理环境变量（HTTP_PROXY, HTTPS_PROXY）"
            )
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"网络连接失败: {e}\n"
                f"请检查网络连接和代理设置"
            )
        except requests.exceptions.RequestException as e:
            print(f"❌ 上传到Vectorize失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    print(f"响应内容: {error_data}")
                except:
                    print(f"响应内容: {e.response.text}")
            raise
    
    def process_file(self, file_path: Path) -> int:
        """处理单个Markdown文件，返回处理的chunk数量"""
        print(f"\n📄 处理文件: {file_path}")
        
        # 提取frontmatter
        metadata = self.extract_frontmatter(file_path)
        if not metadata:
            print(f"⚠️  跳过（无法解析frontmatter）")
            return 0
        
        title = metadata.get('title', '')
        content = metadata.get('content', '')
        
        if not content:
            print(f"⚠️  跳过（内容为空）")
            return 0
        
        # 生成URL
        url = self.generate_url(file_path)
        print(f"   URL: {url}")
        print(f"   标题: {title}")
        
        # 清洗Markdown
        clean_text = self.clean_markdown(content)
        
        # 文本切片
        chunks = self.chunk_text(clean_text)
        print(f"   生成 {len(chunks)} 个chunks")
        
        if not chunks:
            print(f"⚠️  跳过（无有效chunks）")
            return 0
        
        # 批量生成embeddings
        print(f"   🔄 生成embeddings...")
        try:
            embeddings = self.generate_embeddings(chunks)
        except Exception as e:
            print(f"❌ 生成embeddings失败: {e}")
            return 0
        
        if len(embeddings) != len(chunks):
            print(f"⚠️  embeddings数量({len(embeddings)})与chunks数量({len(chunks)})不匹配")
            return 0
        
        # 准备向量数据
        vectors = []
        lc = self.extract_lang_and_category(file_path, metadata)
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = self.generate_chunk_id(url, i)
            vectors.append({
                "id": chunk_id,
                "values": embedding,
                "metadata": {
                    "url": url,
                    "title": title,
                    "text": chunk,
                    "chunk_index": i,
                    # 可筛选字段：category（可通过 wrangler 创建metadata索引）
                    "category": lc.get("category")
                }
            })
        
        # 批量上传到Vectorize
        print(f"   📤 上传到Vectorize...")
        if self.upload_to_vectorize(vectors):
            print(f"   ✅ 成功上传 {len(vectors)} 个向量")
            return len(vectors)
        else:
            print(f"   ❌ 上传失败")
            return 0
    
    def ingest_all(self, pattern: str = "**/*.md", force: bool = False) -> Dict[str, int]:
        """处理所有Markdown文件"""
        stats = {
            'total_files': 0,
            'processed_files': 0,
            'skipped_files': 0,
            'total_chunks': 0,
            'failed_files': 0
        }
        
        # 查找所有Markdown文件
        md_files = list(self.content_dir.rglob(pattern))
        # 排除_index.md文件
        md_files = [f for f in md_files if f.name != '_index.md']
        
        stats['total_files'] = len(md_files)
        print(f"\n📚 找到 {stats['total_files']} 个Markdown文件")
        
        state_changed = False
        
        for file_path in md_files:
            try:
                # 计算相对路径作为key
                rel_path = str(file_path.relative_to(self.content_dir))
                current_hash = self.calculate_file_hash(file_path)
                
                # 检查是否需要跳过
                if not force and rel_path in self.state and self.state[rel_path] == current_hash:
                    # print(f"⏩ 跳过未修改文件: {rel_path}")
                    stats['skipped_files'] += 1
                    continue
                
                chunks_count = self.process_file(file_path)
                if chunks_count > 0:
                    stats['processed_files'] += 1
                    stats['total_chunks'] += chunks_count
                    # 更新状态
                    self.state[rel_path] = current_hash
                    state_changed = True
                else:
                    stats['failed_files'] += 1
            except Exception as e:
                print(f"❌ 处理文件失败 {file_path}: {e}")
                stats['failed_files'] += 1
        
        # 保存状态
        if state_changed:
            self.save_state()
            print(f"💾 状态已保存到 {self.state_file}")
        
        return stats


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='博客内容摄取到Cloudflare Vectorize')
    parser.add_argument(
        '--content-dir',
        default='content',
        help='内容目录路径 (默认: content)'
    )
    parser.add_argument(
        '--base-url',
        default='https://hobbytp.github.io',
        help='博客基础URL (默认: https://hobbytp.github.io)'
    )
    parser.add_argument(
        '--file',
        help='处理单个文件（相对于content目录的路径）'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制重新处理所有文件，忽略缓存状态'
    )
    
    args = parser.parse_args()
    
    try:
        ingester = BlogIngester(
            content_dir=args.content_dir,
            base_url=args.base_url
        )
        
        if args.file:
            # 处理单个文件
            file_path = Path(args.content_dir) / args.file
            if not file_path.exists():
                print(f"❌ 文件不存在: {file_path}")
                return 1
            
            chunks_count = ingester.process_file(file_path)
            print(f"\n✅ 完成！处理了 {chunks_count} 个chunks")
        else:
            # 处理所有文件
            stats = ingester.ingest_all(force=args.force)
            print(f"\n{'='*60}")
            print(f"📊 处理统计:")
            print(f"   总文件数: {stats['total_files']}")
            print(f"   成功处理: {stats['processed_files']}")
            print(f"   跳过文件: {stats['skipped_files']}")
            print(f"   失败文件: {stats['failed_files']}")
            print(f"   总chunks: {stats['total_chunks']}")
            print(f"{'='*60}")
        
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
