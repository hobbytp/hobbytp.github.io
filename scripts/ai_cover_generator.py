#!/usr/bin/env python3
"""
AI Cover Image Generator for Hugo Blog
根据文章description自动生成封面图片
支持ModelScope Qwen-image和OpenAI DALL-E
"""

import os
import hashlib
import requests
import json
import argparse
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass
import logging
import time
from PIL import Image
from io import BytesIO

# 加载.env文件中的环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # 如果没有python-dotenv，手动读取.env文件
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"').strip("'")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ImageGenConfig:
    """图片生成配置"""
    # API配置
    api_provider: str = "modelscope"  # modelscope, openai
    api_key: str = ""
    model: str = "Qwen/Qwen-Image"  # Qwen/Qwen-Image, dall-e-3

    # ModelScope配置
    modelscope_base_url: str = "https://api-inference.modelscope.cn/"
    modelscope_timeout: int = 300  # 5分钟超时
    modelscope_retry_interval: int = 5  # 5秒重试间隔

    # OpenAI配置
    openai_base_url: str = "https://api.openai.com/v1/images/generations"

    # 图片配置 - 横屏尺寸适配博客卡片头部
    width: int = 1200  # 横屏宽度
    height: int = 630   # 横屏高度 (16:9比例)
    quality: str = "standard"  # standard, hd
    style: str = "vivid"  # vivid, natural

    # 存储配置
    output_dir: str = "static/images/generated-covers"
    cache_dir: str = "cache/image-generation"

    # 生成配置
    max_description_length: int = 1000
    style_suffix: str = ", abstract geometric pattern, professional blog cover, clean design, minimal, technology theme, no text, no letters, no words, no people, no faces, no portraits, landscape orientation, widescreen format"

