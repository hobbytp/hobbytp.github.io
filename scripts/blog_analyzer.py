#!/usr/bin/env python3
"""
博客内容分析器
分析博客文件，提取标题、分类、标签、摘要等信息
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, Optional, Tuple


class BlogAnalyzer:
    def __init__(self, content_dir: str = "content"):
        self.content_dir = content_dir
        
    def extract_frontmatter(self, file_path: str) -> Dict:
        """提取博客文件的frontmatter信息"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 查找frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter_text = parts[1]
                    return yaml.safe_load(frontmatter_text) or {}
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            
        return {}
    
    def extract_category_from_path(self, file_path: str) -> str:
        """从文件路径提取分类"""
        path_parts = Path(file_path).parts
        
        # 查找content/zh/后的第一个目录
        if 'content' in path_parts and 'zh' in path_parts:
            zh_index = path_parts.index('zh')
            if zh_index + 1 < len(path_parts):
                return path_parts[zh_index + 1]
        
        return "general"
    
    def extract_summary(self, file_path: str, max_length: int = 200) -> str:
        """提取博客摘要（前几段内容）"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 移除frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    content = parts[2]
            
            # 提取前几段内容
            lines = content.split('\n')
            summary_lines = []
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('*'):
                    summary_lines.append(line)
                    if len(' '.join(summary_lines)) > max_length:
                        break
                        
            summary = ' '.join(summary_lines)
            return summary[:max_length] + "..." if len(summary) > max_length else summary
            
        except Exception as e:
            print(f"Error extracting summary from {file_path}: {e}")
            return ""
    
    def analyze_blog(self, file_path: str) -> Dict:
        """分析博客文件，返回完整信息"""
        frontmatter = self.extract_frontmatter(file_path)
        
        # 提取基本信息
        title = frontmatter.get('title', '')
        tags = frontmatter.get('tags', [])
        categories = frontmatter.get('categories', [])
        
        # 从路径提取分类
        path_category = self.extract_category_from_path(file_path)
        
        # 合并分类
        all_categories = list(set(categories + [path_category]))
        
        # 提取摘要
        summary = self.extract_summary(file_path)
        
        # 生成图片文件名
        filename = Path(file_path).stem
        image_filename = f"{path_category}-{filename}.png"
        
        return {
            'file_path': file_path,
            'title': title,
            'tags': tags,
            'categories': all_categories,
            'primary_category': path_category,
            'summary': summary,
            'image_filename': image_filename,
            'image_path': f"static/images/articles/{image_filename}"
        }
    
    def get_all_blogs(self) -> list:
        """获取所有博客文件"""
        blogs = []
        content_path = Path(self.content_dir)
        
        for md_file in content_path.rglob("*.md"):
            # 跳过_index.md文件
            if md_file.name == "_index.md":
                continue
                
            blogs.append(str(md_file))
            
        return blogs
    
    def find_blogs_without_images(self, output_dir: str = "static/images/articles") -> list:
        """查找没有对应图片的博客"""
        blogs_without_images = []
        all_blogs = self.get_all_blogs()
        
        for blog_path in all_blogs:
            blog_info = self.analyze_blog(blog_path)
            image_path = blog_info['image_path']
            
            if not os.path.exists(image_path):
                blogs_without_images.append(blog_info)
                
        return blogs_without_images


if __name__ == "__main__":
    analyzer = BlogAnalyzer()
    
    # 测试分析一个博客文件
    test_file = "content/zh/projects/langGraph.md"
    if os.path.exists(test_file):
        result = analyzer.analyze_blog(test_file)
        print("Blog analysis result:")
        print(yaml.dump(result, default_flow_style=False, allow_unicode=True))
    
    # 查找没有图片的博客
    blogs_without_images = analyzer.find_blogs_without_images()
    print(f"\nFound {len(blogs_without_images)} blogs without images")


