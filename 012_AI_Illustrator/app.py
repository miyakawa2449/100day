from openai import OpenAI
import requests
from PIL import Image, ImageOps
from io import BytesIO
from dotenv import load_dotenv
import os

# .envファイルを読み込む
load_dotenv()

# OpenAI APIキーを設定
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("APIキーが設定されていません。'.env' ファイルを確認してください。")

client = OpenAI(api_key=api_key)

# --- Option 2: 画像を編集してイラスト風にする (プロンプトでスタイルを指定) ---
try:
    # JPGファイルを正方形にパディングしてPNGに変換
    jpg_image_path = "your_photo.jpg"  # 元のJPGファイルのパス
    png_image_path = "your_photo.png"  # 変換後のPNGファイルのパス

    with Image.open(jpg_image_path) as img:
        # 正方形にパディング
        img = ImageOps.pad(img, (1024, 1024), color=(255, 255, 255))  # 白背景でパディング
        img = img.convert("RGBA")  # RGBA形式に変換
        img.save(png_image_path, "PNG")  # PNG形式で保存

    # PNGファイルをAPIに送信
    response = client.images.edit(
        image=open(png_image_path, "rb"),  # 変換後のPNGファイルを使用
        prompt=( # プロンプトを少し変えてみます
            "Completely transform this entire image into a vibrant and detailed anime-style artwork. "
            "Redraw it in a professional anime art style, featuring dynamic lines, expressive characters (if any), "
            "and a rich, painterly texture with artistic lighting. Do not retain photographic elements."
        ),
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url
    print(f"生成された画像のURL: {image_url}")

    # 生成された画像をダウンロードして表示 (オプション)
    img_data = requests.get(image_url).content
    img = Image.open(BytesIO(img_data))
    img.show()

except Exception as e:
    print(f"エラーが発生しました: {e}")