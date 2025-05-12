import requests
import os
import io
from PIL import Image
from dotenv import load_dotenv # python-dotenvライブラリからload_dotenvをインポート

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からAPIキーを読み込む
STABILITY_API_KEY = os.environ.get("STABILITY_API_KEY")

# APIのエンドポイント
ENGINE_ID = "stable-diffusion-v1-6" # 利用可能なモデルIDを指定 (例: stable-diffusion-xl-1024-v1-0 など)
# 最新のモデルIDはStability AIのドキュメントで確認してください。
API_HOST = os.getenv('API_HOST', 'https://api.stability.ai')
API_URL = f"{API_HOST}/v1/generation/{ENGINE_ID}/text-to-image"

# リクエストヘッダー
headers = {
    "Authorization": f"Bearer {STABILITY_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# リクエストボディ (生成したい画像の説明やパラメータ)
payload = {
    "text_prompts": [   # プロンプトを追加
        {
            "text": ""
        }
    ],
        "negative_prompts": [ # ネガティブプロンプトを追加
        {
            "text": "ugly, blurry, bad anatomy, extra limbs, watermark, text"
        }
    ],
    "cfg_scale": 7,
    "height": 512,
    "width": 512,
    "samples": 1,
    "steps": 30,
    # "style_preset": "fantasy-art",
    # "seed": 0
}

def generate_image():
    """Stability AI APIにリクエストを送信して画像を生成し、保存する関数"""
    if not STABILITY_API_KEY:
        print("エラー: APIキーが読み込めませんでした。")
        print(".envファイルに 'STABILITY_API_KEY=あなたのAPIキー' の形式でキーが正しく設定されているか、")
        print("または環境変数として直接設定されているか確認してください。")
        return

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("artifacts"):
            print("エラー: APIから画像データが返されませんでした。")
            print(f"レスポンス: {data}")
            return

        for i, image_data in enumerate(data["artifacts"]):
            if image_data.get("base64"):
                try:
                    # Stability AIのAPIはbase64エンコードされた文字列を返すので、bytes.fromhexではなく
                    # base64.b64decodeを使用するのが一般的です。
                    # ただし、以前のコードで fromhex を使っていたため、APIの仕様を確認してください。
                    # もしAPIが16進数エンコードされた文字列を返しているなら fromhex のままで問題ありません。
                    # 一般的なbase64なら以下のようにします。
                    import base64
                    image_bytes = io.BytesIO(base64.b64decode(image_data["base64"]))
                    # image_bytes = io.BytesIO(bytes.fromhex(image_data["base64"])) # もし16進数エンコードならこちら
                    
                    img = Image.open(image_bytes)
                    file_name = f"generated_image_dotenv_{i+1}.png"
                    img.save(file_name)
                    print(f"画像を {file_name} として保存しました。")
                except Exception as e:
                    print(f"画像のデコードまたは保存中にエラーが発生しました: {e}")
            else:
                print(f"アーティファクト {i+1} にbase64画像データが含まれていません。")

    except requests.exceptions.RequestException as e:
        print(f"APIリクエスト中にエラーが発生しました: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                print(f"エラー詳細: {e.response.json()}")
            except ValueError:
                print(f"エラー詳細 (テキスト): {e.response.text}")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")

if __name__ == "__main__":
    user_prompt = input("生成したい画像のプロンプトを入力してください: ")
    if user_prompt:
        payload["text_prompts"][0]["text"] = user_prompt # payloadのプロンプトを更新
        generate_image()
    else:
        print("プロンプトが入力されませんでした。")