import requests
import json
import base64
from PIL import Image # PIL (Pillow) の Image モジュールをインポート
import io
import os

# --- 設定 ---
API_URL = "http://127.0.0.1:7861"  # Stable Diffusion Web UI のアドレスとポート
IMG2IMG_ENDPOINT = f"{API_URL}/sdapi/v1/img2img"
OUTPUT_DIR = "converted_images"  # 生成された画像を保存するフォルダ

# --- 関数 ---
# (encode_image_to_base64, save_decoded_image, convert_image_style 関数は変更なしなので省略)
def encode_image_to_base64(image_path):
    """指定されたパスの画像を読み込み、Base64エンコードする"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"エラー: 画像ファイルが見つかりません: {image_path}")
        return None
    except Exception as e:
        print(f"エラー: 画像のエンコード中に問題が発生しました: {e}")
        return None

def save_decoded_image(base64_string, output_filename):
    """Base64エンコードされた画像文字列をデコードして保存する"""
    try:
        img_data = base64.b64decode(base64_string)
        img = Image.open(io.BytesIO(img_data))
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        save_path = os.path.join(OUTPUT_DIR, output_filename)
        img.save(save_path)
        print(f"画像が {save_path} に保存されました。")
    except Exception as e:
        print(f"エラー: 画像の保存中に問題が発生しました: {e}")

def convert_image_style(init_image_base64, prompt, negative_prompt="", denoising_strength=0.75,
                        sampler_name="Euler a", steps=30, cfg_scale=7, seed=-1,
                        width=None, height=None): # width, height を受け取れるようにする
    """img2img APIを呼び出して画像スタイルを変換する"""
    payload = {
        "init_images": [init_image_base64],
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "denoising_strength": denoising_strength,
        "sampler_name": sampler_name,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "seed": seed,
        "width": width,   # 受け取ったwidthを指定
        "height": height, # 受け取ったheightを指定
    }

    # ★デバッグ用に送信するペイロードを表示させる場合は以下のコメントを外してください
    # print("--- 送信するペイロード ---")
    # print(json.dumps(payload, indent=2))
    # print("------------------------")

    print("画像変換を開始します...")
    try:
        response = requests.post(IMG2IMG_ENDPOINT, json=payload)
        response.raise_for_status()
        r = response.json()
        if 'images' in r and r['images']:
            return r['images'][0]
        else:
            print("エラー: APIからのレスポンスに画像データが含まれていません。")
            print("APIレスポンス:", r)
            return None
    except requests.exceptions.RequestException as e:
        print(f"エラー: APIへの接続またはリクエスト中に問題が発生しました: {e}")
        if response is not None: # responseオブジェクトが存在する場合のみアクセス
            print(f"ステータスコード: {response.status_code}")
            try:
                print(f"エラー詳細: {response.json()}")
            except json.JSONDecodeError:
                print(f"エラー詳細 (非JSON): {response.text}")
        return None
    except KeyError as e:
        print(f"エラー: APIレスポンスの解析中に予期しない形式でした (KeyError: {e})。")
        print("APIレスポンス:", response.text if response is not None else "レスポンスなし")
        return None
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        return None

# --- メイン処理 ---
if __name__ == "__main__":
    print("画像スタイル変換スクリプト")
    print("-" * 30)

    while True:
        image_path = input("変換したい写真のフルパスを入力してください: ").strip()
        if os.path.exists(image_path):
            break
        else:
            print("ファイルが見つかりません。正しいパスを入力してください。")

    init_image_base64 = encode_image_to_base64(image_path)
    if not init_image_base64:
        exit()

    # ★★★ 修正箇所: 元の画像のサイズを取得 ★★★
    try:
        with Image.open(image_path) as img: # PillowのImageを使って画像を開く
            original_width, original_height = img.size
        print(f"元画像のサイズ: Width={original_width}, Height={original_height}")
    except Exception as e:
        print(f"エラー: 元画像のサイズ取得に失敗しました: {e}")
        # サイズ取得に失敗した場合、デフォルト値を設定するか、ユーザーに入力を促すなどの処理も考えられる
        # ここでは処理を中断する例
        print("処理を中断します。")
        exit()
    # ★★★ 修正箇所ここまで ★★★

    print("\n変換するスタイルを選択してください:")
    print("1: 水彩画風")
    print("2: ドラゴンボール風")

    style_choice = ""
    while style_choice not in ["1", "2"]:
        style_choice = input("選択肢の番号を入力してください (1 または 2): ").strip()

    prompt = ""
    negative_prompt = "worst quality, low quality, normal quality, blurry, ugly, deformed, text, watermark, signature"
    denoising_strength = 0.75
    output_filename_prefix = os.path.splitext(os.path.basename(image_path))[0]

    if style_choice == "1":
        print("水彩画風を選択しました。")
        prompt = "masterpiece, best quality, beautiful watercolor painting, soft lighting, vibrant colors"
        user_subject_prompt = input("プロンプトに追加する被写体の説明を入力してください (例: 'cat', 'mountain landscape'): ").strip()
        prompt = f"{user_subject_prompt}, {prompt}"
        denoising_strength = 0.7
        output_filename = f"{output_filename_prefix}_watercolor.png"

    elif style_choice == "2":
        print("ドラゴンボール風を選択しました。")
        lora_name = input("使用するドラゴンボール風LoRAのファイル名 (例: dbz_style_v1.safetensors) を入力してください: ").strip()
        lora_trigger_word = input("そのLoRAのトリガーワード (例: dbz style) を入力してください: ").strip()
        lora_weight = 0.8
        lora_prompt_name = os.path.splitext(lora_name)[0]
        prompt = f"masterpiece, best quality, {lora_trigger_word}, <lora:{lora_prompt_name}:{lora_weight}>, dynamic action pose, vibrant colors, bold outlines"
        user_subject_prompt = input("プロンプトに追加するキャラクターやシーンの説明を入力してください (例: 'a saiyan warrior', 'epic battle'): ").strip()
        prompt = f"{user_subject_prompt}, {prompt}"
        denoising_strength = 0.70
        output_filename = f"{output_filename_prefix}_dragonball.png"

    try:
        custom_denoising = input(f"Denoising Strength (デフォルト: {denoising_strength}, 0.1-1.0): ").strip()
        if custom_denoising:
            denoising_strength = float(custom_denoising)
    except ValueError:
        print("Denoising Strengthは数値で入力してください。デフォルト値を使用します。")

    # 画像変換実行 (widthとheightを渡す)
    converted_image_base64 = convert_image_style(
        init_image_base64,
        prompt,
        negative_prompt=negative_prompt,
        denoising_strength=denoising_strength,
        width=original_width,   # ★★★ 修正箇所: 元の画像の幅を渡す ★★★
        height=original_height  # ★★★ 修正箇所: 元の高さを渡す ★★★
    )

    if converted_image_base64:
        save_decoded_image(converted_image_base64, output_filename)

    print("-" * 30)
    print("スクリプト終了")