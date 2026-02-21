import os
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

class LLMConfig:
    def __init__(self):
        self.provider_name = "Google"
        self.model_name = "gemini-3-flash-preview"
        self.temperature = 0.5
        self.api_key_env = "GEMINI_API_KEY"
        self.is_openai_compatible = False
        self.api_base_url = ""
        self.api_key = None
        self.use_google_sdk = False
        
        load_dotenv()
        self._load_config()

    def _load_config(self):
        config_path = Path(__file__).parent.parent.parent.parent / "llm_config.json"
        
        try:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                role_config = config.get("roleConfigs", {}).get("DAILY_REPORT", {})
                self.provider_name = role_config.get("provider", self.provider_name)
                self.model_name = role_config.get("model", self.model_name)
                self.temperature = role_config.get("temperature", self.temperature)
                
                provider_config = config.get("providers", {}).get(self.provider_name, {})
                self.api_base_url = provider_config.get("apiBaseUrl", self.api_base_url)
                self.api_key_env = provider_config.get("apiKeyEnv", self.api_key_env)
                self.is_openai_compatible = provider_config.get("openaiCompatible", self.is_openai_compatible)
                # 备用配置 (DAILY_REPORT_BK)
                bk_role_config = config.get("roleConfigs", {}).get("DAILY_REPORT_BK", {})
                self.bk_provider_name = bk_role_config.get("provider", "")
                self.bk_model_name = bk_role_config.get("model", "")
                self.bk_temperature = bk_role_config.get("temperature", 0.5)
                
                if self.bk_provider_name:
                    bk_provider_config = config.get("providers", {}).get(self.bk_provider_name, {})
                    self.bk_api_base_url = bk_provider_config.get("apiBaseUrl", "")
                    self.bk_api_key_env = bk_provider_config.get("apiKeyEnv", "")
                    self.bk_is_openai_compatible = bk_provider_config.get("openaiCompatible", False)
                else:
                    self.bk_api_key_env = ""
            else:
                self.bk_api_key_env = ""
        except Exception as e:
            print(f"[ERROR] 读取 llm_config.json 失败: {e}，将使用默认配置")
            self.bk_api_key_env = ""
            
        self.api_key = os.getenv(self.api_key_env)
        if not self.api_key and self.api_key_env == "GOOGLE_API_KEY":
            self.api_key = os.getenv("GEMINI_API_KEY")
            
        if self.provider_name == "Google" and not self.is_openai_compatible:
             self.use_google_sdk = True

        self.bk_api_key = os.getenv(self.bk_api_key_env) if self.bk_api_key_env else None
        self.use_google_sdk_bk = (self.bk_provider_name == "Google" and getattr(self, "bk_is_openai_compatible", False) is False)

config = LLMConfig()