class CoverImageGenerator:
    """封面图片生成器"""

    def __init__(self, config: ImageGenConfig):
        self.config = config
        self._ensure_directories()
        self._load_cache()

    def _ensure_directories(self):
        """确保目录存在"""
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.cache_dir).mkdir(parents=True, exist_ok=True)

    def _load_cache(self):
        """加载生成缓存"""
        self.cache_file = Path(self.config.cache_dir) / "generation_cache.json"
        if self.cache_file.exists():
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self.cache = json.load(f)
        else:
            self.cache = {}

    def _save_cache(self):
        """保存缓存"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def _get_content_hash(self, title: str, description: str) -> str:
        """生成内容哈希作为缓存键"""
        content = f"{title}|{description}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def _optimize_description(self, description: str, title: str, category: str = "") -> str:
        """优化描述为适合图片生成的prompt"""
        # 截断描述并提取关键概念
        if len(description) > self.config.max_description_length:
            description = description[:self.config.max_description_length] + "..."

        # 提取文章主题的关键词，避免直接包含标题文字
        keywords = self._extract_keywords(description, title)

        # 构建prompt - 专注于抽象概念，不包含具体文字
        prompt_parts = [
            f"Abstract geometric blog cover representing concepts from: {keywords}",
            f"Technology and innovation theme inspired by {category}" if category else "Technology and innovation theme",
            "Clean professional design suitable for blog header",
            "Minimalist modern aesthetic",
            "Digital art style with smooth gradients",
            "Subtle tech-inspired patterns",
            self.config.style_suffix
        ]

        prompt = " ".join(filter(None, prompt_parts))
        return prompt.strip()

    def _extract_keywords(self, description: str, title: str) -> str:
        """从描述和标题中提取关键词，移除常见的停用词"""
        import re

        # 合并标题和描述
        text = f"{title} {description}".lower()

        # 常见的停用词和不需要视觉化的词
        stop_words = {
            '的', '了', '是', '在', '有', '和', '与', '或', '但', '如果', '因为', '所以', '这', '那', '这些', '那些',
            'the', 'a', 'an', 'and', 'or', 'but', 'if', 'because', 'so', 'this', 'that', 'these', 'those',
            'blog', 'article', 'post', 'news', 'report', 'analysis', 'review', 'guide', 'tutorial'
        }

        # 提取技术相关关键词
        tech_keywords = re.findall(r'\b(ai|artificial intelligence|machine learning|deep learning|neural network|algorithm|data|code|software|app|api|cloud|digital|technology|computer|programming|development|framework|model|system|platform|service|tool|automation|robot|chatbot|language model|llm|gpt|claude|openai|google|microsoft|apple|meta|tesla|bitcoin|blockchain|web3|metaverse|vr|ar|iot|edge|security|privacy|encryption|hack|cyber|quantum|5g|mobile|android|ios)\b', text)

        # 去重并移除停用词
        unique_keywords = []
        for word in tech_keywords:
            if word not in stop_words and word not in unique_keywords:
                unique_keywords.append(word)

        # 如果没有找到技术关键词，使用通用的科技词汇
        if not unique_keywords:
            unique_keywords = ['technology', 'digital', 'innovation', 'data', 'software']

        # 限制关键词数量
        return ' '.join(unique_keywords[:5])

    def _generate_with_modelscope(self, prompt: str) -> Optional[str]:
        """使用ModelScope Qwen-Image生成图片"""
        try:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            }

            # 提交异步任务
            response = requests.post(
                f"{self.config.modelscope_base_url}v1/images/generations",
                headers={**headers, "X-ModelScope-Async-Mode": "true"},
                data=json.dumps({
                    "model": self.config.model,
                    "prompt": prompt,
                    "width": self.config.width,
                    "height": self.config.height
                }, ensure_ascii=False).encode('utf-8'),
                timeout=60
            )

            response.raise_for_status()
            task_id = response.json()["task_id"]
            logger.info(f"ModelScope task submitted: {task_id}")

            # 轮询任务状态
            start_time = time.time()
            while True:
                if time.time() - start_time > self.config.modelscope_timeout:
                    logger.error(f"ModelScope task timeout after {self.config.modelscope_timeout} seconds")
                    return None

                result = requests.get(
                    f"{self.config.modelscope_base_url}v1/tasks/{task_id}",
                    headers={**headers, "X-ModelScope-Task-Type": "image_generation"},
                    timeout=30
                )
                result.raise_for_status()
                data = result.json()

                if data["task_status"] == "SUCCEED":
                    image_url = data["output_images"][0]
                    logger.info(f"ModelScope image generated successfully: {image_url}")
                    return image_url
                elif data["task_status"] == "FAILED":
                    error_msg = data.get("message", "Unknown error")
                    logger.error(f"ModelScope image generation failed: {error_msg}")
                    return None
                elif data["task_status"] == "RUNNING":
                    logger.info(f"ModelScope task running, elapsed: {int(time.time() - start_time)}s")
                    time.sleep(self.config.modelscope_retry_interval)
                else:
                    logger.warning(f"Unknown ModelScope task status: {data['task_status']}")
                    time.sleep(self.config.modelscope_retry_interval)

        except Exception as e:
            logger.error(f"ModelScope generation error: {e}")
            return None

    def _generate_with_openai(self, prompt: str) -> Optional[str]:
        """使用OpenAI DALL-E生成图片"""
        try:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.config.model,
                "prompt": prompt,
                "n": 1,
                "size": f"{self.config.width}x{self.config.height}",
                "quality": self.config.quality,
                "style": self.config.style
            }

            response = requests.post(
                self.config.openai_base_url,
                headers=headers,
                json=data,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                image_url = result["data"][0]["url"]
                return image_url
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            return None

    def _download_image(self, url: str, filepath: str) -> bool:
        """下载生成的图片并转换为webp格式"""
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                # 使用PIL打开图片（支持各种格式）
                image = Image.open(BytesIO(response.content))
                
                # 如果图片有透明通道（RGBA），转换为RGB以支持webp
                if image.mode in ('RGBA', 'LA', 'P'):
                    # 创建白色背景
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # 保存为webp格式，优化质量
                image.save(filepath, 'WEBP', quality=85, method=6)
                logger.info(f"Image converted to webp: {filepath}")
                return True
            else:
                logger.error(f"Image download error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Image download/convert error: {e}")
            return False

    def generate_cover(self, title: str, description: str, category: str = "", force: bool = False) -> Optional[str]:
        """
        生成封面图片

        Args:
            title: 文章标题
            description: 文章描述
            category: 文章分类
            force: 是否强制重新生成

        Returns:
            图片URL路径（相对于static目录）
        """
        # 生成内容哈希
        content_hash = self._get_content_hash(title, description)

        # 检查缓存
        if not force and content_hash in self.cache:
            cached_path = self.cache[content_hash]["image_path"]
            if Path(cached_path).exists():
                logger.info(f"Using cached image: {cached_path}")
                return cached_path.replace("static/", "/", 1)

        # 生成prompt
        prompt = self._optimize_description(description, title, category)
        logger.info(f"Generating image with prompt: {prompt[:1000]}...")

        # 调用AI生成图片
        image_url = None
        if self.config.api_provider == "modelscope":
            image_url = self._generate_with_modelscope(prompt)
        elif self.config.api_provider == "openai":
            image_url = self._generate_with_openai(prompt)
        else:
            logger.error(f"Unsupported API provider: {self.config.api_provider}")
            return None

        if not image_url:
            logger.error("Failed to generate image")
            return None

    # 生成文件名
    filename = f"{content_hash}.webp"
    filepath = Path(self.config.output_dir) / filename

        # 下载图片
        if not self._download_image(image_url, str(filepath)):
            return None

    # 生成相对路径（统一为web路径）
    web_friendly_path = str(filepath).replace("\\", "/")
    relative_path = web_friendly_path.replace("static/", "/", 1)

        # 更新缓存
        self.cache[content_hash] = {
            "title": title,
            "description": description[:200],
            "category": category,
            "image_path": str(filepath),
            "relative_path": relative_path,
            "prompt": prompt,
            "generated_at": str(Path().resolve())
        }
        self._save_cache()

        logger.info(f"Generated cover image: {relative_path}")
        return relative_path

class HugoArticleUpdater:
    """Hugo文章更新器"""

    def __init__(self, content_dir: str = "content", generator: CoverImageGenerator = None):
        self.content_dir = Path(content_dir)
        self.generator = generator

    def find_articles_without_covers(self) -> list:
        """查找没有封面的文章"""
        articles = []

        for md_file in self.content_dir.rglob("*.md"):
            if md_file.name == "_index.md":
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 解析front matter
                if content.startswith('---'):
                    first_line_end = content.find('\n')
                    if first_line_end == -1:
                        continue

                    front_matter_end = content.find('\n---', first_line_end + 1)
                    if front_matter_end == -1:
                        continue

                    front_matter = content[first_line_end + 1:front_matter_end]
                    article_content = content[front_matter_end + 4:]

                    # 检查是否已有图片
                    has_cover = ('cover.image:' in front_matter or
                               'image:' in front_matter or
                               'ai_cover:' in front_matter)

                    # 检查是否有description
                    has_description = 'description:' in front_matter

                    if not has_cover and has_description:
                        articles.append(md_file)

            except Exception as e:
                logger.warning(f"Error processing {md_file}: {e}")

        return articles

    def update_article_with_cover(self, article_path: Path, image_path: str):
        """为文章添加封面图片"""
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.startswith('---'):
                logger.warning(f"No front matter found in {article_path}")
                return False

            # Split content by the front matter delimiters
            parts = content.split('---', 2)
            if len(parts) < 3:
                logger.warning(f"Invalid front matter format in {article_path}")
                return False

            # parts[0] is empty (before first ---)
            # parts[1] is the front matter content
            # parts[2] is the article content
            front_matter = parts[1]
            article_content = parts[2]

            # 解析必要信息
            title = ""
            description = ""
            category = ""

            for line in front_matter.split('\n'):
                if line.startswith('title:'):
                    title = line.split(':', 1)[1].strip().strip('"\'')
                elif line.startswith('description:'):
                    description = line.split(':', 1)[1].strip().strip('"\'')
                elif line.startswith('categories:'):
                    # 简单处理，取第一个分类
                    if '[' in line:
                        category = line.split('[', 1)[1].split(']', 1)[0].split(',')[0].strip().strip('"\'')

            if not title or not description:
                logger.warning(f"Missing title or description in {article_path}")
                return False

            # 转换Windows路径为Web路径
            web_image_path = image_path.replace('\\', '/')

            # 在front matter中添加AI生成图片信息
            cover_image_block = f"""
