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
    api_provider: str = "volcengine"  # volcengine(默认), modelscope, openai
    api_key: str = ""
    model: str = "jimeng_t2i_v40"  # jimeng_t2i_v40, Qwen/Qwen-Image, dall-e-3

    # 火山引擎配置（支持即梦等模型）
    volcengine_base_url: str = "https://visual.volcengineapi.com"
    volcengine_region: str = "cn-north-1"
    volcengine_service: str = "cv"
    volcengine_access_key: str = ""  # 火山引擎 Access Key
    volcengine_secret_key: str = ""  # 火山引擎 Secret Key
    volcengine_model: str = "jimeng_t2i_v40"  # 默认使用即梦4.0
    volcengine_timeout: int = 300  # 5分钟超时
    volcengine_retry_interval: int = 5  # 5秒重试间隔

    # ModelScope配置
    modelscope_base_url: str = "https://api-inference.modelscope.cn/"
    modelscope_timeout: int = 300  # 5分钟超时
    modelscope_retry_interval: int = 5  # 5秒重试间隔

    # OpenAI配置
    openai_base_url: str = "https://api.openai.com/v1/images/generations"

    # 图片配置 - 横屏尺寸适配博客卡片头部
    # 即梦API要求宽高乘积 >= 1024*1024，且推荐 2560x1440 (16:9)
    width: int = 2560  # 横屏宽度
    height: int = 1440   # 横屏高度 (16:9)
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
        # 截断描述
        if len(description) > 300:
            description = description[:300]

        # 提取关键词以决定风格倾向
        text = f"{title} {description}".lower()
        
        # 默认风格元素
        base_visuals = "未来科技感，抽象线条，光影交错，流体形态"
        color_tone = "冷色调，高级感，渐变色"
        
        # 根据关键词调整视觉元素和配色
        if any(k in text for k in ['math', 'imo', 'number', 'logic', 'reasoning', 'geometry', '数学', '推理', '逻辑', '几何', '证明']):
            base_visuals = "黄金分割，分形几何，柏拉图立体，抽象数学符号，秩序感，理性结构，悬浮的几何体"
            color_tone = "深邃蓝紫色，搭配金色线条点缀，神秘，严谨"
        elif any(k in text for k in ['code', 'programming', 'software', 'github', 'linux', 'terminal', '代码', '编程', '开发', '源码']):
            base_visuals = "数字矩阵，代码流，像素化构建块，终端界面元素，赛博空间，电路板纹理"
            color_tone = "黑客绿，暗黑背景，霓虹光效，极客风"
        elif any(k in text for k in ['brain', 'neural', 'cognitive', 'think', 'llm', 'gpt', '大脑', '神经网络', '认知', '思考', '模型']):
            base_visuals = "发光的神经元网络，突触连接，思维火花，生物科技融合，能量脉冲，智能体"
            color_tone = "电光蓝，洋红，粉紫渐变，梦幻，灵动"
        elif any(k in text for k in ['cloud', 'server', 'data', 'network', 'api', '云', '服务器', '数据', '网络', '连接']):
            base_visuals = "云端架构，高速数据流，互联节点，无限延伸的网格，玻璃质感，透明传输"
            color_tone = "纯净白，天蓝，青色，通透感，轻盈"
        elif any(k in text for k in ['security', 'hack', 'privacy', 'lock', '安全', '黑客', '隐私', '加密']):
            base_visuals = "盾牌概念，锁链，防御网，扫描光束，金属质感"
            color_tone = "深灰，银色，警示红光，坚硬"

        # 将描述作为视觉元素的一部分，增加画面的独特性
        visual_elements = f"{base_visuals}。融合基于'{description}'的抽象概念可视化"

        # 构建中文Prompt (针对即梦/火山引擎优化)
        prompt = (
            f"一张极具设计感的博客封面图。主题：{title}。"
            f"核心视觉元素：{visual_elements}。"
            f"艺术风格：C4D 3D渲染，Octane Render，极简主义，虚幻引擎5画质，Tyndall effect，8k分辨率，超高清，细节丰富。"
            f"色彩氛围：{color_tone}。"
            f"构图：宽屏壁纸，大气磅礴，留白适中，中心构图或三分法。"
            f"重要提示：纯图案背景，绝对不要包含任何文字、字母、数字、拼音、汉字、水印、LOGO。不要出现人脸。"
        )
        
        return prompt

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

    def _generate_with_volcengine(self, prompt: str) -> Optional[str]:
        """使用火山引擎视觉API生成图片（支持即梦4.0等模型）"""
        try:
            import hashlib
            import hmac
            from datetime import datetime
            from urllib.parse import quote

            # 构建请求参数
            params = {
                "Action": "CVSync2AsyncSubmitTask",
                "Version": "2022-08-31"
            }
            
            # 使用配置的模型（默认jimeng_t2i_v40）
            req_key = self.config.volcengine_model or "jimeng_t2i_v40"
            
            body = {
                "req_key": req_key,
                "prompt": prompt,
                "width": self.config.width,
                "height": self.config.height,
                "force_single": True  # 强制单图输出,控制延迟和成本
            }

            # 火山引擎签名V4（修正：按照官方HTTP文档实现）
            def sign_request(method, url, query_params, headers, payload):
                # 获取当前时间
                from datetime import timezone
                now = datetime.now(timezone.utc)
                date_stamp = now.strftime('%Y%m%d')
                amz_date = now.strftime('%Y%m%dT%H%M%SZ')
                
                # 计算 payload hash
                payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
                
                # Canonical Request（修正：添加 x-content-sha256）
                canonical_uri = '/'
                # Query参数直接拼接，不进行URL编码（按照官方Python示例）
                canonical_querystring = '&'.join([f"{k}={v}" for k, v in sorted(query_params.items())])
                
                signed_headers = 'content-type;host;x-content-sha256;x-date'
                canonical_headers = f"content-type:{headers['Content-Type']}\nhost:{headers['Host']}\nx-content-sha256:{payload_hash}\nx-date:{amz_date}\n"
                
                canonical_request = f"{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
                
                # String to Sign
                algorithm = 'HMAC-SHA256'
                credential_scope = f"{date_stamp}/{self.config.volcengine_region}/{self.config.volcengine_service}/request"
                string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
                
                # Signing Key（修正：移除VOLC前缀，与官方Python示例一致）
                def get_signature_key(key, date_stamp, region_name, service_name):
                    k_date = hmac.new(key.encode('utf-8'), date_stamp.encode('utf-8'), hashlib.sha256).digest()
                    k_region = hmac.new(k_date, region_name.encode('utf-8'), hashlib.sha256).digest()
                    k_service = hmac.new(k_region, service_name.encode('utf-8'), hashlib.sha256).digest()
                    k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
                    return k_signing
                
                signing_key = get_signature_key(self.config.volcengine_secret_key, date_stamp, self.config.volcengine_region, self.config.volcengine_service)
                signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
                
                # Authorization Header
                authorization_header = f"{algorithm} Credential={self.config.volcengine_access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
                
                return authorization_header, amz_date, payload_hash

            # 构建URL和Headers
            from urllib.parse import urlparse
            parsed_url = urlparse(self.config.volcengine_base_url)
            host = parsed_url.netloc
            url = self.config.volcengine_base_url
            
            headers = {
                "Content-Type": "application/json",
                "Host": host
            }
            
            payload = json.dumps(body, ensure_ascii=False)
            authorization, amz_date, payload_hash = sign_request('POST', url, params, headers, payload)
            
            headers['Authorization'] = authorization
            headers['X-Date'] = amz_date
            headers['X-Content-Sha256'] = payload_hash
            
            # 提交任务
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            submit_url = f"{url}?{query_string}"
            
            logger.info(f"Submitting Volcengine task (model: {req_key})...")
            
            response = requests.post(
                submit_url,
                headers=headers,
                data=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                logger.error(f"Volcengine API Error: {response.status_code}")
                logger.error(f"Response Body: {response.text}")
                
                # Check for AccessDenied
                try:
                    err_data = response.json()
                    if err_data.get("ResponseMetadata", {}).get("Error", {}).get("Code") == "AccessDenied":
                        logger.error("❌ 权限不足 (AccessDenied): 请检查火山引擎IAM策略，确保拥有 'cv:CVSync2AsyncSubmitTask' 权限")
                except:
                    pass
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") != 10000:
                logger.error(f"Volcengine task submission failed: {result.get('message')}")
                return None
            
            task_id = result["data"]["task_id"]
            logger.info(f"Volcengine task submitted: {task_id}")
            
            # 轮询查询结果
            query_params = {
                "Action": "CVSync2AsyncGetResult",
                "Version": "2022-08-31"
            }
            
            query_body = {
                "req_key": req_key,
                "task_id": task_id,
                "req_json": json.dumps({"return_url": True}, ensure_ascii=False)
            }
            
            start_time = time.time()
            while True:
                if time.time() - start_time > self.config.volcengine_timeout:
                    logger.error(f"Volcengine task timeout after {self.config.volcengine_timeout} seconds")
                    return None
                
                # 重新签名查询请求
                query_payload = json.dumps(query_body, ensure_ascii=False)
                query_authorization, query_amz_date, query_payload_hash = sign_request('POST', url, query_params, headers, query_payload)
                
                query_headers = {
                    "Content-Type": "application/json",
                    "Host": host,
                    "Authorization": query_authorization,
                    "X-Date": query_amz_date,
                    "X-Content-Sha256": query_payload_hash
                }
                
                query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
                query_url = f"{url}?{query_string}"
                
                result_response = requests.post(
                    query_url,
                    headers=query_headers,
                    data=query_payload,
                    timeout=30
                )
                
                if result_response.status_code != 200:
                    logger.error(f"Volcengine Query Error: {result_response.status_code}")
                    logger.error(f"Response Body: {result_response.text}")
                
                result_response.raise_for_status()
                query_result = result_response.json()
                
                if query_result.get("code") != 10000:
                    logger.error(f"Volcengine query failed: {query_result.get('message')}")
                    return None
                
                status = query_result["data"]["status"]
                
                if status == "done":
                    image_urls = query_result["data"].get("image_urls", [])
                    if image_urls:
                        image_url = image_urls[0]
                        logger.info(f"Volcengine image generated successfully: {image_url}")
                        return image_url
                    else:
                        logger.error("Volcengine generation completed but no image URLs returned")
                        return None
                elif status == "not_found":
                    logger.error("Volcengine task not found")
                    return None
                elif status == "expired":
                    logger.error("Volcengine task expired")
                    return None
                elif status in ["in_queue", "generating"]:
                    logger.info(f"Volcengine task {status}, elapsed: {int(time.time() - start_time)}s")
                    time.sleep(self.config.volcengine_retry_interval)
                else:
                    logger.warning(f"Unknown Volcengine task status: {status}")
                    time.sleep(self.config.volcengine_retry_interval)
                    
        except Exception as e:
            logger.error(f"Volcengine generation error: {e}")
            import traceback
            logger.error(traceback.format_exc())
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
        if self.config.api_provider == "volcengine":
            image_url = self._generate_with_volcengine(prompt)
        elif self.config.api_provider == "modelscope":
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

            # 移除旧的封面配置（如果存在）
            lines = front_matter.split('\n')
            new_lines = []
            skip_mode = False
            
            for line in lines:
                # 检查是否是封面相关的配置行
                if line.strip().startswith('ai_cover:') or \
                   line.strip().startswith('cover:') or \
                   (skip_mode and (line.strip().startswith('image:') or line.strip().startswith('alt:') or line.strip().startswith('ai_generated:'))):
                    
                    if line.strip().startswith('cover:'):
                        skip_mode = True
                    continue
                
                # 如果遇到非缩进的行，且不是封面配置，则退出跳过模式
                if skip_mode and line.strip() and not line.startswith(' '):
                    skip_mode = False
                
                # 如果是空行，也保留（除非在跳过模式中）
                if skip_mode and not line.strip():
                    continue
                    
                new_lines.append(line)

            # 重建front matter
            clean_front_matter = '\n'.join(new_lines).strip()

            # 在front matter中添加AI生成图片信息
            cover_image_block = f"""
ai_cover: "{web_image_path}"
cover:
  image: "{web_image_path}"
  alt: "{title}"
  ai_generated: true"""

            updated_front_matter = f"{clean_front_matter}\n{cover_image_block}\n"
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
    api_provider = os.getenv("TEXT2IMAGE_PROVIDER", "volcengine")  # volcengine(默认), modelscope, openai
    workflow_mode = args.workflow_mode or os.getenv("WORKFLOW_MODE", "").lower() == "true"
    force_regenerate = args.force or os.getenv("FORCE_REGENERATE", "").lower() == "true"

    if api_provider == "volcengine":
        # 支持从环境变量配置模型（默认jimeng_t2i_v40）
        volcengine_model = os.getenv("VOLCENGINE_MODEL", "jimeng_t2i_v40")
        
        # 获取Access Key和Secret Key
        # 火山引擎API密钥格式说明：
        # - Access Key: 明文字符串，以AKLT开头
        # - Secret Key: 可能是Base64编码或明文，先尝试直接使用
        import base64
        
        access_key_raw = os.getenv("VOLCENGINE_ACCESS_KEY", os.getenv("ARK_API_KEY", ""))
        secret_key_raw = os.getenv("VOLCENGINE_SECRET_KEY", os.getenv("ARK_SECRET_KEY", ""))
        
        # Access Key 直接使用
        access_key = access_key_raw
        
        # Secret Key 先尝试直接使用（不解码）
        secret_key = secret_key_raw
        logger.info(f"✓ Using Access Key (length: {len(access_key)})")
        logger.info(f"✓ Using Secret Key (length: {len(secret_key)}, ends with: {'==' if secret_key.endswith('==') else 'other'})")
        
        config = ImageGenConfig(
            api_provider="volcengine",
            api_key="",  # 火山引擎使用Access Key/Secret Key而非单一API Key
            volcengine_access_key=access_key,
            volcengine_secret_key=secret_key,
            volcengine_model=volcengine_model,
            model=volcengine_model,
            output_dir="static/images/generated-covers",
            style_suffix=", professional blog cover, clean design, technology theme, minimal"
        )

        if not config.volcengine_access_key or not config.volcengine_secret_key:
            logger.error("⚠️  警告: 未设置 VOLCENGINE_ACCESS_KEY 或 VOLCENGINE_SECRET_KEY 环境变量")
            logger.error("请在 .env 文件中添加:")
            logger.error("  VOLCENGINE_ACCESS_KEY=AKLT... (明文，AKLT开头)")
            logger.error("  VOLCENGINE_SECRET_KEY=...== (Base64编码，从火山控制台获取)")
            logger.error("  VOLCENGINE_MODEL=jimeng_t2i_v40  # 可选，默认即梦4.0")
            logger.error("  VOLCENGINE_MODEL=jimeng_t2i_v40  # 可选，默认即梦4.0")
            return

    elif api_provider == "modelscope":
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
        logger.error(f"Unsupported provider: {api_provider}. Use 'volcengine', 'modelscope' or 'openai'")
        return

    # 初始化生成器
    generator = CoverImageGenerator(config)

    if workflow_mode:
        logger.info("🤖 Running in GitHub Actions workflow mode")
        logger.info(f"Target: {args.target}, Force: {force_regenerate}, Limit: {args.limit}")

    # 查找需要封面的文章
    updater = HugoArticleUpdater(generator=generator)

    if args.specific_file:
        # 处理特定文件或目录
        path = Path(args.specific_file)
        if path.exists():
            if path.is_file():
                articles = [str(path)]
                logger.info(f"Processing specific file: {path}")
            elif path.is_dir():
                articles = [str(p) for p in path.rglob("*.md") if p.name != "_index.md"]
                logger.info(f"Processing directory: {path}, found {len(articles)} articles")
        else:
            logger.error(f"File or directory not found: {args.specific_file}")
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
            # 检查是否已有AI封面
            if updater.has_ai_cover(article_path) and not force_regenerate:
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