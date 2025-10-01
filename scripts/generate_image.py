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
import google.generativeai as genai
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
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
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
        """生成图片，带重试机制"""
        for attempt in range(max_retries):
            try:
                print(f"Generating image (attempt {attempt + 1}/{max_retries})...")
                
                # 调用Gemini API生成图片
                response = self.model.generate_content(prompt)
                
                # 检查响应
                if hasattr(response, 'parts') and response.parts:
                    # Gemini API返回的是文本描述，我们需要使用其他方法生成图片
                    # 这里我们使用一个简化的方法：生成一个描述文件
                    description = response.text if hasattr(response, 'text') else str(response)
                    
                    # 创建一个临时的描述文件，实际项目中可能需要调用其他图片生成API
                    temp_desc_file = f"temp_description_{int(time.time())}.txt"
                    with open(temp_desc_file, 'w', encoding='utf-8') as f:
                        f.write(f"Image description: {description}\n")
                        f.write(f"Prompt: {prompt}\n")
                    
                    return temp_desc_file
                else:
                    print(f"Unexpected response format: {response}")
                    return None
                    
            except Exception as e:
                print(f"Error generating image (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(30)  # 等待30秒后重试
                else:
                    return None
        
        return None
    
    def create_placeholder_image(self, blog_info: Dict, desc_file: str) -> bool:
        """创建占位符图片（实际项目中应该调用真正的图片生成API）"""
        try:
            # 读取描述文件
            with open(desc_file, 'r', encoding='utf-8') as f:
                description = f.read()
            
            # 创建一个简单的占位符图片
            from PIL import Image, ImageDraw, ImageFont
            
            # 创建图片
            img = Image.new('RGB', (1200, 630), color='#1e3a8a')  # 深蓝色背景
            draw = ImageDraw.Draw(img)
            
            # 添加渐变效果
            for y in range(630):
                color_value = int(30 + (y / 630) * 100)  # 从深蓝到浅蓝
                color = (color_value, color_value + 50, color_value + 100)
                draw.line([(0, y), (1200, y)], fill=color)
            
            # 添加几何图案
            # 画一些圆形
            for i in range(5):
                x = 200 + i * 200
                y = 315
                radius = 50 + i * 10
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                           outline='white', width=3)
            
            # 添加标题（简化版）
            try:
                # 尝试使用系统字体
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
            except:
                # 使用默认字体
                font = ImageFont.load_default()
            
            title = blog_info.get('title', 'Blog Post')[:30]  # 限制长度
            draw.text((100, 100), title, fill='white', font=font)
            
            # 添加分类标签
            category = blog_info.get('primary_category', 'general')
            draw.text((100, 500), f"Category: {category}", fill='lightblue', font=font)
            
            # 保存图片
            success = self.processor.process_image_from_pil(img, blog_info['image_path'])
            return success
            
        except Exception as e:
            print(f"Error creating placeholder image: {e}")
            return False
    
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
            
            # 生成图片描述
            desc_file = self.generate_image_with_retry(prompt)
            if not desc_file:
                print(f"Failed to generate image description for {blog_path}")
                return False
            
            # 创建一个占位符图片（实际项目中这里应该调用真正的图片生成API）
            success = self.create_placeholder_image(blog_info, desc_file)
            
            # 清理临时文件
            if os.path.exists(desc_file):
                os.remove(desc_file)
            
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
