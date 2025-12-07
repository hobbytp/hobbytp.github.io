
import unittest
import shutil
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import sys

# 添加 scripts 目录到路径以便导入 ingest
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingest import BlogIngester

class TestIncrementalIngest(unittest.TestCase):
    def setUp(self):
        # 创建临时目录结构
        self.test_dir = tempfile.mkdtemp()
        self.content_dir = Path(self.test_dir) / "content"
        self.content_dir.mkdir()
        
        # 创建一个测试用的 markdown 文件
        self.test_file = self.content_dir / "test_post.md"
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("---\ntitle: Test Post\n---\nThis is a test content.")
            
        # 状态文件路径
        self.state_file = Path(self.test_dir) / ".ingest_state.json"
        # 设置必要的环境变量，避免初始化失败
        os.environ['CLOUDFLARE_ACCOUNT_ID'] = 'test_account_12345678'
        os.environ['CLOUDFLARE_API_TOKEN'] = 'test_token_abcdef0123456789'

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch("ingest.requests.post")
    def test_incremental_ingestion(self, mock_post):
        """测试增量摄取：第二次运行不应处理未修改的文件"""
        
        # 模拟 Cloudflare API 响应 (Direct data format as expected by ingest.py)
        mock_response = MagicMock()
        mock_response.status_code = 200
        # ingest.py expects 'data' at the root of the response json for vectors
        mock_response.json.return_value = {"data": [[0.1, 0.2, 0.3]]} 
        mock_post.return_value = mock_response

        # 初始化 Ingester (传入 state_file 路径)
        # 注意：我们需要修改 ingest.py 里的 __init__ 来接受 state_file 参数
        # 这里假设我们将修改代码以支持 state_file 参数，或者通过 kwargs 传递
        ingester = BlogIngester(
            content_dir=str(self.content_dir),
            base_url="http://localhost"
        )
        # 临时注入 state_file 属性 (我们稍后会在代码中正式添加)
        ingester.state_file = self.state_file

        # --- 第一次运行 ---
        print("\nRunning 1st ingestion...")
        stats1 = ingester.ingest_all()
        
        # 验证第一次应该处理了文件
        self.assertEqual(stats1['processed_files'], 1)
        self.assertTrue(self.state_file.exists(), "State file should be created")
        
        # 检查 API 调用次数 (Embedding + Upload)
        # 1 file -> 1 chunk -> 1 embedding call + 1 upload call = 2 calls
        # 或者是根据 chunk 数量。这里文件很短，只有 1 个 chunk。
        # 让我们主要验证 processed_files 计数，这更直接。

        # --- 第二次运行 (文件未修改) ---
        print("Running 2nd ingestion (unchanged)...")
        stats2 = ingester.ingest_all()
        
        # 验证第二次应该跳过文件
        self.assertEqual(stats2['processed_files'], 0, "Should skip unchanged file")
        self.assertEqual(stats2['skipped_files'], 1, "Should count as skipped")

        # --- 第三次运行 (修改文件) ---
        print("Running 3rd ingestion (modified)...")
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("---\ntitle: Test Post Modified\n---\nNew content here.")
            
        stats3 = ingester.ingest_all()
        self.assertEqual(stats3['processed_files'], 1, "Should process modified file")

    @patch("ingest.requests.post")
    def test_cf_nested_result_parsing_and_chunk_count(self, mock_post):
        """Cloudflare响应嵌套在result中时应正确解析，且chunk计数>0"""
        # 模拟 Cloudflare AI 响应：嵌套在 result 中且返回两个向量
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "data": [[0.1]*768, [0.2]*768],
                "shape": [2, 768],
                "pooling": "mean",
                "usage": {"prompt_tokens": 100, "completion_tokens": 0, "total_tokens": 100}
            },
            "success": True,
            "errors": [],
            "messages": []
        }
        mock_post.return_value = mock_response

        # 创建较长内容以产生多个chunk
        long_text = "---\ntitle: Long Post\n---\n" + ("段落。" * 120)  # 足够长
        test_file = self.content_dir / "long_post.md"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(long_text)

        ingester = BlogIngester(
            content_dir=str(self.content_dir),
            base_url="http://localhost"
        )
        # 为测试缩小chunk大小并去掉重叠，确保产生多个chunk
        ingester.CHUNK_SIZE = 50
        ingester.CHUNK_OVERLAP = 0

        # 动态计算chunk数量，并将mock返回的向量数量与chunk数量对齐
        meta = ingester.extract_frontmatter(test_file)
        clean_text = ingester.clean_markdown(meta.get('content', ''))
        chunks = ingester.chunk_text(clean_text)
        n = len(chunks)
        mock_response.json.return_value = {
            "result": {
                "data": [[0.1]*768 for _ in range(n)],
                "shape": [n, 768],
                "pooling": "mean",
                "usage": {"prompt_tokens": 100, "completion_tokens": 0, "total_tokens": 100}
            },
            "success": True,
            "errors": [],
            "messages": []
        }
        mock_post.return_value = mock_response

        # 处理单文件，期望返回>0的chunks计数，且与chunk数量一致
        count = ingester.process_file(test_file)
        self.assertGreater(count, 0, "Processed chunk count should be > 0")
        self.assertEqual(count, n, "Chunk count should equal returned vectors")

    @patch("ingest.requests.post")
    def test_category_metadata_extraction_from_path_and_front_matter(self, mock_post):
        """
        验证metadata.category:
        - 无前言时：从路径 content/<lang>/<category>/... 解析
        - 有前言时：优先使用 front matter 中的 category
        并拦截上传以检查向量载荷中的 metadata。
        """
        # 构造 Cloudflare 嵌入响应的mock：我们会按chunk数量动态设置data长度
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # 构造目录：content/zh/celebrity_insights/
        base_dir = self.content_dir / "zh" / "celebrity_insights"
        base_dir.mkdir(parents=True, exist_ok=True)

        # 文件1：无front matter -> 使用路径中的类别
        f1 = base_dir / "no_front_matter.md"
        f1.write_text("段落。" * 120, encoding="utf-8")

        # 文件2：有front matter -> 使用front matter中的category
        f2 = base_dir / "with_front_matter.md"
        f2.write_text(
            """---
title: FM Test
category: fmcat
---
这里是有前言的文本内容，用于测试category解析。""" * 60,
            encoding="utf-8",
        )

        ingester = BlogIngester(
            content_dir=str(self.content_dir),
            base_url="http://localhost"
        )
        ingester.CHUNK_SIZE = 50
        ingester.CHUNK_OVERLAP = 0

        captured = {}

        def fake_upload(vectors):
            captured["vectors"] = vectors
            return True

        ingester.upload_to_vectorize = fake_upload

        # 处理f1：动态设置嵌入数量与chunk数量一致
        meta1 = ingester.extract_frontmatter(f1)
        clean1 = ingester.clean_markdown(meta1.get('content', ''))
        chunks1 = ingester.chunk_text(clean1)
        n1 = len(chunks1)
        mock_response.json.return_value = {
            "result": {
                "data": [[0.1] * 768 for _ in range(n1)],
                "shape": [n1, 768],
                "pooling": "mean",
                "usage": {"prompt_tokens": 10, "completion_tokens": 0, "total_tokens": 10}
            },
            "success": True,
            "errors": [],
            "messages": []
        }
        mock_post.return_value = mock_response

        cnt1 = ingester.process_file(f1)
        self.assertEqual(cnt1, n1)
        vectors1 = captured.get("vectors", [])
        self.assertTrue(len(vectors1) > 0)
        self.assertTrue(all(v.get("metadata", {}).get("category") == "celebrity_insights" for v in vectors1))

        # 处理f2：动态设置嵌入数量与chunk数量一致
        meta2 = ingester.extract_frontmatter(f2)
        clean2 = ingester.clean_markdown(meta2.get('content', ''))
        chunks2 = ingester.chunk_text(clean2)
        n2 = len(chunks2)
        mock_response.json.return_value = {
            "result": {
                "data": [[0.1] * 768 for _ in range(n2)],
                "shape": [n2, 768],
                "pooling": "mean",
                "usage": {"prompt_tokens": 10, "completion_tokens": 0, "total_tokens": 10}
            },
            "success": True,
            "errors": [],
            "messages": []
        }
        mock_post.return_value = mock_response

        cnt2 = ingester.process_file(f2)
        self.assertEqual(cnt2, n2)
        vectors2 = captured.get("vectors", [])
        self.assertTrue(len(vectors2) > 0)
        self.assertTrue(all(v.get("metadata", {}).get("category") == "fmcat" for v in vectors2))

if __name__ == '__main__':
    unittest.main()
