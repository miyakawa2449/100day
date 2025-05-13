import requests
import json
import base64
from PIL import Image
import io

# Stable Diffusion Web UIのURL (APIが有効になっていること)
url = "http://127.0.0.1:7861" # ポート番号はご自身の環境に合わせてください

# txt2imgのエンドポイント
txt2img_url = f"{url}/sdapi/v1/txt2img"

# 送信するデータ (プロンプトなど)
payload = {
    "prompt": "a cute cat astronaut on the moon, hd, detailed",
    "steps": 20,
    "width": 512,
    "height": 512,
    "cfg_scale": 7,
    "sampler_name": "Euler a", # Web UIで利用可能なサンプラー名
    # "sd_model_checkpoint": "your_favorite_model.safetensors", # 特定のモデルを指定する場合
    # "negative_prompt": "ugly, blurry",
    # その他、Web UIで設定できる多くのパラメータが指定可能です
}

try:
    # APIにPOSTリクエストを送信
    response = requests.post(txt2img_url, json=payload)
    response.raise_for_status() # エラーがあれば例外を発生させる

    r = response.json()

    # レスポンスに含まれる画像データをデコードして保存
    for i, img_str in enumerate(r['images']):
        img_data = base64.b64decode(img_str)
        img = Image.open(io.BytesIO(img_data))
        img.save(f"output_image_{i}.png")
        print(f"Image saved as output_image_{i}.png")

except requests.exceptions.RequestException as e:
    print(f"Error connecting to API: {e}")
    if response:
        print(f"Response content: {response.text}") # エラーレスポンスの内容を表示

except KeyError as e:
    print(f"Error parsing response JSON (KeyError): {e}")
    print(f"Response content: {response.text}")