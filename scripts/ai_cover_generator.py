#!/usr/bin/env python3
"""
AI Cover Image Generator for Hugo Blog
根据文章description自动生成封面图片
支持ModelScope Qwen-image和OpenAI DALL-E
"""

import os
import hashlib
import requests  # type: ignore[import-untyped]
import json
import argparse
import traceback
from pathlib import Path
from typing import Optional, Dict, cast
from dataclasses import dataclass
import logging
import time
from datetime import datetime
from PIL import Image
from PIL import ImageOps
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
    api_provider: str = "volcengine"  # volcengine(默认), ark, modelscope, openai, openrouter, dashscope
    api_key: str = ""
    model: str = "jimeng_t2i_v40"  # jimeng_t2i_v40, doubao-seedream-4-0-250828, Qwen/Qwen-Image, dall-e-3, google/gemini-3-pro-image-preview, wan2.5-t2i-preview

    # LLM 提示词生成配置 (Gemini/OpenAI)
    use_llm_prompt: bool = False  # 是否使用LLM生成提示词
    llm_provider: str = "gemini"  # gemini, openai
    gemini_api_key: str = ""  # Gemini API Key
    gemini_model: str = "gemini-3-flash-preview"  # Gemini 模型
    llm_openai_api_key: str = ""  # OpenAI API Key (用于生成prompt)
    llm_openai_model: str = "gpt-4o-mini"  # OpenAI 模型

    # 火山引擎配置（支持即梦等模型）
    volcengine_base_url: str = "https://visual.volcengineapi.com"
    volcengine_region: str = "cn-north-1"
    volcengine_service: str = "cv"
    volcengine_access_key: str = ""  # 火山引擎 Access Key
    volcengine_secret_key: str = ""  # 火山引擎 Secret Key
    volcengine_model: str = "jimeng_t2i_v40"  # 默认使用即梦4.0
    volcengine_timeout: int = 300  # 5分钟超时
    volcengine_retry_interval: int = 5  # 5秒重试间隔

    # ARK 配置（豆包文生图 Seedream）
    ark_api_key: str = ""  # ARK API Key
    ark_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    ark_model: str = "doubao-seedream-4-0-250828"  # 豆包 Seedream 4.0

    # ModelScope配置
    modelscope_base_url: str = "https://api-inference.modelscope.cn/"
    modelscope_timeout: int = 300  # 5分钟超时
    modelscope_retry_interval: int = 5  # 5秒重试间隔

    # OpenAI配置
    openai_base_url: str = "https://api.openai.com/v1/images/generations"

    # OpenRouter 配置
    openrouter_api_key: str = ""  # OpenRouter API Key
    openrouter_base_url: str = "https://openrouter.ai/api/v1"  # OpenRouter API Base URL
    openrouter_model: str = "google/gemini-3-pro-image-preview"  # 默认模型

    # DashScope 配置（通义万象）
    dashscope_api_key: str = ""  # DashScope API Key
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/api/v1"  # DashScope API Base URL
    dashscope_model: str = "wan2.5-t2i-preview"  # 通义万象 2.5 preview
    dashscope_timeout: int = 300  # 5分钟超时
    dashscope_poll_interval: int = 5  # 轮询间隔 5 秒

    # 图片配置 - 横屏尺寸适配博客卡片头部
    # 即梦API要求宽高乘积 >= 1024*1024，且推荐 2560x1440 (16:9)
    width: int = 2560  # 横屏宽度
    height: int = 1440   # 横屏高度 (16:9)。此值与 width=2560 一起满足即梦API要求的宽高乘积 >= 1024*1024，且为推荐的 16:9 比例
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

    def _generate_prompt_with_llm(self, title: str, article_content: str, category: str = "") -> Optional[str]:
        """使用LLM(如Gemini)根据博客全文生成图片提示词"""
        
        # 截取文章内容（避免超过token限制）
        max_content_length = 8000
        if len(article_content) > max_content_length:
            article_content = article_content[:max_content_length] + "...[truncated]"
        
        system_prompt = """
You are an expert Art Director and Prompt Engineer specializing in abstract, high-concept imagery for blog covers using the 'Tongyi Wanxiang' model.

YOUR GOAL:
Translate technical concepts into CONCRETE, PHYSICAL VISUAL METAPHORS with DYNAMIC, CINEMATIC COMPOSITIONS.
You must aggressively avoid the "single object in the dead center" cliché.

CORE RULES:
1. Output Language: Chinese (Simplified).
2. CONTENT RESTRICTIONS: NO text, letters, numbers, logos, or human faces.
3. FORMAT: 16:9 Widescreen.
4. OUTPUT FORMAT: Return ONLY the prompt string.

COMPOSITION STRATEGIES (CRITICAL - MUST VARY):
Do NOT default to centering the subject. Choose one of the following for each prompt:
- **Rule of Thirds (三分法)**: Place the focal point at the intersection of grid lines, leaving negative space.
- **Leading Lines (引导线)**: Use lines (roads, wires, light beams) to draw the eye from the corner into the distance.
- **Isometric/Orthographic (等距视角)**: A 3D map-like view from a high angle (good for systems/architecture).
- **Low Angle/Worm's Eye (低角度仰视)**: Make the subject look massive and imposing.
- **Macro/Close-up (微距特写)**: Focus on texture and detail, blurring the background heavily (Depth of Field).
- **Diagonal Composition (对角线构图)**: Create movement and tension across the frame.
- **Framing (框架式构图)**: View the subject through a "window" or opening in the foreground.

STEP-BY-STEP GENERATION LOGIC:
1. **Analyze**: Identify the core conflict or flow of the article.
2. **Metaphor**: Brainstorm a physical scene (e.g., "Data flow" -> "A complex system of glass pipes transporting glowing liquid").
3. **Style**: Select an art style (Surrealism, Bauhaus, Claymorphism, Cyberpunk, Ukiyo-e, Paper Art, Industrial Design).
4. **Composition**: Select a STRATEGY from the list above to ensure the image is NOT centered.
5. **Color**: Define a palette that matches the mood (e.g., Warm Amber & Teal for stability, Neon Purple & Black for mystery).

PROMPT STRUCTURE TO GENERATE:
[Art Style] + [Composition Strategy Description] + [Complex Scene/Interaction of Objects] + [Detailed Texture/Material] + [Lighting/Atmosphere] + [Color Palette] + "高品质，8k分辨率，电影级构图，无文字"

Example of "Composition Strategy Description" in output:
- Instead of "A robot", use "右下角放置一个微型机器人，左侧大面积留白(Rule of Thirds)"
- Instead of "A bridge", use "从低角度仰视一座跨越天际的半透明光桥(Low Angle)"
"""

        user_prompt = f"""
请阅读以下博客文章，并基于其核心逻辑，构思一个极具创意的视觉隐喻，生成绘画提示词。

文章元数据：
- 标题: {title}
- 分类: {category}

文章正文（摘要或全文）:
{article_content}

生成要求：
1. **拒绝平庸**：绝对不要出现电脑、手机、服务器机柜、电路板、0和1的代码雨。
2. **实体化**：如果文章讲的是“网络安全”，不要画盾牌，可以画“一座被水晶墙保护的微缩玻璃花园”。如果讲“Python学习”，不要画蛇，可以画“由乐高积木搭建的复杂机械结构”。
3. **详细描述**：包含具体的材质（如磨砂玻璃、丝绸、木质）、光影（体积光、丁达尔效应）和配色。
4. **纯中文输出**，直接给出提示词即可。
"""

        system_prompt = """
You are an expert Art Director and Prompt Engineer for an AI technology blog.
Your goal is to generate specific, high-quality image prompts for the 'Tongyi Wanxiang' model based on the blog article's category and content.

CORE RULES:
1. Output Language: Chinese (Simplified).
2. RESTRICTIONS: NO text, letters, numbers, logos, or human faces.
3. FORMAT: 16:9 Widescreen.
4. OUTPUT FORMAT: Return ONLY the prompt string.

---
COMPOSITION STRATEGIES (CRITICAL - MUST VARY):
Do NOT default to centering the subject. Choose one of the following for each prompt:
- **Rule of Thirds (三分法)**: Place the focal point at the intersection of grid lines, leaving negative space.
- **Leading Lines (引导线)**: Use lines (roads, wires, light beams) to draw the eye from the corner into the distance.
- **Isometric/Orthographic (等距视角)**: A 3D map-like view from a high angle (good for systems/architecture).
- **Low Angle/Worm's Eye (低角度仰视)**: Make the subject look massive and imposing.
- **Macro/Close-up (微距特写)**: Focus on texture and detail, blurring the background heavily (Depth of Field).
- **Diagonal Composition (对角线构图)**: Create movement and tension across the frame.
- **Framing (框架式构图)**: View the subject through a "window" or opening in the foreground.

---
### STYLE MAPPING LOGIC (CRITICAL)
First, identify which category the user's article belongs to, then select a style from that specific group.

**GROUP A: Architecture & Hard Tech**
*Categories: [基础模型, 训练微调技术, 技术栈, AI编程, 大厂产品线]*
*Visual Theme: Structural, Precise, Modular.*
*Select one Style:*
- **Isometric 3D (等距视角3D)**: Clean, god-like view of systems.
- **Bauhaus Style (包豪斯风格)**: Geometric, primary colors, functional shapes.
- **Blueprint Schematic (工程蓝图)**: Dark blue background, white technical lines.

**GROUP B: Logic, Agents & Flow**
*Categories: [多智能体, 上下文工程, 论文解读, AI标准规范]*
*Visual Theme: Interconnected, Fluid, Transparent.*
*Select one Style:*
- **Glassmorphism (磨砂玻璃质感)**: Floating translucent layers, soft shadows.
- **Data Pointillism (数据点彩派)**: Images formed by thousands of glowing dots/nodes.
- **Abstract Line Art (极简线条)**: Complex logic represented by clean, flowing lines.

**GROUP C: Insights & Future**
*Categories: [个人洞察, 名人洞察, 行业动态]*
*Visual Theme: Deep, Philosophical, Metaphorical.*
*Select one Style:*
- **Surrealism (超现实主义)**: Dreamlike, juxtaposing unrelated objects (e.g., a clock melting on a server).
- **Ukiyo-e (浮世绘风格)**: Traditional waves/mountains meeting cybernetic elements.
- **Cinematic Macro (电影级微距)**: Extreme close-up of an abstract object with shallow depth of field.

**GROUP D: Tools, Open Source & Learning**
*Categories: [开源项目, AI工具箱, 课程]*
*Visual Theme: Playful, Tactile, Accessible.*
*Select one Style:*
- **Claymorphism (3D软泥/粘土风格)**: Cute, soft, rounded edges, friendly.
- **Lego/Voxel Art (乐高/体素风格)**: Building blocks, pixelated 3D.
- **Pop Art (波普艺术)**: High contrast, vibrant colors, comic book dots.

---
### STEP-BY-STEP GENERATION:
1. **Classify**: Match the input `category` to Group A, B, C, or D.
2. **Select Style**: Randomly pick ONE style from that Group.
3. **Metaphor**: Create a physical object metaphor for the content (e.g., "Multi-Agent" -> "A swarm of glowing mechanical bees building a hive").
4. **Composition**: Apply a non-centered composition (Rule of Thirds, Leading Lines, Low Angle).
5. **Construct Prompt**:
   "[Selected Style] + [Composition Strategy] + [Visual Metaphor Scene] + [Lighting/Atmosphere] + [Color Palette] + 高品质，8k分辨率，无文字"
"""
        user_prompt = f"""        
文章标题: {title}
文章分类: {category}
文章内容摘要:
{article_content}

请根据System Prompt中的逻辑，为这篇文章生成封面提示词。
"""
        """
        import random, datetime
        current_hour = datetime.datetime.now().hour
        styles = ["浮世绘风格", "赛博朋克", "乐高积木风格", "蒸汽朋克", "极简线条画"]
        time_vibe = "清晨阳光" if current_hour < 12 else "午夜霓虹"

        # 在发送给Gemini之前，先在System Prompt里注入这个随机选出的风格
        injected_style = random.choice(styles)

        system_prompt = system_prompt + f"\nConstraint: You MUST use the art style: {injected_style} combined with {time_vibe}."
        """
        try:
            if self.config.llm_provider == "gemini":
                return self._call_gemini(system_prompt, user_prompt)
            elif self.config.llm_provider == "openai":
                return self._call_openai_for_prompt(system_prompt, user_prompt)
            else:
                logger.warning(f"Unknown LLM provider: {self.config.llm_provider}")
                return None
        except Exception as e:
            logger.error(f"LLM prompt generation failed: {e}")
            return None

    def _call_gemini(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """调用 Gemini API 生成提示词"""
        try:
            api_key = self.config.gemini_api_key
            if not api_key:
                logger.error("GEMINI_API_KEY not set")
                return None
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.gemini_model}:generateContent?key={api_key}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{system_prompt}\n\n{user_prompt}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.9,
                    "maxOutputTokens": 1000,
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and len(result["candidates"]) > 0:
                    text = result["candidates"][0]["content"]["parts"][0]["text"]
                    # 清理输出，去除可能的markdown标记
                    text = text.strip().strip('`').strip()
                    if text.startswith('```'):
                        text = text.split('\n', 1)[-1]
                    if text.endswith('```'):
                        text = text.rsplit('```', 1)[0]
                    logger.info(f"Gemini generated prompt: {text[:200]}...")
                    return text.strip()
                return None
            else:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return None

    def _call_openai_for_prompt(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """调用 OpenAI API 生成提示词"""
        try:
            api_key = self.config.llm_openai_api_key
            if not api_key:
                logger.error("LLM_OPENAI_API_KEY not set")
                return None
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.config.llm_openai_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.9,
                "max_tokens": 1000
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result["choices"][0]["message"]["content"].strip()
                logger.info(f"OpenAI generated prompt: {text[:200]}...")
                return text
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return None

    def _optimize_description(self, description: str, title: str, category: str = "") -> str:
        """优化描述为适合图片生成的prompt，增加多样性和内容相关性"""
        import random

        # 使用标题+描述的哈希值作为随机种子，确保同一篇文章生成稳定但不同文章有差异
        seed_text = f"{title}|{description}"
        seed = int(hashlib.md5(seed_text.encode()).hexdigest()[:8], 16)
        random.seed(seed)

        # 截断描述
        if len(description) > 200:
            description = description[:200]

        # 提取关键词以决定风格倾向
        text = f"{title} {description} {category}".lower()

        # ===== 1. 主题场景库 (更具体、更有画面感) =====
        theme_scenes = {
            'math': {
                'scenes': [
                    "漂浮在虚空中的金色正十二面体，表面刻满神秘符文",
                    "无限延伸的分形隧道，螺旋下降的黄金分割线",
                    "悬浮的水晶棱镜折射出彩虹光谱，几何体环绕",
                    "巨大的莫比乌斯环在星空中缓缓旋转",
                ],
                'colors': ["深邃宝蓝与金色", "紫水晶色与银白", "墨黑与琥珀金"],
                'keywords': ['math', 'imo', 'number', 'logic', 'reasoning', 'geometry', '数学', '推理', '逻辑', '几何', '证明', 'theorem']
            },
            'code': {
                'scenes': [
                    "无数行代码如瀑布般倾泻而下，汇聚成发光的河流",
                    "巨型CPU芯片的微观世界，晶体管如城市般排列",
                    "悬浮的终端窗口矩阵，绿色光标闪烁",
                    "由0和1组成的DNA双螺旋结构",
                ],
                'colors': ["黑客绿与深黑", "赛博朋克霓虹蓝粉", "矩阵绿与暗金"],
                'keywords': ['code', 'programming', 'software', 'github', 'linux', 'terminal', '代码', '编程', '开发', '源码', 'python', 'javascript', 'rust']
            },
            'ai_brain': {
                'scenes': [
                    "巨大的发光大脑悬浮在太空中，神经元连接闪烁如银河",
                    "机械蜂鸟与有机花朵的融合，金属与生命的交界",
                    "无数光点汇聚成人形轮廓，代表意识的诞生",
                    "镜面球体反射出无限的自我，AI觉醒的隐喻",
                ],
                'colors': ["电光蓝与洋红渐变", "粉紫与青色", "暖橙与冷蓝对比"],
                'keywords': ['brain', 'neural', 'cognitive', 'think', 'llm', 'gpt', 'claude', 'gemini', '大脑', '神经网络', '认知', '思考', '模型', 'transformer', 'agent']
            },
            'cloud_data': {
                'scenes': [
                    "云端之上的水晶数据中心，光纤如藤蔓缠绕",
                    "数据流如极光般在夜空中流动",
                    "无限延伸的服务器机房，蓝光LED阵列",
                    "透明的云朵中藏着微型城市，代表云计算",
                ],
                'colors': ["天空蓝与纯净白", "极光绿与深空蓝", "科技青与浅灰"],
                'keywords': ['cloud', 'server', 'data', 'network', 'api', '云', '服务器', '数据', '网络', '连接', 'kubernetes', 'docker', 'aws']
            },
            'security': {
                'scenes': [
                    "数字堡垒在虚空中矗立，盾牌反射着攻击",
                    "锁链与密钥在黑暗中发光",
                    "病毒代码如红色闪电被防火墙阻挡",
                    "指纹扫描光束穿透黑暗",
                ],
                'colors': ["深灰与警示红", "银色与电光蓝", "暗黑与金色防护罩"],
                'keywords': ['security', 'hack', 'privacy', 'lock', '安全', '黑客', '隐私', '加密', 'encryption', 'firewall']
            },
            'robot': {
                'scenes': [
                    "优雅的机器人手指轻触蝴蝶翅膀",
                    "机械臂在星空下组装微型宇宙",
                    "人形机器人静坐冥想，周围环绕数据光环",
                    "齿轮与电路交织的机械心脏",
                ],
                'colors': ["钛金属银与暖光", "工业橙与深蓝", "白色机甲与霓虹点缀"],
                'keywords': ['robot', 'automation', 'mechanical', '机器人', '自动化', 'humanoid', 'android']
            },
            'vision': {
                'scenes': [
                    "巨大的机械眼睛扫描城市天际线",
                    "像素化的世界逐渐变得清晰",
                    "无数摄像头编织成监控网络",
                    "眼睛中反射出数字世界的倒影",
                ],
                'colors': ["视网膜红与瞳孔黑", "扫描绿与数据蓝", "光学棱镜彩虹色"],
                'keywords': ['vision', 'image', 'recognition', 'camera', '视觉', '图像', '识别', 'cv', 'detection']
            },
            'nlp': {
                'scenes': [
                    "文字如星辰般漂浮在宇宙中，形成星座",
                    "巨大的书籍打开，文字飞出形成光带",
                    "对话气泡交织成复杂的网络",
                    "古老卷轴与现代全息投影的融合",
                ],
                'colors': ["墨水蓝与羊皮纸黄", "荧光绿与深紫", "渐变彩虹与纯白"],
                'keywords': ['nlp', 'language', 'text', 'chat', 'conversation', '语言', '文本', '对话', 'gpt', 'bert', 'embedding']
            },
            'product': {
                'scenes': [
                    "产品蓝图如全息图般展开",
                    "用户旅程化作发光的路径",
                    "交互界面元素在空中优雅排列",
                    "设计稿逐渐具象化的过程",
                ],
                'colors': ["产品白与交互蓝", "极简黑与点缀橙", "渐变紫与科技银"],
                'keywords': ['product', 'design', 'ux', 'ui', '产品', '设计', '交互', 'interface', 'user']
            },
            'research': {
                'scenes': [
                    "论文页面化作飞翔的纸鹤群",
                    "实验室中悬浮的分子结构模型",
                    "知识图谱如神经网络般延展",
                    "放大镜下的微观世界与宏观宇宙对照",
                ],
                'colors': ["学术蓝与论文白", "实验绿与试管透明", "知识金与智慧紫"],
                'keywords': ['research', 'paper', 'study', 'experiment', '研究', '论文', '实验', 'academic', 'science']
            },
            'protocol': {
                'scenes': [
                    "多个发光节点通过光束相互连接形成网络",
                    "不同颜色的数据包在管道中高速传输",
                    "握手协议可视化为两只光之手相握",
                    "层层叠加的协议栈如透明的摩天大楼",
                ],
                'colors': ["协议蓝与连接绿", "数据橙与节点白", "网络紫与通信青"],
                'keywords': ['protocol', 'a2a', 'mcp', 'api', 'http', 'grpc', '协议', '通信', 'agent', 'communication', 'interop']
            },
        }

        # ===== 2. 匹配主题 =====
        matched_theme = None
        for theme_name, theme_data in theme_scenes.items():
            if any(k in text for k in theme_data['keywords']):
                matched_theme = theme_data
                break

        # 默认主题
        if not matched_theme:
            matched_theme = {
                'scenes': [
                    "抽象的能量波在空间中扩散",
                    "几何形状在虚空中缓缓旋转",
                    "光与影交织的未来空间",
                    "数字粒子汇聚成神秘图案",
                ],
                'colors': ["科技蓝与未来银", "渐变紫与星空黑", "极光色与深空蓝"],
            }

        # ===== 3. 随机选择场景和配色 =====
        scene = random.choice(matched_theme['scenes'])
        color = random.choice(matched_theme['colors'])

        # ===== 4. 随机艺术风格组合 =====
        art_styles = [
            "C4D 3D渲染，Octane Render，体积光",
            "虚幻引擎5画质，光线追踪，超写实",
            "赛博朋克风格，霓虹灯光，未来都市",
            "极简主义，留白艺术，干净利落",
            "抽象表现主义，流体动态，能量感",
        ]
        
        lighting_effects = [
            "Tyndall effect丁达尔效应",
            "逆光剪影效果",
            "柔和的漫射光",
            "戏剧性的明暗对比",
            "梦幻般的光晕效果",
        ]
        
        perspectives = [
            "俯瞰视角，宏大场景",
            "微距特写，细节丰富",
            "正面对称构图",
            "动态斜角构图",
            "深远透视，空间感强",
        ]

        art_style = random.choice(art_styles)
        lighting = random.choice(lighting_effects)
        perspective = random.choice(perspectives)

        # ===== 5. 构建最终Prompt =====
        prompt = (
            f"【重要】这是一张纯视觉艺术作品，禁止出现任何文字、字母、数字、符号、Logo、水印。"
            f"画面主体：{scene}。"
            f"融入'{title}'的概念进行抽象艺术表达。"
            f"色彩方案：{color}。"
            f"艺术风格：{art_style}，{lighting}，{perspective}。"
            f"画质要求：8K超高清，细节精致，专业级博客封面。"
            f"构图：16:9宽屏横版，大气磅礴。"
            f"再次强调：纯图案背景，绝对不要包含任何文字元素。"
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
                except (ValueError, json.JSONDecodeError):
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

    def _generate_with_ark(self, prompt: str) -> Optional[str]:
        """使用 ARK API（豆包 Seedream）生成图片
        ARK 使用 OpenAI 兼容的 API 格式
        文档: https://www.volcengine.com/docs/82379/1298454
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.config.ark_api_key}",
                "Content-Type": "application/json"
            }

            # ARK API 使用 OpenAI 兼容格式
            data = {
                "model": self.config.ark_model,
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",  # ARK 支持的尺寸
            }

            # 完整的 API 端点
            url = f"{self.config.ark_base_url}/images/generations"
            
            logger.info(f"Calling ARK API: {url}")
            logger.info(f"Model: {self.config.ark_model}")

            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"ARK API response: {result}")
                
                # ARK 返回格式与 OpenAI 兼容
                if "data" in result and len(result["data"]) > 0:
                    image_url = result["data"][0].get("url") or result["data"][0].get("b64_json")
                    if image_url:
                        logger.info(f"✓ Image generated successfully")
                        return image_url
                    else:
                        logger.error("No image URL in response")
                        return None
                else:
                    logger.error(f"Unexpected response format: {result}")
                    return None
            else:
                logger.error(f"ARK API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"ARK generation error: {e}")
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

    def _generate_with_openrouter(self, prompt: str) -> Optional[str]:
        """使用 OpenRouter API 生成图片
        支持 google/gemini-2.5-flash-image-preview, nanobanana 等模型
        文档: https://openrouter.ai/docs/guides/overview/multimodal/image-generation
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.config.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://hobbytp.github.io",  # 可选，用于统计
                "X-Title": "AI Cover Generator"  # 可选，用于统计
            }

            # OpenRouter 图像生成需要设置 modalities 参数
            # 参考: https://openrouter.ai/docs/guides/overview/multimodal/image-generation
            data = {
                "model": self.config.openrouter_model,
                "messages": [
                    {
                        "role": "user",
                        "content": f"Generate an image: {prompt}"
                    }
                ],
                "modalities": ["image", "text"],  # 必须包含 image 和 text
                "image_config": {
                    "aspect_ratio": "16:9"  # 博客封面使用 16:9 比例 (1344×768)
                }
            }

            url = f"{self.config.openrouter_base_url}/chat/completions"
            
            logger.info(f"Calling OpenRouter API: {url}")
            logger.info(f"Model: {self.config.openrouter_model}")

            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=180  # 图像生成可能需要更长时间
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"OpenRouter API response keys: {list(result.keys())}")
                
                # OpenRouter 图像生成返回格式:
                # {
                #   "choices": [{
                #     "message": {
                #       "role": "assistant",
                #       "content": "描述文本",
                #       "images": [{
                #         "type": "image_url",
                #         "image_url": { "url": "data:image/png;base64,..." }
                #       }]
                #     }
                #   }]
                # }
                if "choices" in result and len(result["choices"]) > 0:
                    message = result["choices"][0].get("message", {})
                    
                    # 检查 images 字段（OpenRouter 标准返回格式）
                    images = message.get("images", [])
                    if images:
                        for img in images:
                            if img.get("type") == "image_url":
                                image_url = img.get("image_url", {}).get("url", "")
                                if image_url:
                                    logger.info(f"✓ Found image in response (length: {len(image_url)})")
                                    return image_url
                    
                    # 备用：检查 content 中是否有 base64 图片
                    content = message.get("content", "")
                    if content and "data:image" in content:
                        import re
                        base64_pattern = r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+'
                        match = re.search(base64_pattern, content)
                        if match:
                            logger.info("✓ Found base64 image in content")
                            return match.group(0)
                    
                    logger.error(f"No images found in response. Message keys: {list(message.keys())}")
                    logger.error(f"Content preview: {content[:200] if content else 'empty'}")
                    return None
                else:
                    logger.error(f"Unexpected response format: {result}")
                    return None
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"OpenRouter generation error: {e}")
            logger.error(traceback.format_exc())
            return None

    def _generate_with_dashscope(self, prompt: str) -> Optional[str]:
        """使用 DashScope（通义万象）生成图片
        采用异步调用方式：创建任务 -> 轮询获取结果
        文档: https://help.aliyun.com/zh/model-studio/text-to-image
        """
        try:
            # 步骤1：创建任务
            create_url = f"{self.config.dashscope_base_url}/services/aigc/text2image/image-synthesis"
            
            headers = {
                "Authorization": f"Bearer {self.config.dashscope_api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable"  # 必须设置为异步模式
            }

            # 通义万象支持的尺寸：总像素在[768*768, 1440*1440]之间，宽高比[1:4, 4:1]
            # 16:9 比例推荐 1280*720 或 1344*768
            data = {
                "model": self.config.dashscope_model,
                "input": {
                    "prompt": prompt
                },
                "parameters": {
                    "size": "1280*720",  # 16:9 横屏比例
                    "n": 1,
                    "prompt_extend": False,  # 不使用智能改写，保持LLM生成的prompt
                    "watermark": False
                }
            }

            logger.info(f"Creating DashScope task: {create_url}")
            logger.info(f"Model: {self.config.dashscope_model}")

            response = requests.post(
                create_url,
                headers=headers,
                json=data,
                timeout=60
            )

            if response.status_code != 200:
                logger.error(f"DashScope create task error: {response.status_code} - {response.text}")
                return None

            result = response.json()
            
            # 检查是否有错误
            if "code" in result:
                logger.error(f"DashScope API error: {result.get('code')} - {result.get('message')}")
                return None

            task_id = result.get("output", {}).get("task_id")
            if not task_id:
                logger.error(f"No task_id in response: {result}")
                return None

            logger.info(f"DashScope task created: {task_id}")

            # 步骤2：轮询获取结果
            query_url = f"{self.config.dashscope_base_url}/tasks/{task_id}"
            query_headers = {
                "Authorization": f"Bearer {self.config.dashscope_api_key}"
            }

            start_time = time.time()
            while True:
                # 检查超时
                elapsed = time.time() - start_time
                if elapsed > self.config.dashscope_timeout:
                    logger.error(f"DashScope task timeout after {elapsed:.0f}s")
                    return None

                # 等待后查询
                time.sleep(self.config.dashscope_poll_interval)

                query_response = requests.get(
                    query_url,
                    headers=query_headers,
                    timeout=30
                )

                if query_response.status_code != 200:
                    logger.error(f"DashScope query error: {query_response.status_code} - {query_response.text}")
                    return None

                query_result = query_response.json()
                task_status = query_result.get("output", {}).get("task_status")

                logger.info(f"DashScope task status: {task_status} (elapsed: {elapsed:.0f}s)")

                if task_status == "SUCCEEDED":
                    # 获取图片URL
                    results = query_result.get("output", {}).get("results", [])
                    if results and len(results) > 0:
                        image_url = results[0].get("url")
                        if image_url:
                            logger.info(f"✓ DashScope image generated: {image_url[:80]}...")
                            return image_url
                    logger.error(f"No image URL in results: {results}")
                    return None

                elif task_status == "FAILED":
                    error_code = query_result.get("output", {}).get("code", "Unknown")
                    error_msg = query_result.get("output", {}).get("message", "Unknown error")
                    logger.error(f"DashScope task failed: {error_code} - {error_msg}")
                    return None

                elif task_status in ["PENDING", "RUNNING"]:
                    # 继续等待
                    continue

                else:
                    logger.error(f"Unknown task status: {task_status}")
                    return None

        except Exception as e:
            logger.error(f"DashScope generation error: {e}")
            logger.error(traceback.format_exc())
            return None

    def _download_image(self, url: str, filepath: str) -> bool:
        """下载生成的图片并转换为webp格式
        支持 HTTP URL 和 base64 data URL
        """
        try:
            import base64
            
            # 检查是否是 base64 data URL
            if url.startswith("data:image"):
                # 解析 data URL: data:image/png;base64,iVBORw0KGgo...
                try:
                    # 分离 header 和 data
                    header, encoded = url.split(",", 1)
                    image_data = base64.b64decode(encoded)
                    image = cast(Image.Image, Image.open(BytesIO(image_data)))
                    logger.info(f"Decoded base64 image: {image.size}")
                except Exception as e:
                    logger.error(f"Failed to decode base64 image: {e}")
                    return False
            else:
                # HTTP URL - 下载图片
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    image = cast(Image.Image, Image.open(BytesIO(response.content)))
                else:
                    logger.error(f"Image download error: {response.status_code}")
                    return False
            
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
            
        except Exception as e:
            logger.error(f"Image download/convert error: {e}")
            return False

    def generate_cover(self, title: str, description: str, category: str = "", force: bool = False, article_content: str = "") -> Optional[str]:
        """
        生成封面图片

        Args:
            title: 文章标题
            description: 文章描述
            category: 文章分类
            force: 是否强制重新生成
            article_content: 文章全文（用于LLM生成提示词）

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

        # 生成prompt - 优先使用LLM，失败则回退到规则生成
        prompt = None
        if self.config.use_llm_prompt and article_content:
            logger.info("🤖 Using LLM to generate image prompt...")
            prompt = self._generate_prompt_with_llm(title, article_content, category)
            if prompt:
                logger.info(f"✅ LLM generated prompt successfully")
            else:
                logger.warning("⚠️ LLM prompt generation failed, falling back to rule-based prompt")
        
        if not prompt:
            prompt = self._optimize_description(description, title, category)
        
        logger.info(f"Generating image with prompt: {prompt[:500]}...")

        # 调用AI生成图片
        image_url = None
        if self.config.api_provider == "volcengine":
            image_url = self._generate_with_volcengine(prompt)
        elif self.config.api_provider == "ark":
            image_url = self._generate_with_ark(prompt)
        elif self.config.api_provider == "modelscope":
            image_url = self._generate_with_modelscope(prompt)
        elif self.config.api_provider == "openai":
            image_url = self._generate_with_openai(prompt)
        elif self.config.api_provider == "openrouter":
            image_url = self._generate_with_openrouter(prompt)
        elif self.config.api_provider == "dashscope":
            image_url = self._generate_with_dashscope(prompt)
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
            "image_path": str(filepath).replace("\\", "/"),
            "relative_path": relative_path,
            "prompt": prompt,
            "generated_at": datetime.now().isoformat()
        }
        self._save_cache()

        logger.info(f"Generated cover image: {relative_path}")
        return relative_path

    def generate_cover_from_photo(self, photo_path: Path, output_filename: str, force: bool = False) -> Optional[str]:
        """使用现成图片生成博客封面。

        - 自动按 16:9 居中裁切
        - 缩放到 config.width x config.height
        - 输出为 WebP 到 config.output_dir

        Returns:
            图片URL路径（相对于static目录），例如 /images/generated-covers/xxx.webp
        """
        try:
            photo_path = Path(photo_path)
            if not photo_path.exists() or not photo_path.is_file():
                logger.error(f"Photo not found: {photo_path}")
                return None

            output_filename = output_filename.strip()
            if not output_filename:
                logger.error("output_filename is empty")
                return None
            if not output_filename.lower().endswith(".webp"):
                output_filename = f"{output_filename}.webp"

            filepath = Path(self.config.output_dir) / output_filename
            if filepath.exists() and not force:
                web_friendly_path = str(filepath).replace("\\", "/")
                return web_friendly_path.replace("static/", "/", 1)

            with Image.open(photo_path) as img:
                img = ImageOps.exif_transpose(img)
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGB")

                target_w = int(self.config.width)
                target_h = int(self.config.height)
                target_ratio = target_w / target_h

                src_w, src_h = img.size
                if src_h == 0:
                    logger.error(f"Invalid image size: {img.size}")
                    return None

                src_ratio = src_w / src_h

                # 居中裁切到目标比例
                if src_ratio > target_ratio:
                    new_w = int(src_h * target_ratio)
                    left = max(0, (src_w - new_w) // 2)
                    img = img.crop((left, 0, left + new_w, src_h))
                else:
                    new_h = int(src_w / target_ratio)
                    top = max(0, (src_h - new_h) // 2)
                    img = img.crop((0, top, src_w, top + new_h))

                # 缩放（兼容 Pillow 新旧版本 & 类型桩差异）
                resampling = getattr(Image, "Resampling", None)
                resample = getattr(resampling, "LANCZOS", None) if resampling else None
                if resample is None:
                    resample = getattr(Image, "LANCZOS", None)
                if resample is None:
                    resample = getattr(Image, "BICUBIC")
                img = img.resize((target_w, target_h), resample)
                if img.mode == "RGBA":
                    # WebP 可存 RGBA，但为了兼容性/体积，这里统一转 RGB
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background

                filepath.parent.mkdir(parents=True, exist_ok=True)
                img.save(filepath, "WEBP", quality=85, method=6)

            web_friendly_path = str(filepath).replace("\\", "/")
            relative_path = web_friendly_path.replace("static/", "/", 1)
            logger.info(f"Generated photo-based cover: {relative_path}")
            return relative_path

        except Exception as e:
            logger.error(f"Photo cover generation error: {e}")
            return None

    def delete_cover(self, article_path: Path) -> bool:
        """删除文章的AI封面图片和缓存"""
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.startswith('---'):
                return False

            parts = content.split('---', 2)
            if len(parts) < 3:
                return False

            front_matter = parts[1]
            article_content = parts[2]

            # 解析title和description获取hash
            title = description = ''
            for line in front_matter.split('\n'):
                if line.strip().startswith('title:'):
                    title = line.split(':', 1)[1].strip().strip('"\'')
                elif line.strip().startswith('description:'):
                    description = line.split(':', 1)[1].strip().strip('"\'')

            if not title or not description:
                logger.info(f"No title/description in {article_path.name}, skipping")
                return False

            content_hash = hashlib.md5(f"{title}|{description}".encode()).hexdigest()
            deleted_anything = False

            # 删除缓存
            if content_hash in self.cache:
                del self.cache[content_hash]
                self._save_cache()
                logger.info(f"✅ Deleted cache: {content_hash}")
                deleted_anything = True

            # 删除图片
            img_path = Path(self.config.output_dir) / f"{content_hash}.webp"
            if img_path.exists():
                img_path.unlink()
                logger.info(f"✅ Deleted image: {img_path.name}")
                deleted_anything = True

            # 移除front matter中的AI封面信息
            new_lines = []
            skip = False
            for line in front_matter.split('\n'):
                if line.strip().startswith('ai_cover:') or line.strip().startswith('cover:'):
                    skip = True
                    continue
                if skip and (line.startswith('  ') or line.startswith('\t')):
                    continue
                if skip and line.strip():
                    skip = False
                if not skip or not line.strip():
                    new_lines.append(line)

            updated_fm = '\n'.join(new_lines).strip()
            updated_content = f"---\n{updated_fm}\n---{article_content}"

            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            logger.info(f"✅ Cleaned front matter: {article_path.name}")
            deleted_anything = True

            return deleted_anything

        except Exception as e:
            logger.error(f"Error deleting cover: {e}")
            return False

class HugoArticleUpdater:
    """Hugo文章更新器"""

    def __init__(self, content_dir: str = "content", generator: Optional[CoverImageGenerator] = None):
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

    def update_article_with_cover(self, article_path: Path, image_path: str, *, ai_generated: bool = True, write_ai_cover: bool = True):
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
                stripped = line.strip()
                if stripped.startswith('title:'):
                    title = stripped.split(':', 1)[1].strip().strip('"\'')
                elif stripped.startswith('description:'):
                    description = stripped.split(':', 1)[1].strip().strip('"\'')
                elif stripped.startswith('categories:'):
                    # 简单处理，取第一个分类
                    if '[' in stripped:
                        category = stripped.split('[', 1)[1].split(']', 1)[0].split(',')[0].strip().strip('"\'')

            # AI 生成模式保持原有严格要求（需要 title + description）
            if ai_generated:
                if not title or not description:
                    logger.warning(f"Missing title or description in {article_path}")
                    return False
            else:
                # 照片封面模式：允许没有 description；title 缺失则回退到文件名
                if not title:
                    title = article_path.stem

            # 转换Windows路径为Web路径
            web_image_path = image_path.replace('\\', '/')

            # 移除旧的封面配置（如果存在）
            lines = front_matter.split('\n')
            new_lines = []
            skip_mode = False
            
            for line in lines:
                # 检查是否是封面相关的配置行
                if line.strip().startswith('cover:') or line.strip().startswith('ai_cover:'):
                    skip_mode = True
                    continue

                if skip_mode and (line.strip().startswith('image:') or line.strip().startswith('alt:') or line.strip().startswith('ai_generated:')):
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

            # 在front matter中添加封面图片信息
            cover_image_block_lines = []
            if write_ai_cover:
                cover_image_block_lines.append(f'ai_cover: "{web_image_path}"')
            cover_image_block_lines.append("cover:")
            cover_image_block_lines.append(f'  image: "{web_image_path}"')
            cover_image_block_lines.append(f'  alt: "{title}"')
            if ai_generated:
                # 保持原有行为：在 cover 下标记 AI 生成
                cover_image_block_lines.append("  ai_generated: true")

            cover_image_block = "\n" + "\n".join(cover_image_block_lines)

            updated_front_matter = f"{clean_front_matter}\n{cover_image_block}\n"
            updated_content = f"---\n{updated_front_matter}---{article_content}"

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

            return False

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
    parser.add_argument('--delete', action='store_true', help='Delete cover images and cache')
    parser.add_argument('--category', type=str, help='Filter by category (use with --delete)')
    parser.add_argument('--use-llm-prompt', action='store_true', help='Use LLM (Gemini/OpenAI) to generate image prompts from full article content')
    parser.add_argument('--llm-provider', choices=['gemini', 'openai'], default='gemini', help='LLM provider for prompt generation')
    parser.add_argument('--photo', type=str, help='Use an existing photo to generate cover (requires --specific-file to be a single markdown file)')
    args = parser.parse_args()

    # 现成照片生成封面模式（不依赖任何 AI API Key）
    if args.photo:
        if not args.specific_file:
            logger.error("--photo requires --specific-file (a single markdown file)")
            return

        article_path = Path(args.specific_file)
        if not article_path.exists() or not article_path.is_file() or article_path.suffix.lower() != ".md":
            logger.error(f"--specific-file must be a markdown file: {article_path}")
            return

        photo_path = Path(args.photo)
        if not photo_path.exists() or not photo_path.is_file():
            logger.error(f"Photo not found: {photo_path}")
            return

        # 使用与 AI 封面一致的输出目录，确保站点可直接引用
        config = ImageGenConfig(output_dir="static/images/generated-covers")
        generator = CoverImageGenerator(config)
        updater = HugoArticleUpdater(generator=generator)

        output_filename = f"{article_path.stem}.webp"
        image_path = generator.generate_cover_from_photo(photo_path, output_filename, force=args.force)
        if not image_path:
            logger.error("Failed to generate cover from photo")
            return

        if updater.update_article_with_cover(article_path, image_path, ai_generated=False, write_ai_cover=False):
            logger.info(f"✅ Updated cover from photo for {article_path}")
        else:
            logger.error(f"❌ Failed to update article with photo cover: {article_path}")
        return

    # 处理删除模式
    if args.delete:
        content_dir = Path('content')
        temp_config = ImageGenConfig(output_dir="static/images/generated-covers")
        gen = CoverImageGenerator(temp_config)

        articles = []
        if args.specific_file:
            p = Path(args.specific_file)
            if p.exists():
                articles.append(p)
            else:
                logger.error(f"File not found: {args.specific_file}")
                return
        else:
            for md in content_dir.rglob("*.md"):
                if md.name == "_index.md":
                    continue
                if args.category:
                    try:
                        with open(md, 'r') as f:
                            c = f.read()
                        if args.category in c:
                            articles.append(md)
                    except:
                        pass
                else:
                    articles.append(md)

        if not articles:
            logger.info("No articles found")
            return

        logger.info(f"Found {len(articles)} article(s)")
        count = 0
        for a in articles:
            logger.info(f"\n🗑️  {a.name}")
            if gen.delete_cover(a):
                count += 1
        logger.info(f"\n✅ Deleted {count}/{len(articles)} covers")
        return

    # 配置
    api_provider = os.getenv("TEXT2IMAGE_PROVIDER", "volcengine")  # volcengine(默认), ark, modelscope, openai, openrouter, dashscope
    workflow_mode = args.workflow_mode or os.getenv("WORKFLOW_MODE", "").lower() == "true"
    force_regenerate = args.force or os.getenv("FORCE_REGENERATE", "").lower() == "true"
    
    # LLM 配置
    use_llm_prompt = args.use_llm_prompt or os.getenv("USE_LLM_PROMPT", "").lower() == "true"
    llm_provider = args.llm_provider or os.getenv("LLM_PROVIDER", "gemini")
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    llm_openai_api_key = os.getenv("LLM_OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))

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
            style_suffix=", professional blog cover, clean design, technology theme, minimal",
            # LLM 配置
            use_llm_prompt=use_llm_prompt,
            llm_provider=llm_provider,
            gemini_api_key=gemini_api_key,
            llm_openai_api_key=llm_openai_api_key,
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
            style_suffix=", professional blog cover, clean design, technology theme, minimal",
            use_llm_prompt=use_llm_prompt,
            llm_provider=llm_provider,
            gemini_api_key=gemini_api_key,
            llm_openai_api_key=llm_openai_api_key,
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
            style_suffix=", professional blog cover, clean design, technology theme, minimal",
            use_llm_prompt=use_llm_prompt,
            llm_provider=llm_provider,
            gemini_api_key=gemini_api_key,
            llm_openai_api_key=llm_openai_api_key,
        )

        if not config.api_key:
            logger.error("Please set OPENAI_API_KEY environment variable")
            return

    elif api_provider == "ark":
        ark_api_key = os.getenv("ARK_API_KEY", "")
        ark_base_url = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        ark_model = os.getenv("ARK_MODEL", "doubao-seedream-4-0-250828")

        config = ImageGenConfig(
            api_provider="ark",
            api_key=ark_api_key,
            model=ark_model,
            ark_api_key=ark_api_key,
            ark_base_url=ark_base_url,
            ark_model=ark_model,
            output_dir="static/images/generated-covers",
            style_suffix=", professional blog cover, clean design, technology theme, minimal",
            use_llm_prompt=use_llm_prompt,
            llm_provider=llm_provider,
            gemini_api_key=gemini_api_key,
            llm_openai_api_key=llm_openai_api_key,
        )

        if not config.ark_api_key:
            logger.error("Please set ARK_API_KEY environment variable")
            logger.error("You can get it from: https://console.volcengine.com/ark")
            return

    elif api_provider == "openrouter":
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
        openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        openrouter_model = os.getenv("OPENROUTER_MODEL", "google/gemini-3-pro-image-preview")

        config = ImageGenConfig(
            api_provider="openrouter",
            api_key=openrouter_api_key,
            model=openrouter_model,
            openrouter_api_key=openrouter_api_key,
            openrouter_base_url=openrouter_base_url,
            openrouter_model=openrouter_model,
            output_dir="static/images/generated-covers",
            style_suffix=", professional blog cover, clean design, technology theme, minimal",
            use_llm_prompt=use_llm_prompt,
            llm_provider=llm_provider,
            gemini_api_key=gemini_api_key,
            llm_openai_api_key=llm_openai_api_key,
        )

        if not config.openrouter_api_key:
            logger.error("Please set OPENROUTER_API_KEY environment variable")
            logger.error("You can get it from: https://openrouter.ai/keys")
            return

    elif api_provider == "dashscope":
        dashscope_api_key = os.getenv("DASHSCOPE_API_KEY", "")
        dashscope_base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/api/v1")
        # 移除 compatible-mode 路径，使用标准 API 路径
        if "compatible-mode" in dashscope_base_url:
            dashscope_base_url = "https://dashscope.aliyuncs.com/api/v1"
        dashscope_model = os.getenv("DASHSCOPE_MODEL", "wan2.5-t2i-preview")

        config = ImageGenConfig(
            api_provider="dashscope",
            api_key=dashscope_api_key,
            model=dashscope_model,
            dashscope_api_key=dashscope_api_key,
            dashscope_base_url=dashscope_base_url,
            dashscope_model=dashscope_model,
            output_dir="static/images/generated-covers",
            style_suffix=", professional blog cover, clean design, technology theme, minimal",
            use_llm_prompt=use_llm_prompt,
            llm_provider=llm_provider,
            gemini_api_key=gemini_api_key,
            llm_openai_api_key=llm_openai_api_key,
        )

        if not config.dashscope_api_key:
            logger.error("Please set DASHSCOPE_API_KEY environment variable")
            logger.error("You can get it from: https://bailian.console.aliyun.com/")
            return

    else:
        logger.error(f"Unsupported provider: {api_provider}. Use 'volcengine', 'ark', 'modelscope', 'openai', 'openrouter' or 'dashscope'")
        return

    # 初始化生成器
    generator = CoverImageGenerator(config)

    if workflow_mode:
        logger.info("🤖 Running in GitHub Actions workflow mode")
        logger.info(f"Target: {args.target}, Force: {force_regenerate}, Limit: {args.limit}")
    
    if use_llm_prompt:
        logger.info("🧠 LLM prompt generation enabled - using Gemini to analyze article content")

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
                article_body = ""
            else:
                front_matter_end = content.find('\n---', first_line_end + 1)
                front_matter = content[first_line_end + 1:front_matter_end] if front_matter_end > 0 else ""
                article_body = content[front_matter_end + 4:] if front_matter_end > 0 else ""
        else:
            front_matter = ""
            article_body = content

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

            # 生成封面 (传递文章全文用于LLM生成提示词)
            image_path = generator.generate_cover(
                title, description, category, 
                force=force_regenerate,
                article_content=article_body
            )

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