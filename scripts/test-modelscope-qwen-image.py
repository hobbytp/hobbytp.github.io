import requests
import time
import json
from PIL import Image
from io import BytesIO

import os
from pathlib import Path
# 自动加载.env文件
try:
    from dotenv import load_dotenv
    # 尝试从项目根目录加载.env文件
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        
except ImportError:
    # python-dotenv未安装时跳过
    pass

api_key = os.getenv('MODELSCOPE_API_KEY')
if not api_key:
    raise ValueError("MODELSCOPE_API_KEY environment variable not set")
base_url = os.getenv('MODELSCOPE_BASE_URL')
if not base_url:
    raise ValueError("MODELSCOPE_BASE_URL environment variable not set")
model_name=os.getenv('MODELSCOPE_MODEL')
if not model_name:
    raise ValueError("MODELSCOPE_MODEL environment variable not set")

prompt = "A golden cat"
common_headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

response = requests.post(
    f"{base_url}v1/images/generations",
    headers={**common_headers, "X-ModelScope-Async-Mode": "true"},
    data=json.dumps({
        "model": model_name, # ModelScope Model-Id, required
        "prompt": prompt
    }, ensure_ascii=False).encode('utf-8')
)

response.raise_for_status()
task_id = response.json()["task_id"]

while True:
    result = requests.get(
        f"{base_url}v1/tasks/{task_id}",
        headers={**common_headers, "X-ModelScope-Task-Type": "image_generation"},
    )
    result.raise_for_status()
    data = result.json()

    if data["task_status"] == "SUCCEED":
        image = Image.open(BytesIO(requests.get(data["output_images"][0]).content))
        image.save("result_image.jpg")
        break
    elif data["task_status"] == "FAILED":
        print("Image Generation Failed.")
        break

    time.sleep(5)
