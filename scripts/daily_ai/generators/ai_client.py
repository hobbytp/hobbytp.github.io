import re
import time
import os

try:
    from google import genai
except ImportError:
    genai = None

try:
    import openai
except ImportError:
    openai = None

from scripts.daily_ai.config.config_loader import config

# 最大重试次数和基础等待时间
_MAX_RETRIES = 4
_BASE_WAIT = 15  # seconds


def _parse_retry_delay(err_msg: str) -> float:
    """从错误消息中提取建议等待秒数，例如 'retryDelay: 34s'"""
    match = re.search(r"retryDelay.*?(\d+(?:\.\d+)?)s", str(err_msg))
    if match:
        return float(match.group(1)) + 2  # 加 2s 缓冲
    
    # 检查是否是 Google 的强限流
    if "GenerateRequestsPerDayPerProjectPerModel-FreeTier" in str(err_msg):
        # 这种 429 意味着已用尽一天的配额。等待也没用，返回大数字直接中断重试。
        return 99999.0
        
    return _BASE_WAIT


class AIClient:
    """统一的 AI 调用客户端，内置 429/503 自动重试及备用模型降级"""

    def __init__(self):
        self.client = None
        self.bk_client = None
        self.use_google_sdk = False
        self._init_client()

    def _init_client(self):
        # 初始化主客户端
        if not config.api_key:
            print("[ERROR] 主 API Key 未设置，主生成功能将不可用！")
        elif config.use_google_sdk and genai:
            try:
                self.client = genai.Client(api_key=config.api_key)
                self.use_google_sdk = True
            except Exception as e:
                print(f"ERROR: Google SDK 初始化失败: {e}")
        elif openai:
            try:
                base_url = config.api_base_url
                if not base_url and "gemini" in config.model_name.lower():
                    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

                self.client = openai.OpenAI(
                    api_key=config.api_key,
                    base_url=base_url if base_url else None,
                )
            except Exception as e:
                print(f"ERROR: OpenAI兼容客户端初始化失败: {e}")

        # 初始化备用客户端
        if getattr(config, "bk_api_key", None):
            if getattr(config, "use_google_sdk_bk", False) and genai:
                try:
                    self.bk_client = genai.Client(api_key=config.bk_api_key)
                except Exception as e:
                    print(f"ERROR: 备用 Google SDK 初始化失败: {e}")
            elif openai:
                try:
                    self.bk_client = openai.OpenAI(
                        api_key=config.bk_api_key,
                        base_url=config.bk_api_base_url if getattr(config, "bk_api_base_url", None) else None,
                    )
                except Exception as e:
                    print(f"ERROR: 备用 OpenAI 兼容客户端初始化失败: {e}")

    def _call_once(self, prompt: str) -> str:
        """发起一次主 LLM 调用（不含重试）"""
        if self.use_google_sdk:
            response = self.client.models.generate_content(
                model=config.model_name,
                contents=prompt,
                config={'temperature': config.temperature, 'max_output_tokens': 8192},
            )
            return response.text if hasattr(response, 'text') else ""
        else:
            response = self.client.chat.completions.create(
                model=config.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8192,
                temperature=config.temperature,
            )
            return response.choices[0].message.content if response.choices else ""
            
    def _call_once_bk(self, prompt: str) -> str:
        """发起一次备用 LLM 调用（不含重试）"""
        if getattr(config, "use_google_sdk_bk", False):
            response = self.bk_client.models.generate_content(
                model=config.bk_model_name,
                contents=prompt,
                config={'temperature': getattr(config, 'bk_temperature', 0.5), 'max_output_tokens': 8192},
            )
            return response.text if hasattr(response, 'text') else ""
        else:
            response = self.bk_client.chat.completions.create(
                model=config.bk_model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8192,
                temperature=getattr(config, 'bk_temperature', 0.5),
            )
            return response.choices[0].message.content if response.choices else ""

    def generate(self, prompt: str) -> str:
        if not self.client and not self.bk_client:
            return "由于所有 AI 客户端均未初始化，生成失败。"

        last_err = None
        if self.client:
            for attempt in range(1, _MAX_RETRIES + 1):
                try:
                    return self._call_once(prompt)
                except Exception as e:
                    err_str = str(e)
                    last_err = e

                    # 只对限流 / 暂时不可用错误重试
                    is_retryable = (
                        "429" in err_str
                        or "RESOURCE_EXHAUSTED" in err_str
                        or "503" in err_str
                        or "UNAVAILABLE" in err_str
                    )

                    wait_sec = _parse_retry_delay(err_str) if is_retryable else 0
                    
                    if is_retryable and attempt < _MAX_RETRIES and wait_sec < 999:
                        print(
                            f"[WARNING] 主 LLM 限流/不可用 (尝试 {attempt}/{_MAX_RETRIES})，"
                            f"等待 {wait_sec:.0f}s 后重试..."
                        )
                        time.sleep(wait_sec)
                    else:
                        break  # 非限流错误或已用完重试次数，或确定配额已尽，直接退出循环

            print(f"[ERROR] 主 LLM 生成最终失败: {last_err}")

        # 如果主模型失败 或 根本没有加载主模型，则走备用模型
        if self.bk_client:
            print("[INFO] 启用备用 LLM 客户端 (降级调用)...")
            try:
                res = self._call_once_bk(prompt)
                return res
            except Exception as e:
                print(f"[ERROR] 备用 LLM 生成失败: {e}")
                err_msg = f"主控和备控均已失败。主原因: {last_err}，备原因: {e}"
                return f"> 暂无 AI 总结，生成时遇到不可恢复的错误: {err_msg}"
        else:
            return f"> 暂无 AI 总结，生成时遇到错误且未配置备用模型: {last_err}"
