import requests
import time
import json
import os
from PIL import Image
from io import BytesIO

def generate_image_modelscope(api_key, base_url, prompt, width, height, model="Qwen/Qwen-Image"):
    """
    使用 ModelScope API 生成图片
    
    Args:
        api_key (str): ModelScope API Key
        base_url (str): API Base URL (e.g., https://api-inference.modelscope.cn/)
        prompt (str): 提示词
        width (int): 图片宽度
        height (int): 图片高度
        model (str): 模型名称
    
    Returns:
        str: 生成图片的URL，如果失败则返回None
    """
    print(f"Generating image with ModelScope...")
    print(f"API URL: {base_url}")
    print(f"Model: {model}")
    print(f"Size: {width}x{height}")
    print(f"Prompt: {prompt[:50]}...")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-ModelScope-Async-Mode": "true"
    }

    payload = {
        "model": model,
        "prompt": prompt,
        "width": width,
        "height": height
    }

    # 1. 提交任务 (Submit Task)
    submit_url = f"{base_url.rstrip('/')}/v1/images/generations"
    try:
        response = requests.post(
            submit_url,
            headers=headers,
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
            timeout=30
        )
        response.raise_for_status()
        task_data = response.json()
        task_id = task_data.get("task_id")
        print(f"Task submitted successfully. Task ID: {task_id}")
    except Exception as e:
        print(f"Failed to submit task: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")
        return None

    # 2. 轮询状态 (Poll Status)
    task_url = f"{base_url.rstrip('/')}/v1/tasks/{task_id}"
    start_time = time.time()
    timeout = 300 # 5 minutes timeout

    while True:
        if time.time() - start_time > timeout:
            print("Timeout waiting for image generation.")
            return None

        try:
            # 查询状态需要特定的 Header
            poll_headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-ModelScope-Task-Type": "image_generation"
            }
            
            response = requests.get(task_url, headers=poll_headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            status = data.get("task_status")
            print(f"Task Status: {status}")

            if status == "SUCCEED":
                if "output_images" in data and len(data["output_images"]) > 0:
                    image_url = data["output_images"][0]
                    print(f"Image generated successfully: {image_url}")
                    return image_url
                else:
                    print("Task succeeded but no image URL found.")
                    return None
            elif status == "FAILED":
                print(f"Task failed: {data.get('message')}")
                return None
            
            # 等待后重试
            time.sleep(5)
            
        except Exception as e:
            print(f"Error polling task status: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # 示例配置
    # 请确保在环境变量中设置 MODELSCOPE_API_KEY 或直接在此处替换
    API_KEY = os.getenv("MODELSCOPE_API_KEY", "ms-f1998dcc-5662-44a6-b0f1-e4b3a0a036ed")
    BASE_URL = "https://api-inference.modelscope.cn/"
    
    # 示例参数
    PROMPT = "A futuristic city with flying cars, cyberpunk style, neon lights, 8k resolution, cinematic lighting"
    WIDTH = 1280
    HEIGHT = 720
    
    if API_KEY == "your_api_key_here":
        print("Please set your ModelScope API Key.")
    else:
        image_url = generate_image_modelscope(API_KEY, BASE_URL, PROMPT, WIDTH, HEIGHT)
        
        if image_url:
            print(f"Downloading image...")
            try:
                img_response = requests.get(image_url)
                img = Image.open(BytesIO(img_response.content))
                output_file = "modelscope_result.png"
                img.save(output_file)
                print(f"Image saved to {output_file}")
            except Exception as e:
                print(f"Failed to download/save image: {e}")
