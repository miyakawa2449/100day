from stability_sdk import client
# from stability_sdk.interfaces.gooseai.generation.generation_pb2 import Sampler # Samplerをインポート
from PIL import Image, ImageOps # ImageOps をインポート
from dotenv import load_dotenv
import os

# .envファイルを読み込む
load_dotenv()

# Stability AI APIキーを設定
api_key = os.getenv("STABILITY_API_KEY")
if not api_key:
    raise ValueError("APIキーが設定されていません。'.env' ファイルを確認してください。")

# Stability AI クライアントを初期化
stability_api = client.StabilityInference(
    key=api_key,
    verbose=True,
    engine="stable-diffusion-xl-1024-v1-0"  # 例: SDXL 1.0エンジン (最新の推奨エンジンを確認してください)
)

# --- JPEG画像を処理 ---
try:
    jpg_image_path = "your_photo.jpg"
    # モデルが推奨するサイズ、または試したいサイズ (SDXLなら1024x1024, 768x768, 512x512など)
    target_size = (1024, 1024)

    with Image.open(jpg_image_path) as img:
        # アスペクト比を維持してリサイズ
        img.thumbnail(target_size, Image.Resampling.LANCZOS)

        # 正方形にパディング (背景色は白や透明など。モデルの入力形式に合わせる)
        # まずRGBAに変換してアルファチャンネルを扱えるようにする
        img_rgba = img.convert("RGBA")
        
        # 新しい正方形の画像を作成 (背景は白のRGB画像としてAPIに渡す場合)
        # PillowのImage.newでは 'RGB'モードの場合、アルファは考慮されないので、
        # 背景色をRGBで指定し、その上にRGBA画像をpasteする際にアルファマスクを使う
        padded_img = Image.new('RGB', target_size, (255, 255, 255)) # 白背景
        
        # 元の画像を中央に配置
        paste_position = (
            (target_size[0] - img_rgba.width) // 2,
            (target_size[1] - img_rgba.height) // 2
        )
        # RGBA画像をRGB背景にpasteする際は、アルファチャンネルをマスクとして利用
        padded_img.paste(img_rgba, paste_position, img_rgba if img_rgba.mode == 'RGBA' else None)
        
        # APIに渡すのはPillowのImageオブジェクト (RGB形式)
        init_image_pil = padded_img

    # Stability AI API に画像を送信して変換
    response = stability_api.generate(
        prompt=(
            "Create a safe and professional anime-style artwork of a person. "
            "Focus on the face and upper body, with expressive anime-style eyes and clean line art. "
            "The background should be a simple, clean anime-style room with soft lighting. "
            "Use vibrant colors and smooth shading to create a professional anime art style. "
            "Ensure the content is appropriate and adheres to safety guidelines."
        ),
        init_image=init_image_pil,
        start_schedule=0.5,  # プロンプトと元画像のバランスを調整
        cfg_scale=8.0,       # クリエイティブな自由度
        steps=30             # ステップ数
    )

    # 生成された画像を保存
    output_idx = 0
    for resp in response:
        for artifact in resp.artifacts:
            # artifact.finish_reason の比較はSDKのバージョンによって異なる可能性あり
            # 正しい比較方法はSDKのドキュメントやサンプルを参照してください。
            # 一般的には artifact.type == generation.ARTIFACT_IMAGE で画像かどうかを判定し、
            # artifact.finish_reason で成功/失敗を確認します。
            # 例: if artifact.type == generation.ARTIFACT_IMAGE and artifact.finish_reason == generation.FILTER: (検閲された場合)
            if artifact.finish_reason == 1: # 1 が SUCCESS を意味する場合 (要確認) または他の成功判定
                output_path = f"output_anime_{output_idx}.png"
                with open(output_path, "wb") as f:
                    f.write(artifact.binary)
                print(f"生成された画像を保存しました: {output_path}")
                output_idx += 1
            else:
                # 失敗理由のより詳細な情報があるか確認
                print(f"アーティファクト生成完了せず (または失敗): reason={artifact.finish_reason}, type={artifact.type}")
                if artifact.text: # エラーメッセージが含まれている場合
                    print(f"  エラーテキスト: {artifact.text}")


except Exception as e:
    print(f"エラーが発生しました: {e}")