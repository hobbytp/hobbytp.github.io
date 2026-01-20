
import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
from pathlib import Path
import os

# 将 scripts 目录添加到 sys.path 以便导入脚本
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.append(str(SCRIPTS_DIR))

class TestGeneratePaperBlog(unittest.TestCase):

    @patch("shutil.move")
    @patch("generate_paper_blog.Image")
    @patch("pathlib.Path.exists", autospec=True)
    @patch("pathlib.Path.write_text")
    @patch("builtins.open", new_callable=mock_open, read_data="Question 1,Answer 1\nQuestion 2,Answer 2")
    def test_generate_blog_workflow(self, mock_file, mock_write, mock_exists, mock_image, mock_move):
        import generate_paper_blog as script

        # Mock 路径存在检查
        def side_effect(*args, **kwargs):
            # 模拟文件系统状态
            if not args:
                return True
            path_str = str(args[0])
            # 源文件在 tmp 目录下存在
            if "tmp" in path_str and ("TestFile.png" in path_str or "TestFile.csv" in path_str or "TestFile.pdf" in path_str or "TestFile.xls" in path_str):
                return True
            
            # 目标 WebP 不存在，需要生成
            if path_str.endswith(".webp"):
                return False 
            
            # 其他目录默认存在
            return True
        
        mock_exists.side_effect = side_effect

        # Mock Image.open and save
        mock_img_instance = MagicMock()
        mock_image.open.return_value.__enter__.return_value = mock_img_instance
        
        # 执行主函数
        # 假设脚本支持可选参数 output_dir，默认 papers
        script.generate_paper_blog("TestFile")

        # 验证图片转换
        # 保存路径应该是 optimized/png/TestFile.webp
        args, kwargs = mock_img_instance.save.call_args
        self.assertIn("optimized", str(args[0]))
        self.assertTrue(str(args[0]).endswith("TestFile.webp"))
        self.assertEqual(args[1], "WebP")
        
        # 验证文件移动
        # 应该有3次移动：PNG, PDF, CSV/XLS
        self.assertEqual(mock_move.call_count, 3)
        
        # 验证 Markdown 写入
        self.assertTrue(mock_write.called)
        content = mock_write.call_args[0][0]
        
        # 验证内容关键部分 - 图片路径应指向 optimized
        self.assertIn('title: "TestFile"', content)
        self.assertIn('![TestFile示意图](/images/optimized/png/TestFile.webp)', content)
        self.assertIn('{{< pdf src="/pdf/TestFile.pdf" >}}', content)
        self.assertIn('{{< flashcards >}}', content)

if __name__ == "__main__":
    unittest.main()
