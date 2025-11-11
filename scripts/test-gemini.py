import os
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
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

print(os.getenv('GEMINI_API_KEY'))


def generate_image():
    client = genai.Client()
    prompt = (
        "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"
    )

    response = client.models.generate_content(
        # model="gemini-2.5-flash-image",
        model="gemini-2.5-flash-preview-image",
        contents=[prompt],
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            image.save("generated_image.png")
            
def generate_image_with_imagen():
    from google import genai
    from google.genai import types
    from PIL import Image
    from io import BytesIO

    client = genai.Client()

    response = client.models.generate_images(
        model='imagen-4.0-generate-001',
        prompt='Robot holding a red skateboard',
        config=types.GenerateImagesConfig(
            number_of_images= 4,
        )
    )
    for generated_image in response.generated_images:
        generated_image.image.show()
        
# 免费用户使用
generate_image()
# 只能付费用户可以使用
# generate_image_with_imagen()