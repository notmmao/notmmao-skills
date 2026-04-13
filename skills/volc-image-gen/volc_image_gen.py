#!/home/ota/.openclaw/claw_venv/bin/python
import os
import argparse
import requests
import hashlib
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("/home/ota/.openclaw/.env")
ARK_API_KEY = os.getenv("ARK_API_KEY")
ARK_API_MODEL = os.getenv("ARK_API_MODEL", "doubao-seedream-4-0-250828")
API_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
CACHE_DIR = os.path.expanduser("~/.cache/volc-image-gen/")

# 确保缓存目录存在
os.makedirs(CACHE_DIR, exist_ok=True)

def generate_image(prompt, images=None, model=ARK_API_MODEL, size="2K", watermark=True):
    if not ARK_API_KEY:
        return {"error": "未找到ARK_API_KEY，请在.env文件中配置"}
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ARK_API_KEY}"
    }
    
    payload = {
        "model": model,
        "prompt": prompt,
        "sequential_image_generation": "disabled",
        "response_format": "url",
        "size": size,
        "stream": False,
        "watermark": watermark
    }
    
    # 图生图模式
    if images:
        if len(images) == 1:
            payload["image"] = images[0]
        else:
            payload["image"] = images
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"请求失败: {str(e)}"}

def get_default_filename(prompt):
    """生成默认文件名：提示词前10个字符+哈希前缀"""
    prompt_short = prompt[:10].replace(" ", "_").replace("/", "_")
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
    return f"{prompt_short}_{prompt_hash}.png"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="火山引擎豆包图片生成工具")
    parser.add_argument("prompt", type=str, help="生成图片的提示词")
    parser.add_argument("--image", "-i", action="append", help="参考图URL（图生图模式，可传入多个）")
    parser.add_argument("--model", "-m", type=str, default=ARK_API_MODEL, help="模型名称，默认使用环境变量ARK_API_MODEL配置，未配置则为doubao-seedream-4-0-250828")
    parser.add_argument("--size", "-s", type=str, default="2K", help="图片尺寸：2K/4K等")
    parser.add_argument("--no-watermark", action="store_true", help="关闭水印")
    parser.add_argument("--save", type=str, help="保存图片到本地路径，默认保存到~/.cache/volc-image-gen/")
    
    args = parser.parse_args()
    
    result = generate_image(
        prompt=args.prompt,
        images=args.image,
        model=args.model,
        size=args.size,
        watermark=not args.no_watermark
    )
    
    if "error" in result:
        print(f"❌ 生成失败: {result['error']}")
    else:
        img_url = result["data"][0]["url"]
        img_size = result["data"][0]["size"]
        print(f"✅ 图片生成成功！")
        print(f"📐 尺寸: {img_size}")
        print(f"🔗 链接: {img_url}")
        
        # 确定保存路径
        if args.save:
            save_path = args.save
        else:
            save_path = os.path.join(CACHE_DIR, get_default_filename(args.prompt))
        
        # 保存到本地
        try:
            img_data = requests.get(img_url).content
            with open(save_path, "wb") as f:
                f.write(img_data)
            print(f"💾 已保存到: {os.path.abspath(save_path)}")
        except Exception as e:
            print(f"⚠️ 保存失败: {str(e)}")
