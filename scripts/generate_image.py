#!/usr/bin/env python3
"""
图片生成主脚本
使用Gemini API生成博客图片
"""

import os
import sys
import yaml
import time
import json
from pathlib import Path
from typing import Dict, Optional
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from blog_analyzer import BlogAnalyzer
from image_processor import ImageProcessor


class ImageGenerator:
    def __init__(self, config_path: str = "config/image_config.yml"):
        self.config = self.load_config(config_path)
        self.analyzer = BlogAnalyzer()
        self.processor = ImageProcessor()
        
        # 初始化Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        self.client = genai.Client(api_key=api_key)
        
    def load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def generate_prompt(self, blog_info: Dict) -> str:
        """根据博客信息生成提示词"""
        template = self.config.get('prompt_template', '')
        
        # 获取分类风格
        category = blog_info.get('primary_category', 'general')
        category_styles = self.config.get('category_styles', {})
        style_description = category_styles.get(category, "Tech elements, modern design")
        
        # 替换模板变量
        prompt = template.format(
            title=blog_info.get('title', ''),
            category=category,
            tags=', '.join(blog_info.get('tags', [])),
            summary=blog_info.get('summary', '')
        )
        
        # 添加分类特定的风格描述
        prompt += f"\n\nAdditional style elements for {category} category: {style_description}"
        
        return prompt
    
    def generate_image_with_retry(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """使用Gemini API生成图片，带重试机制"""
        for attempt in range(max_retries):
            try:
                print(f"Generating image with Gemini API (attempt {attempt + 1}/{max_retries})...")
                
                # 调用Gemini API生成图片
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash-image-preview",
                    contents=[prompt],
                )
                
                # 检查响应并提取图片数据
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                # 找到图片数据
                                image_data = part.inline_data.data
                                
                                # 保存为临时文件
                                temp_image_file = f"temp_generated_{int(time.time())}.png"
                                with open(temp_image_file, 'wb') as f:
                                    f.write(image_data)
                                
                                print(f"Successfully generated image: {temp_image_file}")
                                return temp_image_file
                            elif hasattr(part, 'text') and part.text:
                                # 如果返回的是文本描述，记录日志
                                print(f"Received text response: {part.text[:200]}...")
                
                print(f"No image data found in response")
                return None
                    
            except Exception as e:
                print(f"Error generating image (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(30)  # 等待30秒后重试
                else:
                    return None
        
        return None
    
    
    def generate_blog_image(self, blog_path: str) -> bool:
        """为单个博客生成图片"""
        try:
            # 分析博客内容
            blog_info = self.analyzer.analyze_blog(blog_path)
            print(f"Analyzing blog: {blog_info['title']}")
            
            # 检查图片是否已存在
            if os.path.exists(blog_info['image_path']):
                print(f"Image already exists: {blog_info['image_path']}")
                return True
            
            # 生成提示词
            prompt = self.generate_prompt(blog_info)
            print(f"Generated prompt: {prompt[:200]}...")
            
            # 使用Gemini API生成图片
            temp_image_file = self.generate_image_with_retry(prompt)
            if not temp_image_file:
                print(f"Failed to generate image for {blog_path}")
                return False
            
            # 处理生成的图片
            success = self.processor.process_image(temp_image_file, blog_info['image_path'])
            
            # 清理临时文件
            if os.path.exists(temp_image_file):
                os.remove(temp_image_file)
            
            if success:
                print(f"Successfully generated image: {blog_info['image_path']}")
                return True
            else:
                print(f"Failed to process image for {blog_path}")
                return False
                
        except Exception as e:
            print(f"Error generating image for {blog_path}: {e}")
            return False
    
    def generate_images_for_blogs(self, blog_paths: list) -> Dict:
        """为多个博客生成图片"""
        results = {
            'success': [],
            'failed': [],
            'skipped': []
        }
        
        for blog_path in blog_paths:
            print(f"\nProcessing: {blog_path}")
            
            if self.generate_blog_image(blog_path):
                results['success'].append(blog_path)
            else:
                results['failed'].append(blog_path)
        
        return results
    
    def get_rate_limit_status(self) -> Dict:
        """检查速率限制状态"""
        # 这里可以实现更复杂的速率限制逻辑
        # 目前返回简单的状态
        return {
            'daily_processed': 0,
            'hourly_processed': 0,
            'can_process': True
        }


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python generate_image.py <blog_path> [blog_path2] ...")
        print("   or: python generate_image.py --backfill")
        sys.exit(1)
    
    generator = ImageGenerator()
    
    if sys.argv[1] == '--backfill':
        # 历史博客补图模式
        print("Starting backfill mode...")
        
        # 检查速率限制
        rate_status = generator.get_rate_limit_status()
        if not rate_status['can_process']:
            print("Rate limit reached, skipping backfill")
            sys.exit(0)
        
        # 查找没有图片的博客
        blogs_without_images = generator.analyzer.find_blogs_without_images()
        
        # 限制处理数量
        daily_limit = generator.config.get('rate_limits', {}).get('daily_limit', 5)
        blogs_to_process = blogs_without_images[:daily_limit]
        
        print(f"Found {len(blogs_without_images)} blogs without images")
        print(f"Processing {len(blogs_to_process)} blogs (daily limit: {daily_limit})")
        
        # 处理博客
        blog_paths = [blog['file_path'] for blog in blogs_to_process]
        results = generator.generate_images_for_blogs(blog_paths)
        
    else:
        # 处理指定的博客文件
        blog_paths = sys.argv[1:]
        results = generator.generate_images_for_blogs(blog_paths)
    
    # 输出结果
    print(f"\nResults:")
    print(f"Success: {len(results['success'])}")
    print(f"Failed: {len(results['failed'])}")
    print(f"Skipped: {len(results['skipped'])}")
    
    if results['failed']:
        print(f"Failed files: {results['failed']}")


if __name__ == "__main__":
    main()