ai_cover: "{web_image_path}"
cover:
  image: "{web_image_path}"
  alt: "{title}"
  ai_generated: true
"""

            # 确保front matter以换行符结束，然后添加cover信息
            if not front_matter.endswith('\n'):
                front_matter += '\n'

            updated_front_matter = front_matter + cover_image_block
            updated_content = f"---{updated_front_matter}---{article_content}"

            # 写回文件
            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            logger.info(f"Updated {article_path} with cover image: {web_image_path}")
            return True

        except Exception as e:
            logger.error(f"Error updating {article_path}: {e}")
            return False

    def find_articles_with_descriptions(self) -> list:
        """查找有description的文章"""
        articles = []

        for md_file in self.content_dir.rglob("*.md"):
            if md_file.name == "_index.md":
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 解析front matter
                if content.startswith('---'):
                    first_line_end = content.find('\n')
                    if first_line_end == -1:
                        continue

                    front_matter_end = content.find('\n---', first_line_end + 1)
                    if front_matter_end == -1:
                        continue

                    front_matter = content[first_line_end + 1:front_matter_end]
                    article_content = content[front_matter_end + 4:]

                    # 检查是否有description
                    has_description = 'description:' in front_matter

                    if has_description:
                        articles.append(md_file)

            except Exception as e:
                logger.warning(f"Error processing {md_file}: {e}")

        return articles

    def has_ai_cover(self, article_path: Path) -> bool:
        """检查文章是否已有AI封面"""
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if content.startswith('---'):
                first_line_end = content.find('\n')
                if first_line_end == -1:
                    return False

                front_matter_end = content.find('\n---', first_line_end + 1)
                if front_matter_end == -1:
                    return False

                front_matter = content[first_line_end + 1:front_matter_end]
                return 'ai_cover:' in front_matter

        except Exception as e:
            logger.warning(f"Error checking AI cover for {article_path}: {e}")
            return False

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='AI Cover Image Generator for Hugo Blog')
    parser.add_argument('--workflow-mode', action='store_true', help='Run in workflow mode')
    parser.add_argument('--target', choices=['covers', 'articles'], default='covers', help='Generation target')
    parser.add_argument('--force', action='store_true', help='Force regenerate existing images')
    parser.add_argument('--limit', type=int, default=10, help='Limit number of articles to process')
    parser.add_argument('--specific-file', type=str, help='Process a specific file only')
    args = parser.parse_args()

    # 配置
    api_provider = os.getenv("TEXT2IMAGE_PROVIDER", "modelscope")  # modelscope, openai
    workflow_mode = args.workflow_mode or os.getenv("WORKFLOW_MODE", "").lower() == "true"
    force_regenerate = args.force or os.getenv("FORCE_REGENERATE", "").lower() == "true"

    if api_provider == "modelscope":
        config = ImageGenConfig(
            api_provider="modelscope",
            api_key=os.getenv("MODELSCOPE_API_KEY", ""),
            model="Qwen/Qwen-Image",
            output_dir="static/images/generated-covers",
            style_suffix=", professional blog cover, clean design, technology theme, minimal"
        )

        if not config.api_key:
            logger.error("Please set MODELSCOPE_API_KEY environment variable")
            return

    elif api_provider == "openai":
        config = ImageGenConfig(
            api_provider="openai",
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model="dall-e-3",
            output_dir="static/images/generated-covers",
            style_suffix=", professional blog cover, clean design, technology theme, minimal"
        )

        if not config.api_key:
            logger.error("Please set OPENAI_API_KEY environment variable")
            return
    else:
        logger.error(f"Unsupported provider: {api_provider}. Use 'modelscope' or 'openai'")
        return

    # 初始化生成器
    generator = CoverImageGenerator(config)

    if workflow_mode:
        logger.info("🤖 Running in GitHub Actions workflow mode")
        logger.info(f"Target: {args.target}, Force: {force_regenerate}, Limit: {args.limit}")

    # 查找需要封面的文章
    updater = HugoArticleUpdater(generator=generator)

    if args.specific_file:
        # 处理特定文件
        if os.path.exists(args.specific_file):
            articles = [args.specific_file]
            logger.info(f"Processing specific file: {args.specific_file}")
        else:
            logger.error(f"File not found: {args.specific_file}")
            return
    elif force_regenerate:
        # 强制模式：查找所有有description的文章
        articles = updater.find_articles_with_descriptions()
        logger.info(f"Force regenerate mode: Found {len(articles)} articles with descriptions")
    else:
        # 正常模式：查找没有封面的文章
        articles = updater.find_articles_without_covers()
        logger.info(f"Found {len(articles)} articles without covers")

    # 限制处理数量（workflow模式，但不影响特定文件处理）
    if workflow_mode and not args.specific_file and args.limit > 0 and len(articles) > args.limit:
        articles = articles[:args.limit]
        logger.info(f"Limited to {args.limit} articles for workflow")

    # 为每篇文章生成封面
    success_count = 0
    for i, article_path in enumerate(articles):
        logger.info(f"Processing {i+1}/{len(articles)}: {article_path}")

        # 读取文章信息
        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if content.startswith('---'):
            first_line_end = content.find('\n')
            if first_line_end == -1:
                front_matter = ""
            else:
                front_matter_end = content.find('\n---', first_line_end + 1)
                front_matter = content[first_line_end + 1:front_matter_end] if front_matter_end > 0 else ""
        else:
            front_matter = ""

        title = ""
        description = ""
        category = ""

        for line in front_matter.split('\n'):
            if line.startswith('title:'):
                title = line.split(':', 1)[1].strip().strip('"\'')
            elif line.startswith('description:'):
                description = line.split(':', 1)[1].strip().strip('"\'')
            elif line.startswith('categories:'):
                if '[' in line:
                    category = line.split('[', 1)[1].split(']', 1)[0].split(',')[0].strip().strip('"\'')

        if title and description:
            # 检查是否已有AI封面（在force模式下）
            if force_regenerate and updater.has_ai_cover(article_path):
                logger.info(f"Skipping {article_path} - already has AI cover (use --force to override)")
                continue

            # 生成封面
            image_path = generator.generate_cover(title, description, category)

            if image_path:
                # 更新文章
                if updater.update_article_with_cover(article_path, image_path):
                    success_count += 1
                    logger.info(f"✅ Successfully generated and updated cover for {article_path}")
                else:
                    logger.error(f"❌ Failed to update article with cover {article_path}")
            else:
                logger.error(f"❌ Failed to generate cover for {article_path}")
        else:
            logger.warning(f"⚠️ Skipping {article_path} - missing title or description")

        # 避免API限制
        time.sleep(2)

    # 生成完成报告
    logger.info(f"🎉 AI cover generation completed!")
    logger.info(f"✅ Successfully generated: {success_count}/{len(articles)} covers")

    if workflow_mode:
        logger.info(f"Workflow mode completed with {success_count} covers generated")

if __name__ == "__main__":
    main()