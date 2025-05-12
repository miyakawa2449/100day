import requests
import os
import io
from PIL import Image
from dotenv import load_dotenv
import openai # OpenAIライブラリ (v1.0.0以降)
import base64

# .envファイルから環境変数を読み込む
load_dotenv()

# APIキーの読み込み
STABILITY_API_KEY = os.environ.get("STABILITY_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# APIキー存在チェック
if not STABILITY_API_KEY:
    print("エラー: 環境変数 'STABILITY_API_KEY' が設定されていません。")
    exit()
if not OPENAI_API_KEY:
    print("エラー: 環境変数 'OPENAI_API_KEY' が設定されていません。")
    exit()

# OpenAI APIクライアントの初期化
try:
    client_openai = openai.OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    print(f"OpenAIクライアントの初期化に失敗しました: {e}")
    exit()

# Stability AI API設定
STABILITY_ENGINE_ID = "stable-diffusion-v1-6" # 最新のモデルIDは適宜確認してください
STABILITY_API_HOST = os.getenv('API_HOST', 'https://api.stability.ai')
STABILITY_API_URL = f"{STABILITY_API_HOST}/v1/generation/{STABILITY_ENGINE_ID}/text-to-image"

stability_headers = {
    "Authorization": f"Bearer {STABILITY_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Stability AI 用のペイロードのテンプレート (プロンプトは後で設定)
stability_payload_template = {
    "negative_prompts": [
        {
            "text": "ugly, blurry, bad anatomy, extra limbs, watermark, text, deformed, poorly drawn, tiling, out of frame, disfigured"
        }
    ],
    "cfg_scale": 7,
    "height": 512,
    "width": 512,
    "samples": 1,
    "steps": 30,
    # "style_preset": "photographic", # 必要に応じてスタイルプリセットを指定
}

def translate_to_english_with_openai(japanese_text):
    """日本語テキストをOpenAI APIを使って英語に翻訳する関数"""
    print(f"翻訳元の日本語: {japanese_text}")
    try:
        response = client_openai.chat.completions.create(
            model="gpt-4",  # または "gpt-3.5-turbo"または"gpt-4" など、利用可能なモデルを指定
            messages=[
                {"role": "system", "content": "You are a helpful assistant that translates Japanese to English. Provide a translation suitable for an image generation prompt, focusing on descriptive and evocative language."},
                {"role": "user", "content": japanese_text}
            ],
            temperature=0.3,  # 翻訳なので、あまり創造的すぎないように低めに設定
            max_tokens=200    # 翻訳結果の最大長
        )
        translated_text = response.choices[0].message.content.strip()
        print(f"翻訳後の英語: {translated_text}")
        return translated_text
    except openai.APIConnectionError as e:
        print(f"OpenAI APIサーバーへの接続に失敗しました: {e}")
    except openai.RateLimitError as e:
        print(f"OpenAI APIのレート制限に達しました: {e}")
    except openai.APIStatusError as e:
        print(f"OpenAI APIがエラーステータスを返しました: {e.status_code}, Response: {e.response}")
    except Exception as e:
        print(f"OpenAI APIでの翻訳中に予期せぬエラーが発生しました: {e}")
    return None

def generate_image_with_stabilityai(english_prompt):
    """英語プロンプトを使ってStability AI APIで画像を生成する関数"""
    if not english_prompt:
        print("エラー: 英語プロンプトが空です。画像生成を中止します。")
        return

    # ペイロードに翻訳されたプロンプトを設定
    current_payload = stability_payload_template.copy()
    current_payload["text_prompts"] = [{"text": english_prompt}]

    print(f"Stability AIに送信するプロンプト: {english_prompt}")

    try:
        response = requests.post(
            STABILITY_API_URL,
            headers=stability_headers,
            json=current_payload
        )
        response.raise_for_status() # HTTPエラーがあれば例外を発生

        data = response.json()

        if not data.get("artifacts"):
            print("エラー: APIから画像データ(artifacts)が返されませんでした。")
            print(f"レスポンス: {data}")
            return

        for i, image_data in enumerate(data["artifacts"]):
            if image_data.get("base64"):
                try:
                    image_bytes = io.BytesIO(base64.b64decode(image_data["base64"]))
                    img = Image.open(image_bytes)
                    file_name = f"generated_image_jp_en_{i+1}.png" # ファイル名を変更
                    img.save(file_name)
                    print(f"画像を {file_name} として保存しました。")
                except Exception as e_save:
                    print(f"画像のデコードまたは保存中にエラーが発生しました: {e_save}")
            else:
                print(f"アーティファクト {i+1} にbase64画像データが含まれていません。")

    except requests.exceptions.RequestException as e_req:
        print(f"Stability AI APIリクエスト中にエラーが発生しました: {e_req}")
        if hasattr(e_req, 'response') and e_req.response is not None:
            try:
                print(f"エラー詳細: {e_req.response.json()}")
            except ValueError:
                print(f"エラー詳細 (テキスト): {e_req.response.text}")
    except Exception as e_gen:
        print(f"画像生成処理中に予期せぬエラーが発生しました: {e_gen}")

if __name__ == "__main__":
    japanese_user_prompt = input("生成したい画像のイメージを日本語で入力してください: ")

    if japanese_user_prompt:
        english_prompt = translate_to_english_with_openai(japanese_user_prompt)
        if english_prompt:
            generate_image_with_stabilityai(english_prompt)
        else:
            print("英語への翻訳に失敗したため、画像生成は行いませんでした。")
    else:
        print("プロンプトが入力されませんでした。")