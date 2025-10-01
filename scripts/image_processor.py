#!/usr/bin/env python3
"""
图片处理工具
处理生成的图片，调整尺寸、优化格式等
"""

import os
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional


class ImageProcessor:
    def __init__(self, target_size: Tuple[int, int] = (1200, 630)):
        self.target_size = target_size
        
    def resize_image(self, input_path: str, output_path: str) -> bool:
        """调整图片尺寸到目标大小"""
        try:
            with Image.open(input_path) as img:
                # 保持宽高比，裁剪到目标尺寸
                img_resized = img.resize(self.target_size, Image.Resampling.LANCZOS)
                img_resized.save(output_path, 'PNG', optimize=True)
                return True
        except Exception as e:
            print(f"Error resizing image {input_path}: {e}")
            return False
    
    def optimize_image(self, image_path: str) -> bool:
        """优化图片文件大小"""
        try:
            with Image.open(image_path) as img:
                # 转换为RGB模式（如果需要）
                if img.mode in ('RGBA', 'LA'):
                    # 创建白色背景
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    img = background
                
                # 保存优化后的图片
                img.save(image_path, 'PNG', optimize=True, quality=95)
                return True
        except Exception as e:
            print(f"Error optimizing image {image_path}: {e}")
            return False
    
    def ensure_output_dir(self, output_path: str) -> bool:
        """确保输出目录存在"""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating output directory {output_path}: {e}")
            return False
    
    def process_image(self, input_path: str, output_path: str) -> bool:
        """完整的图片处理流程"""
        try:
            # 确保输出目录存在
            if not self.ensure_output_dir(output_path):
                return False
            
            # 调整尺寸
            if not self.resize_image(input_path, output_path):
                return False
            
            # 优化图片
            if not self.optimize_image(output_path):
                return False
            
            print(f"Successfully processed image: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error processing image {input_path}: {e}")
            return False
    
    def process_image_from_pil(self, pil_image: Image.Image, output_path: str) -> bool:
        """处理PIL图片对象"""
        try:
            # 确保输出目录存在
            if not self.ensure_output_dir(output_path):
                return False
            
            # 调整尺寸
            resized_image = pil_image.resize(self.target_size, Image.Resampling.LANCZOS)
            
            # 保存图片
            resized_image.save(output_path, 'PNG', optimize=True, quality=95)
            
            print(f"Successfully processed PIL image: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error processing PIL image: {e}")
            return False


if __name__ == "__main__":
    processor = ImageProcessor()
    
    # 测试图片处理
    test_input = "test_input.png"
    test_output = "static/images/articles/test_output.png"
    
    if os.path.exists(test_input):
        success = processor.process_image(test_input, test_output)
        print(f"Image processing {'successful' if success else 'failed'}")
    else:
        print("Test input image not found")
