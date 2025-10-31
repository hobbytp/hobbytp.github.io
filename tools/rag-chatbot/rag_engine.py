#!/usr/bin/env python3
"""
Hugo Blog RAG Chatbot Engine

基于Retrieval-Augmented Generation的智能问答系统：
- 自动索引Hugo博客内容
- 基于向量检索的相关内容搜索
- 结合上下文的智能回答生成
- 支持多语言内容理解
- 实时内容更新和索引维护

使用方法：
python rag_engine.py [选项]

选项：
--rebuild-index    重建向量索引
--query TEXT       执行查询并生成回答
--serve            启动Web服务
--update-index     更新现有索引（增量）
--stats            显示索引统计信息
"""

import os
import sys
import json
import time
import asyncio
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import hashlib
import pickle

# RAG相关依赖
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import faiss
    import markdown
    from bs4 import BeautifulSoup
    import openai
    from openai import OpenAI
except ImportError as e:
    print(f"错误: 缺少必要的依赖 - {e}")
    print("请安装: pip install numpy sentence-transformers faiss-cpu beautifulsoup4 openai markdown")
    sys.exit(1)

class HugoRAGEngine:
    """Hugo博客RAG引擎"""

    def __init__(self,
                 content_dir: str = "content",
                 index_dir: str = "rag-index",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 openai_api_key: Optional[str] = None,
                 max_docs: int = 100):  # 限制最大文档数量
        self.content_dir = Path(content_dir)
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # 模型和API配置
        self.embedding_model_name = embedding_model
        self.embedding_model = None
        self.openai_client = None

        if openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
        else:
            # 尝试从环境变量获取
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)

        # 索引文件路径
        self.index_file = self.index_dir / "faiss_index.idx"
        self.metadata_file = self.index_dir / "metadata.pkl"
        self.content_file = self.index_dir / "content.pkl"

        # 索引数据
        self.index = None
        self.metadata = []
        self.content_chunks = []

        # 配置
        self.chunk_size = 800  # 文本块大小 (减少以节省内存)
        self.chunk_overlap = 150  # 块重叠大小 (减少重叠)
        self.max_docs = max_docs  # 最大文档数量限制

    def load_embedding_model(self):
        """加载嵌入模型"""
        if self.embedding_model is None:
            print("🔄 加载嵌入模型...")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            print("✅ 嵌入模型加载完成")

    def extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """提取Hugo frontmatter"""
        frontmatter = {}
        lines = content.split('\n')

        if not lines[0].strip() == '---':
            return frontmatter

        end_idx = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_idx = i
                break

        if end_idx == -1:
            return frontmatter

        try:
            frontmatter_text = '\n'.join(lines[1:end_idx])
            # 简单YAML解析
            for line in frontmatter_text.split('\n'):
                line = line.strip()
                if ':' in line and not line.startswith('#'):
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    frontmatter[key] = value
        except:
            pass

        return frontmatter

    def clean_markdown(self, text: str) -> str:
        """清理Markdown标记"""
        # 移除frontmatter
        lines = text.split('\n')
        if lines and lines[0].strip() == '---':
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    text = '\n'.join(lines[i+1:])
                    break

        # 转换为HTML然后提取纯文本
        html = markdown.markdown(text)
        soup = BeautifulSoup(html, 'html.parser')

        # 移除代码块
        for code in soup.find_all(['code', 'pre']):
            code.decompose()

        # 移除链接但保留文本
        for a in soup.find_all('a'):
            a.replace_with(a.get_text())

        # 移除图片
        for img in soup.find_all('img'):
            img.decompose()

        return soup.get_text()

    def split_text(self, text: str) -> List[str]:
        """将文本分割成块"""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # 尝试在句子边界结束
            if end < len(text):
                # 查找最近的句子结束符
                for punct in ['. ', '! ', '? ', '\n\n']:
                    last_punct = text.rfind(punct, start, end)
                    if last_punct != -1:
                        end = last_punct + len(punct)
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # 移动到下一个位置，考虑重叠
            start = end - self.chunk_overlap

        return chunks

    def process_markdown_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """处理单个Markdown文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            frontmatter = self.extract_frontmatter(content)
            clean_text = self.clean_markdown(content)

            if not clean_text.strip():
                return []

            # 分割文本
            chunks = self.split_text(clean_text)

            # 为每个块创建元数据
            documents = []
            for i, chunk in enumerate(chunks):
                doc = {
                    'file_path': str(file_path.relative_to(self.content_dir)),
                    'chunk_id': i,
                    'title': frontmatter.get('title', file_path.stem),
                    'date': frontmatter.get('date', ''),
                    'tags': frontmatter.get('tags', []),
                    'categories': frontmatter.get('categories', []),
                    'content': chunk,
                    'url': self.generate_url(file_path, frontmatter),
                    'hash': hashlib.md5(chunk.encode()).hexdigest()[:8]
                }
                documents.append(doc)

            return documents

        except Exception as e:
            print(f"⚠️  处理文件失败 {file_path}: {e}")
            return []

    def generate_url(self, file_path: Path, frontmatter: Dict) -> str:
        """生成文章URL"""
        rel_path = file_path.relative_to(self.content_dir)
        url_path = str(rel_path).replace('.md', '/').replace('\\', '/')

        # 移除多余的路径前缀
        if url_path.startswith('./'):
            url_path = url_path[2:]

        return f"/{url_path}"

    def build_index(self, force_rebuild: bool = False):
        """构建向量索引"""
        print("🏗️  构建向量索引...")

        self.load_embedding_model()

        # 检查是否需要重建
        if self.index_file.exists() and not force_rebuild:
            print("📂 发现现有索引，使用 --rebuild-index 强制重建")
            self.load_index()
            return

        all_documents = []

        # 处理所有Markdown文件
        md_files = list(self.content_dir.rglob('*.md'))
        print(f"📚 发现 {len(md_files)} 个Markdown文件")

        for i, md_file in enumerate(md_files):
            if md_file.name.startswith('_'):  # 跳过特殊文件
                continue

            if len(all_documents) >= self.max_docs:
                print(f"⚠️  已达到最大文档数量限制 ({self.max_docs})，停止处理")
                break

            print(f"📄 处理: {md_file.name} ({i+1}/{len(md_files)})")
            documents = self.process_markdown_file(md_file)
            all_documents.extend(documents)

            # 显示进度
            if (i + 1) % 10 == 0:
                print(f"📊 已处理 {len(all_documents)} 个文档块...")

        if not all_documents:
            print("⚠️  没有找到有效文档")
            return

        print(f"📊 处理了 {len(all_documents)} 个文档块")

        # 生成嵌入向量 (分批处理以减少内存使用)
        print("🧮 生成嵌入向量...")
        texts = [doc['content'] for doc in all_documents]
        batch_size = 32  # 批处理大小
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            print(f"处理批次 {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size} ({len(batch_texts)} 个文档)")
            batch_embeddings = self.embedding_model.encode(batch_texts, show_progress_bar=False)
            embeddings.append(batch_embeddings)

        embeddings = np.vstack(embeddings)

        # 构建FAISS索引
        print("🔍 构建FAISS索引...")
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # 内积索引
        faiss.normalize_L2(embeddings)  # L2归一化
        self.index.add(embeddings)

        # 保存索引和元数据
        self.metadata = all_documents
        self.content_chunks = texts

        self.save_index()
        print("✅ 索引构建完成")
        print(f"📈 索引统计: {len(all_documents)} 个文档块，维度: {dimension}")

    def save_index(self):
        """保存索引到磁盘"""
        print("💾 保存索引...")

        # 保存FAISS索引
        faiss.write_index(self.index, str(self.index_file))

        # 保存元数据
        with open(self.metadata_file, 'wb') as f:
            pickle.dump(self.metadata, f)

        # 保存内容块
        with open(self.content_file, 'wb') as f:
            pickle.dump(self.content_chunks, f)

    def load_index(self):
        """从磁盘加载索引"""
        print("📂 加载现有索引...")

        if not self.index_file.exists():
            print("⚠️  索引文件不存在")
            return

        try:
            # 加载FAISS索引
            self.index = faiss.read_index(str(self.index_file))

            # 加载元数据
            with open(self.metadata_file, 'rb') as f:
                self.metadata = pickle.load(f)

            # 加载内容块
            with open(self.content_file, 'rb') as f:
                self.content_chunks = pickle.load(f)

            print(f"✅ 索引加载完成: {len(self.metadata)} 个文档块")

        except Exception as e:
            print(f"❌ 加载索引失败: {e}")
            self.index = None
            self.metadata = []
            self.content_chunks = []

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索相关文档"""
        if self.index is None:
            self.load_index()

        if self.index is None:
            print("❌ 索引未加载")
            return []

        self.load_embedding_model()

        # 生成查询向量
        query_embedding = self.embedding_model.encode([query])[0]
        query_embedding = query_embedding / np.linalg.norm(query_embedding)  # 归一化

        # 搜索最相似的文档
        query_embedding = query_embedding.reshape(1, -1)
        scores, indices = self.index.search(query_embedding, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['score'] = float(score)
                results.append(result)

        return results

    def generate_answer(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """基于检索结果生成回答"""
        if not self.openai_client:
            # 如果没有OpenAI API，使用简单的模板回答
            return self.generate_simple_answer(query, context_docs)

        try:
            # 构建上下文
            context = "\n\n".join([
                f"标题: {doc['title']}\n内容: {doc['content'][:500]}..."
                for doc in context_docs[:3]  # 只使用前3个最相关的文档
            ])

            prompt = f"""基于以下博客文章内容，回答用户的问题。请提供准确、有帮助的回答，并引用相关信息来源。

问题: {query}

相关文章内容:
{context}

请用中文回答，并保持简洁明了。"""

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的博客助手，基于提供的文章内容回答问题。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"❌ 生成回答失败: {e}")
            return self.generate_simple_answer(query, context_docs)

    def generate_simple_answer(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """生成简单的回答（不使用AI）"""
        if not context_docs:
            return "抱歉，我没有找到相关信息。"

        # 找到最相关的文档
        best_doc = context_docs[0]

        answer = f"根据《{best_doc['title']}》中的内容：\n\n"
        answer += best_doc['content'][:300]
        if len(best_doc['content']) > 300:
            answer += "..."

        if best_doc['url']:
            answer += f"\n\n查看完整文章: {best_doc['url']}"

        return answer

    def query(self, query_text: str, top_k: int = 5) -> Dict[str, Any]:
        """执行完整查询流程"""
        print(f"🔍 查询: {query_text}")

        # 搜索相关文档
        relevant_docs = self.search(query_text, top_k)

        if not relevant_docs:
            return {
                'query': query_text,
                'answer': "抱歉，我没有找到相关信息。",
                'sources': []
            }

        # 生成回答
        answer = self.generate_answer(query_text, relevant_docs)

        # 构建结果
        sources = []
        for doc in relevant_docs[:3]:  # 只返回前3个来源
            sources.append({
                'title': doc['title'],
                'url': doc['url'],
                'score': doc['score'],
                'snippet': doc['content'][:200] + "..."
            })

        return {
            'query': query_text,
            'answer': answer,
            'sources': sources,
            'timestamp': datetime.now().isoformat()
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        if self.index is None:
            self.load_index()

        stats = {
            'total_documents': len(self.metadata) if self.metadata else 0,
            'index_size': self.index.ntotal if self.index else 0,
            'dimension': self.index.d if self.index else 0,
            'last_updated': None,
            'content_stats': {}
        }

        if self.metadata:
            # 统计内容信息
            total_words = sum(len(doc['content'].split()) for doc in self.metadata)
            stats['content_stats'] = {
                'total_words': total_words,
                'avg_chunk_size': total_words / len(self.metadata),
                'unique_files': len(set(doc['file_path'] for doc in self.metadata))
            }

            # 检查最后更新时间
            if self.index_file.exists():
                stats['last_updated'] = datetime.fromtimestamp(
                    self.index_file.stat().st_mtime
                ).isoformat()

        return stats

def main():
    parser = argparse.ArgumentParser(
        description="Hugo博客RAG聊天机器人引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--content-dir',
        default='content',
        help='内容目录 (默认: content)'
    )

    parser.add_argument(
        '--index-dir',
        default='rag-index',
        help='索引目录 (默认: rag-index)'
    )

    parser.add_argument(
        '--rebuild-index',
        action='store_true',
        help='重建向量索引'
    )

    parser.add_argument(
        '--update-index',
        action='store_true',
        help='更新现有索引'
    )

    parser.add_argument(
        '--query',
        help='执行查询'
    )

    parser.add_argument(
        '--serve',
        action='store_true',
        help='启动Web服务'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='显示索引统计信息'
    )

    parser.add_argument(
        '--openai-api-key',
        help='OpenAI API密钥'
    )

    parser.add_argument(
        '--embedding-model',
        default='all-MiniLM-L6-v2',
        help='嵌入模型名称 (默认: all-MiniLM-L6-v2)'
    )

    parser.add_argument(
        '--max-docs',
        type=int,
        default=50,
        help='最大文档数量限制 (默认: 50)'
    )

    args = parser.parse_args()

    # 初始化RAG引擎
    engine = HugoRAGEngine(
        content_dir=args.content_dir,
        index_dir=args.index_dir,
        embedding_model=args.embedding_model,
        openai_api_key=args.openai_api_key,
        max_docs=args.max_docs
    )

    try:
        if args.rebuild_index:
            # 重建索引
            engine.build_index(force_rebuild=True)

        elif args.update_index:
            # 更新索引
            engine.build_index(force_rebuild=False)

        elif args.query:
            # 执行查询
            if not engine.index:
                engine.load_index()

            result = engine.query(args.query)
            print("\n" + "="*50)
            print("🤖 回答:")
            print(result['answer'])
            print("\n📚 相关来源:")
            for i, source in enumerate(result['sources'], 1):
                print(f"{i}. {source['title']} (相关度: {source['score']:.3f})")
                print(f"   {source['url']}")
            print("="*50)

        elif args.stats:
            # 显示统计信息
            stats = engine.get_stats()
            print("📊 RAG索引统计信息:")
            print(f"- 文档块数量: {stats['total_documents']}")
            print(f"- 向量维度: {stats['dimension']}")
            print(f"- 总词数: {stats.get('content_stats', {}).get('total_words', 0)}")
            print(f"- 唯一文件数: {stats.get('content_stats', {}).get('unique_files', 0)}")
            if stats['last_updated']:
                print(f"- 最后更新: {stats['last_updated']}")

        elif args.serve:
            # 启动Web服务
            print("🚀 启动RAG聊天服务...")
            print("功能待实现，请使用 --query 参数进行测试")

        else:
            # 默认操作：检查索引状态
            if engine.index_file.exists():
                print("✅ RAG索引已存在")
                engine.get_stats()
            else:
                print("❌ RAG索引不存在，请运行 --rebuild-index 构建索引")

    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
